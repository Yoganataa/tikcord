# File: bot/commands.py

import discord
from discord import app_commands
from bot.client import tree
from modules import forwarder, recorder
from config import settings

@tree.command(name="live", description="Memicu perekaman & notifikasi untuk user TikTok live.")
@app_commands.describe(username="Username TikTok yang ingin diproses (contoh: arrelleeee)")
async def live_command(interaction: discord.Interaction, username: str):
    await interaction.response.send_message(f"✅ Permintaan untuk **{username}** diterima...", ephemeral=True)
    live_url = f"https://www.tiktok.com/@{username}/live"
    
    # Memanggil modul forwarder dan recorder
    await forwarder.forward_notification(interaction.client, username, live_url)
    if settings.RECORDER_ENABLED:
        process = recorder.start_new_recording(username)
        if process:
            await interaction.followup.send(f"✅ Perekaman untuk **{username}** telah dimulai.", ephemeral=True)
        else:
            await interaction.followup.send(f"⚠️ Perekaman untuk **{username}** sudah aktif.", ephemeral=True)

@tree.command(name="stop", description="Menghentikan proses perekaman untuk seorang user.")
@app_commands.describe(username="Username TikTok yang perekamannya ingin dihentikan.")
async def stop_command(interaction: discord.Interaction, username: str):
    if recorder.stop_a_recording(username):
        await interaction.response.send_message(f"✅ Perekaman untuk **{username}** telah dihentikan.", ephemeral=True)
    else:
        await interaction.response.send_message(f"ℹ️ Tidak ada perekaman aktif untuk **{username}**.", ephemeral=True)