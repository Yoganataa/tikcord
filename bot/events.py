# File: bot/events.py

import re
import discord
from bot.client import client, tree # Impor 'tree' dari client
from modules import forwarder, recorder
from config import settings

TIKTOK_URL_PATTERN = re.compile(r'https?://(?:www\.)?tiktok\.com/@([^/]+)/(?:live|video|photo)/?(\d+)?')

@client.event
async def on_ready():
    # --- BLOK KODE BARU UNTUK SINKRONISASI COMMAND ---
    # Mendaftarkan semua command ke Discord setelah bot siap.
    if settings.GUILD_ID:
        guild = discord.Object(id=settings.GUILD_ID)
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        print(f"Slash commands disinkronkan ke server ID: {settings.GUILD_ID}")
    else:
        await tree.sync()
        print("Slash commands disinkronkan secara global.")
    # -------------------------------------------------

    print('---')
    print(f'Bot {client.user} telah berhasil online! ✨')
    print(f'Memantau {len(settings.MONITORED_CHANNELS)} channel.')
    print('---')

@client.event
async def on_message(message):
    """Menangani notifikasi otomatis dari bot lain."""
    if (message.author == client.user or
        message.channel.id not in settings.MONITORED_CHANNELS or
        message.author.id != settings.SOURCE_BOT_ID):
        return

    print(f"-> Notifikasi relevan terdeteksi di channel: #{message.channel.name}")

    # Ekstrak URL dari tombol atau konten
    raw_url = None
    if message.components:
        for row in message.components:
            for comp in row.children:
                if isinstance(comp, discord.Button) and comp.url:
                    raw_url = comp.url
                    break
            if raw_url: break
    
    if not raw_url and message.content:
         match = TIKTOK_URL_PATTERN.search(message.content)
         if match:
             raw_url = match.group(0)

    if not raw_url:
        print("   - Tidak ada URL TikTok yang valid ditemukan.")
        return

    # Ekstrak username dari URL
    username_match = re.search(r'@([^/]+)', raw_url)
    if not username_match:
        print(f"   - Tidak dapat mengekstrak username dari URL: {raw_url}")
        return
        
    username = username_match.group(1)
    print(f"   - Username Diekstrak: {username}")
    
    # Memanggil modul forwarder
    await forwarder.forward_notification(client, username, raw_url)
    
    # Memanggil modul recorder jika URL adalah LIVE
    if "/live" in raw_url and settings.RECORDER_ENABLED:
        process = recorder.start_new_recording(username)
        if process:
             await message.channel.send(f"✅ Perekaman untuk **{username}** telah dimulai.")