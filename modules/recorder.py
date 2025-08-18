import sys
import os
# Tambahkan path ke lib agar bisa mengimpor tiktok_recorder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib', 'tiktok_recorder')))

from lib.tiktok_recorder.botrec import start_recording

# Dictionary untuk melacak proses perekaman yang aktif
active_recordings = {}

def start_new_recording(username: str):
    """Memulai proses perekaman baru dan melacaknya."""
    if username in active_recordings and active_recordings[username].is_alive():
        print(f"   - Recorder: Perekaman untuk '{username}' sudah berjalan.")
        return None # Mengembalikan None jika sudah berjalan

    print("   - Recorder: Memicu proses perekaman...")
    process = start_recording(username)
    if process:
        active_recordings[username] = process
    return process

def stop_a_recording(username: str):
    """Menghentikan proses perekaman berdasarkan username."""
    if username in active_recordings and active_recordings[username].is_alive():
        process_to_stop = active_recordings[username]
        process_to_stop.terminate()
        process_to_stop.join(timeout=5)
        del active_recordings[username]
        print(f"   - Proses untuk '{username}' (PID: {process_to_stop.pid}) telah dihentikan.")
        return True # Berhasil dihentikan
    return False # Tidak ada proses untuk dihentikan