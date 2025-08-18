# File: lib/tiktok_recorder/bridge.py
# Enhanced with graceful stop support via multiprocessing.Event

import multiprocessing
from multiprocessing.synchronize import Event
import os
import re
import json

from .core.tiktok_recorder import TikTokRecorder
from .utils.logger_manager import logger
from .utils.enums import Mode

def sanitize_foldername(name: str) -> str:
    """Sanitize username for safe folder creation."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def _start_recording_process(user: str, output_path: str, cookies: dict, stop_event: Event):
    """
    Internal function that runs the actual recording process.
    
    Now properly handles the stop_event for graceful shutdown.
    """
    try:
        logger.info(f"🎬 Starting recording process: {user} -> {output_path}")
        
        # Create TikTokRecorder with stop_event support
        recorder = TikTokRecorder(
            user=user, 
            mode=Mode.AUTOMATIC, 
            output=output_path, 
            cookies=cookies,
            stop_event=stop_event,  # Pass the stop event for graceful shutdown
            url=None, 
            room_id=None, 
            automatic_interval=5, 
            proxy=None,
            duration=None, 
            use_telegram=False
        )
        
        # Start recording - this will now respect the stop_event
        recorder.run()
        
        logger.info(f"✅ Recording process completed for {user}")
        
    except Exception as e:
        logger.error(f"❌ Error in recording process for {user}: {e}")

def start_recording(username: str, stop_event: Event):
    """
    Main function to start recording with graceful stop support.
    
    Args:
        username: TikTok username to record
        stop_event: Event object for graceful shutdown signaling
    
    Returns:
        Process object if successful, None otherwise
    """
    if not username: 
        logger.error("Username cannot be empty")
        return None
        
    logger.info(f"🎯 Recording request received for: {username}")
    
    # Sanitize username for folder creation
    safe_folder_name = sanitize_foldername(username)
    
    # Create output directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    output_path = os.path.join(project_root, 'downloads', safe_folder_name)

    try:
        os.makedirs(output_path, exist_ok=True)
        logger.info(f"📁 Output directory ready: {output_path}")
    except OSError as e:
        logger.error(f"❌ Failed to create directory {output_path}: {e}")
        return None
    
    # Ensure output path ends with separator
    if not output_path.endswith(os.path.sep):
        output_path += os.path.sep
    
    # Load cookies configuration
    cookies = {}
    try:
        cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.json')
        if os.path.exists(cookies_path):
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
            logger.info("🍪 Cookies loaded successfully")
        else:
            logger.warning("⚠️ cookies.json not found, using empty cookies")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load cookies.json: {e}")
    
    # Create and start the recording process
    try:
        process = multiprocessing.Process(
            target=_start_recording_process,
            args=(username, output_path, cookies, stop_event),
            name=f"TikTokRecorder-{username}"
        )
        process.start()
        
        if process.is_alive():
            logger.info(f"🚀 Recording process started successfully for {username} (PID: {process.pid})")
            return process
        else:
            logger.error(f"❌ Recording process failed to start for {username}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to create recording process for {username}: {e}")
        return None