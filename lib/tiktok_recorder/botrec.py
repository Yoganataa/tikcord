# File: lib/tiktok_recorder/botrec.py

import multiprocessing
from multiprocessing.synchronize import Event
import os
import re
import json

from .core.tiktok_recorder import TikTokRecorder
from .utils.logger_manager import logger
from .utils.enums import Mode

def sanitize_foldername(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def _start_recording_process(user, output_path, cookies, stop_event):
    """Fungsi internal sekarang menerima 'stop_event'."""
    try:
        logger.info(f"Memulai proses: {user} -> {output_path}")
        TikTokRecorder(
            user=user, mode=Mode.AUTOMATIC, output=output_path, cookies=cookies,
            stop_event=stop_event,  # <-- Teruskan event ke perekam
            url=None, room_id=None, automatic_interval=5, proxy=None,
            duration=None, use_telegram=False
        ).run()
    except Exception as e:
        logger.error(f"Error di proses perekaman {user}: {e}")

def start_recording(username: str, stop_event: Event):
    """FUNGSI UTAMA. Sekarang menerima 'stop_event' dari bot utama."""
    if not username: return None
    logger.info(f"Sinyal rekam diterima untuk: {username}")
    safe_folder_name = sanitize_foldername(username)
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    output_path = os.path.join(project_root, 'downloads', safe_folder_name)

    try:
        os.makedirs(output_path, exist_ok=True)
    except OSError as e:
        logger.error(f"Gagal membuat direktori {output_path}: {e}")
        return None
        
    cookies = {}
    try:
        cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.json')
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
    except Exception:
        logger.warning("cookies.json tidak ditemukan atau error.")
    
    process = multiprocessing.Process(
        target=_start_recording_process,
        args=(username, output_path + os.path.sep, cookies, stop_event)  # <-- Teruskan event
    )
    process.start()
    return process