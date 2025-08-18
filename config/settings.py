import os
import json
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load .env dari direktori utama
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_env_int(key: str, default: Optional[int] = None, required: bool = False) -> Optional[int]:
    """Safely parse environment variable as integer."""
    value = os.getenv(key)
    if not value:
        if required:
            print(f"❌ ERROR: Required environment variable '{key}' is missing!")
            sys.exit(1)
        return default
    
    try:
        return int(value)
    except ValueError:
        print(f"❌ ERROR: Environment variable '{key}' must be a valid integer, got: {value}")
        sys.exit(1)

def get_env_str(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Safely get environment variable as string."""
    value = os.getenv(key)
    if not value:
        if required:
            print(f"❌ ERROR: Required environment variable '{key}' is missing!")
            sys.exit(1)
        return default
    return value

def parse_channel_ids(ids_str: Optional[str]) -> List[int]:
    """Parse comma-separated channel IDs from string."""
    if not ids_str:
        return []
    
    result = []
    for channel_id in ids_str.split(','):
        channel_id = channel_id.strip()
        if channel_id:
            try:
                result.append(int(channel_id))
            except ValueError:
                print(f"⚠️ WARNING: Invalid channel ID '{channel_id}', skipping...")
                continue
    return result

# === Discord & Bot Configuration ===
TOKEN = get_env_str('DISCORD_TOKEN', required=True)
SOURCE_BOT_ID = get_env_int('SOURCE_BOT_ID', required=True)
FALLBACK_CHANNEL_ID = get_env_int('FALLBACK_CHANNEL_ID', required=True)
GUILD_ID = get_env_int('GUILD_ID')  # Optional, for faster command sync

# === Channel Monitoring Configuration ===
MONITORED_CHANNELS = []

# Main server channel
main_server_id = get_env_int('MAIN_SERVER_ID')
if main_server_id:
    MONITORED_CHANNELS.append(main_server_id)

# Multiple server channels
multi_server_ids = parse_channel_ids(get_env_str('MULTI_SERVER_ID'))
MONITORED_CHANNELS.extend(multi_server_ids)

if not MONITORED_CHANNELS:
    print("⚠️ WARNING: No monitored channels configured. Bot will not monitor any channels.")

# === Feature Configuration ===
RECORDER_ENABLED = get_env_str('RECORDER_ENABLED', 'false').lower() == 'true'

# === User Mapping Configuration ===
USER_MAP: Dict[str, str] = {}
try:
    map_path = os.path.join(os.path.dirname(__file__), 'user_map.json')
    if os.path.exists(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            USER_MAP = json.load(f)
        print(f"✅ [CONFIG] user_map.json loaded successfully with {len(USER_MAP)} mappings.")
    else:
        print("⚠️ [CONFIG] user_map.json not found. Using default fallback channel for all users.")
except json.JSONDecodeError as e:
    print(f"❌ [CONFIG] ERROR: Invalid JSON format in user_map.json: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ [CONFIG] ERROR: Failed to read user_map.json: {e}")
    sys.exit(1)

# === Validation Summary ===
print("🔧 [CONFIG] Configuration loaded:")
print(f"   • Monitored channels: {len(MONITORED_CHANNELS)}")
print(f"   • User mappings: {len(USER_MAP)}")
print(f"   • Recorder enabled: {RECORDER_ENABLED}")
print(f"   • Guild ID: {GUILD_ID or 'Global commands'}")