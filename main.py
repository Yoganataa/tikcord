# File: main.py

import sys
import os
import asyncio
import signal

# Tambahkan path root ke sys.path agar impor dari folder lain berhasil
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from bot.client import client
from bot import events, commands # Impor untuk mendaftarkan event dan command
from config import settings
from modules import recorder # Impor untuk mengakses active_recordings saat shutdown

async def main():
    """Fungsi utama untuk menjalankan bot."""
    async with client:
        # Logika sinkronisasi command dipindahkan dari sini ke bot/events.py
        await client.start(settings.TOKEN)

def shutdown_handler():
    """Fungsi untuk mematikan semua proses perekaman dengan bersih."""
    print("\n[SHUTDOWN] Memulai proses shutdown...")
    active_procs = recorder.active_recordings
    if active_procs:
        print(f"[SHUTDOWN] Menghentikan {len(active_procs)} proses perekaman aktif...")
        for username, process in list(active_procs.items()):
            if process.is_alive():
                print(f"   - Menghentikan perekaman untuk {username} (PID: {process.pid})")
                process.terminate()
                process.join(timeout=5)
    print("[SHUTDOWN] Bot telah dimatikan.")

if __name__ == "__main__":
    if not settings.TOKEN:
        print("!!! KESALAHAN: DISCORD_TOKEN tidak ditemukan di file .env.")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            shutdown_handler()