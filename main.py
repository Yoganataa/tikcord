# File: main.py

import sys
import os
import asyncio
import multiprocessing

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from bot.client import client
from bot import events, commands
from config import settings
from modules import recorder

async def main():
    """Fungsi utama untuk menjalankan bot."""
    async with client:
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
                process.join(timeout=10) # Beri waktu lebih lama untuk cleanup
    print("[SHUTDOWN] Bot telah dimatikan.")

if __name__ == "__main__":
    multiprocessing.freeze_support() # Penting untuk Windows
    
    if not settings.TOKEN:
        print("!!! KESALAHAN: DISCORD_TOKEN tidak ditemukan di file .env.")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            # Tidak perlu memanggil shutdown_handler secara eksplisit di sini,
            # karena terminate akan mengirim sinyal yang benar ke proses anak.
            print("\n[SHUTDOWN] KeyboardInterrupt terdeteksi. Menutup bot.")
            # Pastikan semua proses anak juga mati saat skrip utama berhenti
            for proc in multiprocessing.active_children():
                proc.terminate()
                proc.join()