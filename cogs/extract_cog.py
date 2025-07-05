import discord
from discord.ext import commands
import logging
import asyncio
from PIL import Image
from io import BytesIO
import numpy as np
import traceback

from .extract_helpers import (
    prevent_discord_formatting,
    highlight_zero_values,
    validate_stat,
    clean_for_match,
    build_single_embed,
    build_monitor_embed,
)
from database import (
    get_registered_users,
    insert_player_data,
    find_best_match,
    get_registered_user_by_discord_id,
    get_clan_name_by_discord_server_id,
    get_server_listing_by_id
)
from config import (
    ALLOWED_EXTENSIONS, MATCH_SCORE_THRESHOLD
)
from ocr_processing import process_for_ocr, clean_ocr_result
from boundary_drawing import define_regions

logger = logging.getLogger(__name__)

class ExtractCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def submit_stats_button_flow(self, interaction: discord.Interaction):
        """Main entrypoint after pressing the SUBMIT STATS button."""
        if not interaction.guild_id:
            await interaction.response.send_message("This command cannot be used in DMs.", ephemeral=True)
            return

        server_data = await get_server_listing_by_id(interaction.guild_id)
        if not server_data:
            await interaction.response.send_message(
                "Server is not configured. Contact an admin.",
                ephemeral=True
            )
            return
        gpt_stat_access_role_id = server_data.get("gpt_stat_access_role_id")
        monitor_channel_id = server_data.get("monitor_channel_id")
        if not gpt_stat_access_role_id or not monitor_channel_id:
            await interaction.response.send_message(
                "Server is missing required IDs (role or channel) in the database. Contact an admin.",
                ephemeral=True
            )
            return

        role_ids = [r.id for r in interaction.user.roles] if hasattr(interaction.user, "roles") else []
        if gpt_stat_access_role_id not in role_ids:
            await interaction.response.send_message(
                "You do not have permission to use this feature (missing GPT STAT ACCESS role).",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Please upload your mission screenshot image **as a reply in this channel** within 60 seconds.",
            ephemeral=True
        )

        def check(msg):
            return (
                msg.author == interaction.user
                and msg.channel == interaction.channel
                and msg.attachments
                and any(msg.attachments[0].filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60.0)
            image = msg.attachments[0]
            img_bytes = await image.read()
            img_pil = Image.open(BytesIO(img_bytes))
            img_cv = np.array(img_pil)
            regions = define_regions(img_cv.shape)

            await interaction.followup.send(
                content="Here is the submitted image for stats extraction:",
                file=discord.File(BytesIO(img_bytes), filename=image.filename),
                ephemeral=True
            )

            players_data = await asyncio.to_thread(process_for_ocr, img_cv, regions)
            players_data = [
                p for p in players_data
                if p.get('player_name') and str(p.get('player_name')).strip() not in ["", "0", ".", "a"]
            ]
            if len(players_data) < 2:
                await interaction.followup.send("At least 2 players with valid names must be present in the image.", ephemeral=True)
                return
            registered_users = await get_registered_users()
            for player in players_data:
                ocr_name = player.get('player_name')
                if ocr_name:
                    cleaned_ocr = clean_ocr_result(ocr_name, 'Name')
                    db_names = [u["player_name"] for u in registered_users]
                    ocr_name_clean = clean_for_match(cleaned_ocr)
                    db_names_clean = [clean_for_match(n) for n in db_names]
                    best_match_cleaned, match_score = find_best_match(
                        ocr_name_clean,
                        db_names_clean,
                        threshold=MATCH_SCORE_THRESHOLD
                    )
                    if best_match_cleaned and match_score is not None and match_score >= MATCH_SCORE_THRESHOLD:
                        idx = db_names_clean.index(best_match_cleaned)
                        matched_user = registered_users[idx]
                        player['player_name'] = matched_user["player_name"]
                        player['discord_id'] = matched_user.get("discord_id")
                        player['discord_server_id'] = matched_user.get("discord_server_id")
                        if matched_user.get("discord_server_id"):
                            clan_name = await get_clan_name_by_discord_server_id(matched_user["discord_server_id"])
                            player['clan_name'] = clan_name
                        else:
                            player['clan_name'] = "N/A"
                    else:
                        player['player_name'] = None
                        player['discord_id'] = None
                        player['discord_server_id'] = None
                        player['clan_name'] = "N/A"
                else:
                    player['player_name'] = None
                    player['discord_id'] = None
                    player['discord_server_id'] = None
                    player['clan_name'] = "N/A"
            players_data = [p for p in players_data if p.get('player_name')]
            if len(players_data) < 2:
                await interaction.followup.send(
                    "At least 2 registered players must be detected in the image. "
                    "All reported players must be registered in the database.",
                    ephemeral=True
                )
                return
            submitter_user = await get_registered_user_by_discord_id(interaction.user.id)
            submitter_player_name = submitter_user.get('player_name', 'Unknown') if submitter_user else 'Unknown'

            single_embed = build_single_embed(players_data, submitter_player_name)
            shared_data = SharedData(
                players_data,
                submitter_player_name,
                registered_users,
                monitor_channel_id,
                screenshot_bytes=img_bytes,
                screenshot_filename=image.filename
            )
            view = ConfirmationView(shared_data, self.bot)
            shared_data.view = view
            message = await interaction.followup.send(
                content="**Extracted Data:** Please confirm the extracted data.",
                embeds=[single_embed],
                view=view,
                ephemeral=True
            )
            shared_data.message = message

        except asyncio.TimeoutError:
            await interaction.followup.send("Timed out waiting for an image. Please try again.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            logger.error(f"Traceback: {traceback_str}")
            await interaction.followup.send("An error occurred while processing the image.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ExtractCog(bot))
