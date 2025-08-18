import discord
from discord import app_commands
from config import settings

# Inisialisasi client dan command tree
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Dictionary untuk menyimpan data antar modul jika diperlukan
client.active_recordings = {}