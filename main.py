import os
import logging
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Load all your cogs on startup
initial_extensions = [
    'cogs.cleanup_cog',
    'cogs.dm_response',
    'cogs.guild_management_cog',
    'cogs.leaderboard_cog',
    'cogs.menu_view',
    'cogs.register_modal',
    'cogs.sos_cog',
    'cogs.sos_view',
    'cogs.extract_cog',
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

async def setup():
    # Load cogs/extensions
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            logging.info(f"Loaded extension {ext}")
        except Exception as e:
            logging.error(f'Failed to load extension {ext}: {e}')

if __name__ == '__main__':
    import asyncio

    # Load environment variables
    token = os.environ.get('DISCORD_TOKEN')
    mongo_uri = os.environ.get('MONGODB_URI')
    db_name = 'GPTStudios'

    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is not set!")
    if not mongo_uri:
        raise ValueError("MONGODB_URI environment variable is not set!")

    # Attach MongoDB client to the bot before loading cogs
    mongo_client = AsyncIOMotorClient(mongo_uri)
    bot.mongo_db = mongo_client[db_name]

    # Run setup and start the bot
    async def runner():
        await setup()
        await bot.start(token)

    asyncio.run(runner())
