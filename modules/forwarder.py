import discord
from config import settings

async def forward_notification(client: discord.Client, username: str, url: str):
    """Mengirim notifikasi ke channel yang sesuai berdasarkan mapping."""
    target_channel_id = settings.USER_MAP.get(username, settings.FALLBACK_CHANNEL_ID)
    target_channel = client.get_channel(int(target_channel_id))

    if not target_channel:
        print(f"   - Forwarder: Channel tujuan dengan ID {target_channel_id} tidak ditemukan.")
        return

    is_mapped = username in settings.USER_MAP
    msg_template = ("Postingan baru dari **{u}**:\n{url}" if is_mapped
                    else "Notifikasi untuk user tidak terdaftar **({u})**:\n{url}")
    message_to_send = msg_template.format(u=username, url=url)

    try:
        await target_channel.send(message_to_send)
        print(f"   - Forwarder: Berhasil mengirim notifikasi ke #{target_channel.name}.")
    except Exception as e:
        print(f"   - KESALAHAN Forwarder: {e}")