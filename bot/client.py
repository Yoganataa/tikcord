import discord
from discord import app_commands
from config import settings

# Initialize client and command tree
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Note: Removed active_recordings from client
# State management is now centralized in modules/recorder.py