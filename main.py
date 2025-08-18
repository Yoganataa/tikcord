# File: main.py
# Enhanced with proper graceful shutdown and signal handling

import sys
import os
import asyncio
import multiprocessing
import signal
from typing import NoReturn

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from bot.client import client
from bot import events, commands
from config import settings
from modules import recorder

def signal_handler(signum: int, frame) -> NoReturn:
    """Handle shutdown signals gracefully."""
    print(f"\n🛑 [SHUTDOWN] Received signal {signum}")
    print("⏳ [SHUTDOWN] Gracefully shutting down all recordings...")
    
    # Shutdown all recordings gracefully
    recorder.shutdown_all_recordings()
    
    print("✅ [SHUTDOWN] Bot shutdown complete.")
    sys.exit(0)

async def main():
    """Main function to run the bot."""
    try:
        print("🚀 Starting TikCord bot...")
        print(f"📡 Monitoring {len(settings.MONITORED_CHANNELS)} channels")
        print(f"🎬 Recording enabled: {settings.RECORDER_ENABLED}")
        
        async with client:
            await client.start(settings.TOKEN)
            
    except KeyboardInterrupt:
        print("\n🛑 [SHUTDOWN] KeyboardInterrupt received")
        recorder.shutdown_all_recordings()
        raise
    except Exception as e:
        print(f"❌ [ERROR] Bot crashed: {e}")
        recorder.shutdown_all_recordings()
        raise

if __name__ == "__main__":
    # Enable multiprocessing support (important for Windows)
    multiprocessing.freeze_support()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Validate configuration
    if not settings.TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not found in .env file!")
        print("💡 Create a .env file based on .env.example")
        sys.exit(1)
    
    if not settings.MONITORED_CHANNELS:
        print("⚠️ WARNING: No monitored channels configured!")
        print("💡 Configure MAIN_SERVER_ID or MULTI_SERVER_ID in .env")
    
    try:
        # Run the bot
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
        
    finally:
        # Ensure all child processes are cleaned up
        print("🧹 Cleaning up child processes...")
        for proc in multiprocessing.active_children():
            if proc.is_alive():
                print(f"   • Terminating process: {proc.name} (PID: {proc.pid})")
                proc.terminate()
                proc.join(timeout=5)
        print("✅ Cleanup complete")