# File: bot/commands.py

import discord
import asyncio
from discord import app_commands
from bot.client import tree
from modules import forwarder, recorder
from config import settings

@tree.command(name="live", description="Memicu perekaman & notifikasi untuk user TikTok live.")
@app_commands.describe(username="Username TikTok yang ingin diproses")
async def live_command(interaction: discord.Interaction, username: str):
    await interaction.response.send_message(f"✅ Permintaan untuk **{username}** diterima...", ephemeral=True)
    live_url = f"https://www.tiktok.com/@{username}/live"
    
    await forwarder.forward_notification(interaction.client, username, live_url)
    if settings.RECORDER_ENABLED:
        process = recorder.start_new_recording(username)
        if process:
            await interaction.followup.send(f"✅ Perekaman untuk **{username}** telah dimulai.", ephemeral=True)
        else:
            await interaction.followup.send(f"⚠️ Perekaman untuk **{username}** sudah aktif.", ephemeral=True)

@tree.command(name="stop", description="Menghentikan perekaman untuk seorang user dengan benar.")
@app_commands.describe(username="Username TikTok yang perekamannya ingin dihentikan.")
async def stop_command(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True) # Beri waktu untuk proses
    
    process_to_stop = recorder.stop_a_recording(username)
    
    if process_to_stop:
        # Tunggu sebentar untuk memberi kesempatan proses berhenti sendiri
        await asyncio.sleep(8) # Beri waktu 8 detik
        
        if process_to_stop.is_alive():
            process_to_stop.terminate() # Fallback jika tidak berhenti
            await interaction.followup.send(f"⚠️ Perekaman untuk **{username}** tidak merespons, dihentikan secara paksa.", ephemeral=True)
        else:
            del recorder.active_recordings[username] # Hapus dari daftar jika sudah berhenti
            await interaction.followup.send(f"✅ Perekaman untuk **{username}** telah dihentikan & video sedang diproses.", ephemeral=True)
    else:
        await interaction.followup.send(f"ℹ️ Tidak ada perekaman aktif untuk **{username}**.", ephemeral=True)