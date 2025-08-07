# utils.py

import logging
import discord
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

async def send_ephemeral(interaction, content):
    """Send an ephemeral message to the user."""
    try:
        await interaction.followup.send(content=content, ephemeral=True)
    except Exception as e:
        logger.error(f"Error sending ephemeral message: {e}")

async def log_to_monitor_channel(bot, content: str, level: int = logging.INFO, guild: Optional[discord.Guild] = None):
    """
    Attempt to log a message to the configured monitor channel(s).
    If a guild is provided, only send to that guild's monitor channel; otherwise broadcast to all known ones.
    Falls back to standard logging on failure.
    """
    try:
        if not hasattr(bot, 'mongo_db') or bot.mongo_db is None:
            logger.log(level, content)
            return
        server_listing = bot.mongo_db['Server_Listing']
        targets = []
        if guild:
            doc = await server_listing.find_one({"discord_server_id": guild.id})
            if doc and doc.get("monitor_channel_id"):
                targets.append((guild, doc["monitor_channel_id"]))
        else:
            async for doc in server_listing.find({}, {"discord_server_id": 1, "monitor_channel_id": 1}):
                g = bot.get_guild(doc.get("discord_server_id"))
                if g and doc.get("monitor_channel_id"):
                    targets.append((g, doc["monitor_channel_id"]))
        if not targets:
            logger.log(level, content)
            return
        for g, channel_id in targets:
            channel = g.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(content)
                except Exception as send_err:
                    logger.error(f"Failed to send to monitor channel {channel_id} in guild {g.id}: {send_err}")
            else:
                logger.warning(f"Monitor channel {channel_id} not found in guild {g.id}")
    except Exception as e:
        logger.error(f"log_to_monitor_channel failed: {e}")
