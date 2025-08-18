import os
import json
from dotenv import load_dotenv

# Muat file .env dari direktori utama
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# --- Konfigurasi Discord & Bot ---
TOKEN = os.getenv('DISCORD_TOKEN')
SOURCE_BOT_ID = int(os.getenv('SOURCE_BOT_ID'))
FALLBACK_CHANNEL_ID = int(os.getenv('FALLBACK_CHANNEL_ID'))
GUILD_ID = os.getenv('GUILD_ID') # Opsional, untuk sinkronisasi command cepat

# --- Konfigurasi Channel Pantauan ---
MONITORED_CHANNELS = []
main_server_id_str = os.getenv('MAIN_SERVER_ID')
if main_server_id_str:
    MONITORED_CHANNELS.append(int(main_server_id_str))

multi_server_ids_str = os.getenv('MULTI_SERVER_ID')
if multi_server_ids_str:
    id_list = multi_server_ids_str.split(',')
    for channel_id in id_list:
        if channel_id.strip():
            MONITORED_CHANNELS.append(int(channel_id.strip()))

# --- Konfigurasi Fitur ---
RECORDER_ENABLED = os.getenv('RECORDER_ENABLED', 'false').lower() == 'true'

# --- Memuat Mapping User ---
USER_MAP = {}
try:
    map_path = os.path.join(os.path.dirname(__file__), 'user_map.json')
    with open(map_path, 'r', encoding='utf-8') as f:
        USER_MAP = json.load(f)
    print("[CONFIG] File user_map.json berhasil dimuat.")
except FileNotFoundError:
    print("PERINGATAN: File 'config/user_map.json' tidak ditemukan.")
except json.JSONDecodeError:
    print("!!! KESALAHAN: Format JSON di 'config/user_map.json' salah!")