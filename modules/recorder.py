# File: modules/recorder.py

import sys
import os
import multiprocessing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib', 'tiktok_recorder')))

# Kita tidak lagi butuh 'botrec', kita panggil 'main' dari library langsung
from lib.tiktok_recorder.main import main as run_recorder_main
from lib.tiktok_recorder.utils import utils as recorder_utils

# Dictionary untuk melacak proses perekaman
active_recordings = {}

def start_new_recording(username: str):
    """Memulai proses perekaman baru menggunakan fungsi 'main' dari library."""
    if username in active_recordings and active_recordings[username].is_alive():
        print(f"   - Recorder: Perekaman untuk '{username}' sudah berjalan.")
        return None

    print(f"   - Recorder: Memicu proses perekaman untuk {username}...")
    
    # Menyiapkan argumen seolah-olah dari command line
    # Ini memastikan semua inisialisasi di dalam library berjalan
    sys.argv = [
        'main.py',
        '-user', username,
        '-mode', 'automatic',
        '-no-update-check' # Nonaktifkan cek update agar tidak mengganggu
    ]
    
    process = multiprocessing.Process(target=run_recorder_main)
    process.start()
    
    if process.is_alive():
        active_recordings[username] = process
        print(f"   - Recorder: Perekaman untuk '{username}' berhasil dimulai (PID: {process.pid}).")
        return process
    else:
        print(f"   - KESALAHAN Recorder: Proses untuk '{username}' gagal dimulai.")
        return None

def stop_a_recording(username: str):
    """Menghentikan proses perekaman berdasarkan username."""
    process_to_stop = active_recordings.get(username)
    if process_to_stop and process_to_stop.is_alive():
        print(f"   - Mengirim sinyal berhenti ke proses untuk '{username}' (PID: {process_to_stop.pid})")
        
        # Di Windows, terminate() adalah cara yang paling umum untuk mengirim sinyal stop
        # yang bisa ditangani, mirip dengan Ctrl+C di console.
        process_to_stop.terminate()
        del active_recordings[username]
        return True
    return False