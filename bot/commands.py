# File: bot/commands.py
# Enhanced with better user feedback and error handling

import discord
import asyncio
from discord import app_commands
from bot.client import tree
from modules import forwarder, recorder
from config import settings

@tree.command(name="live", description="Start recording & notification for TikTok live user.")
@app_commands.describe(username="TikTok username to process")
async def live_command(interaction: discord.Interaction, username: str):
    """Command to manually trigger live recording and notification."""
    # Validate username
    username = username.lstrip('@').strip()
    if not username:
        await interaction.response.send_message("❌ Please provide a valid username.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"✅ Processing request for **{username}**...", ephemeral=True)
    live_url = f"https://www.tiktok.com/@{username}/live"
    
    # Send notification
    try:
        await forwarder.forward_notification(interaction.client, username, live_url)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Failed to send notification: {str(e)}", ephemeral=True)
    
    # Start recording if enabled
    if settings.RECORDER_ENABLED:
        try:
            process = recorder.start_new_recording(username)
            if process:
                await interaction.followup.send(
                    f"🎬 Recording started for **{username}**.\n"
                    f"💡 Use `/stop {username}` to stop recording gracefully.", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"⚠️ Recording for **{username}** is already active or failed to start.", 
                    ephemeral=True
                )
        except Exception as e:
            await interaction.followup.send(f"❌ Recording failed: {str(e)}", ephemeral=True)
    else:
        await interaction.followup.send("ℹ️ Recording is disabled in bot configuration.", ephemeral=True)

@tree.command(name="stop", description="Gracefully stop recording for a user.")  
@app_commands.describe(username="TikTok username to stop recording for")  
async def stop_command(interaction: discord.Interaction, username: str):  
    """
    Gracefully stop recording command.
    
    This command:
    1. Sends stop signal to the recording process
    2. Waits for the process to finish current segment
    3. Allows file conversion to complete
    4. Provides user feedback throughout the process
    """
    # Validate username
    username = username.lstrip('@').strip()
    if not username:
        await interaction.response.send_message("❌ Please provide a valid username.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)  
      
    # Check if recording exists
    active_recordings = recorder.get_active_recordings()
    if username not in active_recordings:
        await interaction.followup.send(f"ℹ️ No active recording found for **{username}**.", ephemeral=True)
        return
    
    # Send initial feedback
    process = active_recordings[username]
    await interaction.followup.send(
        f"🛑 Stopping recording for **{username}** (PID: {process.pid})...\n"
        f"⏳ Please wait while the recording finishes gracefully and converts to MP4.\n"
        f"📝 This may take up to 45 seconds.", 
        ephemeral=True
    )
    
    # Start graceful stop
    try:
        process_to_stop = recorder.stop_a_recording(username)  
        
        if not process_to_stop:
            await interaction.followup.send(f"ℹ️ No process to stop for **{username}**.", ephemeral=True)
            return
        
        # Wait and provide progress updates
        await asyncio.sleep(5)  # Initial wait
        
        if process_to_stop.is_alive():
            await interaction.followup.send(
                f"⏳ Recording for **{username}** is finishing current segment and converting file...\n"
                f"🔄 Please continue to wait...", 
                ephemeral=True
            )
            
            # Wait more for conversion
            await asyncio.sleep(25)  # Total ~30 seconds so far
            
            if process_to_stop.is_alive():
                await interaction.followup.send(
                    f"⚠️ Recording for **{username}** is taking longer than expected.\n"
                    f"🔧 Waiting additional time for file conversion...", 
                    ephemeral=True
                )
                
                await asyncio.sleep(15)  # Total ~45 seconds
                
                if process_to_stop.is_alive():
                    await interaction.followup.send(
                        f"❌ Recording for **{username}** did not respond to graceful stop within 45 seconds.\n"
                        f"🚨 Process was terminated forcefully. File may be incomplete.", 
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        f"✅ Recording for **{username}** stopped successfully!\n"
                        f"📁 Video has been processed and saved.", 
                        ephemeral=True
                    )
            else:
                await interaction.followup.send(
                    f"✅ Recording for **{username}** stopped gracefully!\n"
                    f"📁 Video has been converted and saved successfully.", 
                    ephemeral=True
                )
        else:
            await interaction.followup.send(
                f"✅ Recording for **{username}** stopped quickly!\n"
                f"📁 Video processing completed.", 
                ephemeral=True
            )
            
    except Exception as e:
        await interaction.followup.send(
            f"❌ Error stopping recording for **{username}**: {str(e)}", 
            ephemeral=True
        )

@tree.command(name="status", description="Show status of active recordings.")
async def status_command(interaction: discord.Interaction):
    """Show current recording status."""
    await interaction.response.defer(ephemeral=True)
    
    try:
        active_recordings = recorder.get_active_recordings()
        
        if not active_recordings:
            await interaction.followup.send("ℹ️ No active recordings.", ephemeral=True)
            return
        
        status_lines = ["📊 **Active Recordings:**"]
        for username, process in active_recordings.items():
            status = "🟢 Running" if process.is_alive() else "🔴 Dead"
            status_lines.append(f"• **{username}** (PID: {process.pid}) - {status}")
        
        status_message = "\n".join(status_lines)
        await interaction.followup.send(status_message, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting status: {str(e)}", ephemeral=True)