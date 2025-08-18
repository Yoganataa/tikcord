import multiprocessing  
import time
from multiprocessing.synchronize import Event  
from typing import Dict, Optional

# Centralized state management - single source of truth
active_recordings: Dict[str, multiprocessing.Process] = {}
stop_events: Dict[str, Event] = {}

def start_new_recording(username: str) -> Optional[multiprocessing.Process]:
    """
    Start new recording process for a TikTok user.
    
    Args:
        username: TikTok username to record
        
    Returns:
        Process object if successful, None if already recording or failed
    """
    # Check if already recording
    if username in active_recordings:
        process = active_recordings[username]
        if process.is_alive():
            print(f"   - Recorder: Recording for '{username}' is already running (PID: {process.pid}).")
            return None
        else:
            # Clean up dead process
            print(f"   - Recorder: Cleaning up dead process for '{username}'.")
            _cleanup_recording(username)
    
    print(f"   - Recorder: Starting new recording process for '{username}'...")
      
    # Create stop event for graceful shutdown communication
    stop_event = multiprocessing.Event()
      
    # Import and start recording with stop event support
    try:
        from lib.tiktok_recorder.bridge import start_recording  
        process = start_recording(username, stop_event)  
    except ImportError as e:
        print(f"   - ❌ Recorder ERROR: Failed to import recording module: {e}")
        return None
    except Exception as e:
        print(f"   - ❌ Recorder ERROR: Failed to start recording: {e}")
        return None
      
    if process and process.is_alive():  
        active_recordings[username] = process  
        stop_events[username] = stop_event  
        print(f"   - ✅ Recorder: Recording started for '{username}' (PID: {process.pid}).")  
        return process  
    else:  
        print(f"   - ❌ Recorder ERROR: Process for '{username}' failed to start.")  
        return None  

def stop_a_recording(username: str) -> Optional[multiprocessing.Process]:
    """
    Gracefully stop a recording process.
    
    This function:
    1. Sends a graceful stop signal via Event
    2. Waits for the process to finish naturally (including file conversion)
    3. Only uses terminate() as last resort after timeout
    
    Args:
        username: TikTok username to stop recording for
        
    Returns:
        Process object that was stopped, or None if not found
    """
    process = active_recordings.get(username)
    stop_event = stop_events.get(username)
      
    if not process:
        print(f"   - ℹ️ Recorder: No active recording found for '{username}'.")
        return None
        
    if not process.is_alive():
        print(f"   - ℹ️ Recorder: Process for '{username}' is already dead.")
        _cleanup_recording(username)
        return None
    
    if not stop_event:
        print(f"   - ⚠️ Recorder: No stop event found for '{username}', using terminate.")
        process.terminate()
        _cleanup_recording(username)
        return process
        
    print(f"   - 🛑 Recorder: Sending graceful stop signal to '{username}' (PID: {process.pid})")
    
    # Step 1: Send graceful stop signal
    stop_event.set()
    
    # Step 2: Wait for graceful shutdown (allow time for file conversion)
    # This is critical - recorder needs time to finish current segment and convert to mp4
    print(f"   - ⏳ Recorder: Waiting for '{username}' to finish gracefully...")
    process.join(timeout=45)  # Extended timeout for file conversion
    
    # Step 3: Check if process finished gracefully
    if not process.is_alive():
        print(f"   - ✅ Recorder: '{username}' stopped gracefully and file conversion completed.")
        _cleanup_recording(username)
        return process
    
    # Step 4: Force terminate as last resort
    print(f"   - ⚠️ Recorder: '{username}' didn't respond to graceful stop within 45s, forcing termination...")
    process.terminate()
    
    # Give a bit more time for cleanup after terminate
    process.join(timeout=10)
    
    if process.is_alive():
        print(f"   - ❌ Recorder: '{username}' process is still alive after terminate! Consider restarting bot.")
    
    _cleanup_recording(username)
    return process

def get_active_recordings() -> Dict[str, multiprocessing.Process]:
    """
    Get current active recordings.
    
    Returns:
        Dictionary of username -> process mappings
    """
    # Clean up dead processes first
    dead_users = []
    for username, process in active_recordings.items():
        if not process.is_alive():
            dead_users.append(username)
    
    for username in dead_users:
        print(f"   - 🧹 Recorder: Cleaning up dead process for '{username}'.")
        _cleanup_recording(username)
    
    return active_recordings.copy()

def _cleanup_recording(username: str) -> None:
    """
    Clean up recording state for a user.
    
    Args:
        username: TikTok username to clean up
    """
    if username in active_recordings:
        del active_recordings[username]
    if username in stop_events:
        del stop_events[username]

def shutdown_all_recordings() -> None:
    """
    Gracefully shutdown all active recordings.
    This should be called during bot shutdown.
    """
    if not active_recordings:
        print("   - 🔹 Recorder: No active recordings to shutdown.")
        return
    
    print(f"   - 🛑 Recorder: Shutting down {len(active_recordings)} active recordings...")
    
    # Send graceful stop to all
    for username, stop_event in stop_events.items():
        print(f"     • Stopping '{username}'...")
        stop_event.set()
    
    # Wait for all to finish
    for username, process in list(active_recordings.items()):
        if process.is_alive():
            print(f"     • Waiting for '{username}' to finish...")
            process.join(timeout=30)  # Reasonable timeout during shutdown
            
            if process.is_alive():
                print(f"     • Force terminating '{username}'...")
                process.terminate()
                process.join(timeout=5)
    
    # Clear all state
    active_recordings.clear()
    stop_events.clear()
    print("   - ✅ Recorder: All recordings shutdown complete.")