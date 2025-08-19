import os
import time
from http.client import HTTPException
from multiprocessing import Process
from multiprocessing.synchronize import Event

from requests import RequestException

from .tiktok_api import TikTokAPI
from ..utils.logger_manager import logger
from ..utils.video_management import VideoManagement
from ..upload.telegram import Telegram
from ..utils.custom_exceptions import LiveNotFound, UserLiveError, \
    TikTokRecorderError
from ..utils.enums import Mode, Error, TimeOut, TikTokError


class TikTokRecorder:

    def __init__(
        self,
        url,
        user,
        room_id,
        mode,
        automatic_interval,
        cookies,
        proxy,
        output,
        duration,
        use_telegram,
        stop_event=None,  # New parameter for graceful stop support
    ):
        # Setup TikTok API client
        self.tiktok = TikTokAPI(proxy=proxy, cookies=cookies)

        # TikTok Data
        self.url = url
        self.user = user
        self.room_id = room_id

        # Tool Settings
        self.mode = mode
        self.automatic_interval = automatic_interval
        self.duration = duration
        self.output = output

        # Upload Settings
        self.use_telegram = use_telegram

        # Graceful stop support
        self.stop_event = stop_event

        # Check if the user's country is blacklisted
        self.check_country_blacklisted()

        # Retrieve sec_uid if the mode is FOLLOWERS
        if self.mode == Mode.FOLLOWERS:
            self.sec_uid = self.tiktok.get_sec_uid()
            if self.sec_uid is None:
                raise TikTokRecorderError("Failed to retrieve sec_uid.")

            logger.info(f"Followers mode activated\n")
        else:
            # Get live information based on the provided user data
            if self.url:
                self.user, self.room_id = \
                    self.tiktok.get_room_and_user_from_url(self.url)

            if not self.user:
                self.user = self.tiktok.get_user_from_room_id(self.room_id)

            if not self.room_id:
                self.room_id = self.tiktok.get_room_id_from_user(self.user)

            logger.info(
                f"USERNAME: {self.user}" + ("\n" if not self.room_id else ""))
            logger.info(f"ROOM_ID:  {self.room_id}" + (
                "\n" if not self.tiktok.is_room_alive(self.room_id) else ""))

        # If proxy is provided, set up the HTTP client without the proxy
        if proxy:
            self.tiktok = TikTokAPI(proxy=None, cookies=cookies)

    def _should_stop(self) -> bool:
        """Check if graceful stop was requested."""
        if self.stop_event and self.stop_event.is_set():
            logger.info("🛑 Graceful stop requested")
            return True
        return False

    def run(self):
        """
        runs the program in the selected mode. 
        
        If the mode is MANUAL, it checks if the user is currently live and
        if so, starts recording.
        
        If the mode is AUTOMATIC, it continuously checks if the user is live
        and if not, waits for the specified timeout before rechecking.
        If the user is live, it starts recording.
        """

        if self.mode == Mode.MANUAL:
            self.manual_mode()

        elif self.mode == Mode.AUTOMATIC:
            self.automatic_mode()

        elif self.mode == Mode.FOLLOWERS:
            self.followers_mode()

    def manual_mode(self):
        if not self.tiktok.is_room_alive(self.room_id):
            raise UserLiveError(
                f"@{self.user}: {TikTokError.USER_NOT_CURRENTLY_LIVE}"
            )

        self.start_recording(self.user, self.room_id)

    def automatic_mode(self):
        while True:
            # Check for graceful stop before starting new iteration
            if self._should_stop():
                logger.info("🛑 Automatic mode stopped gracefully")
                break

            try:
                self.room_id = self.tiktok.get_room_id_from_user(self.user)
                self.manual_mode()

            except UserLiveError as ex:
                logger.info(ex)
                logger.info(f"Waiting {self.automatic_interval} minutes before recheck\n")
                
                # Wait with periodic stop event checks
                for _ in range(self.automatic_interval * 60):  # Convert to seconds
                    if self._should_stop():
                        logger.info("🛑 Automatic mode stopped during wait period")
                        return
                    time.sleep(1)

            except LiveNotFound as ex:
                logger.error(f"Live not found: {ex}")
                logger.info(f"Waiting {self.automatic_interval} minutes before recheck\n")
                
                # Wait with periodic stop event checks
                for _ in range(self.automatic_interval * 60):
                    if self._should_stop():
                        logger.info("🛑 Automatic mode stopped during wait period")
                        return
                    time.sleep(1)

            except ConnectionError:
                logger.error(Error.CONNECTION_CLOSED_AUTOMATIC)
                
                # Wait with periodic stop event checks
                wait_time = TimeOut.CONNECTION_CLOSED * TimeOut.ONE_MINUTE
                for _ in range(wait_time):
                    if self._should_stop():
                        logger.info("🛑 Automatic mode stopped during connection recovery")
                        return
                    time.sleep(1)

            except Exception as ex:
                logger.error(f"Unexpected error: {ex}\n")

    def followers_mode(self):
        active_recordings = {}  # follower -> Process

        while True:
            # Check for graceful stop
            if self._should_stop():
                logger.info("🛑 Followers mode stopped gracefully")
                break

            try:
                followers = self.tiktok.get_followers_list(self.sec_uid)

                for follower in followers:
                    if self._should_stop():
                        logger.info("🛑 Followers mode stopped during follower processing")
                        return

                    if follower in active_recordings:
                        if not active_recordings[follower].is_alive():
                            logger.info(f'Recording of @{follower} finished.')
                            del active_recordings[follower]
                        else:
                            continue

                    try:
                        room_id = self.tiktok.get_room_id_from_user(follower)

                        if not room_id or not self.tiktok.is_room_alive(room_id):
                            continue

                        logger.info(f"@{follower} is live. Starting recording...")

                        process = Process(
                            target=self.start_recording,
                            args=(follower, room_id)
                        )
                        process.start()
                        active_recordings[follower] = process

                        time.sleep(2.5)

                    except Exception as e:
                        logger.error(f'Error while processing @{follower}: {e}')
                        continue

                print()
                delay = self.automatic_interval * TimeOut.ONE_MINUTE
                logger.info(f'Waiting {delay} minutes for the next check...')
                
                # Wait with periodic stop event checks
                for _ in range(delay):
                    if self._should_stop():
                        logger.info("🛑 Followers mode stopped during wait period")
                        return
                    time.sleep(1)

            except UserLiveError as ex:
                logger.info(ex)
                logger.info(f"Waiting {self.automatic_interval} minutes before recheck\n")
                
                wait_time = self.automatic_interval * TimeOut.ONE_MINUTE
                for _ in range(wait_time):
                    if self._should_stop():
                        return
                    time.sleep(1)

            except ConnectionError:
                logger.error(Error.CONNECTION_CLOSED_AUTOMATIC)
                
                wait_time = TimeOut.CONNECTION_CLOSED * TimeOut.ONE_MINUTE
                for _ in range(wait_time):
                    if self._should_stop():
                        return
                    time.sleep(1)

            except Exception as ex:
                logger.error(f"Unexpected error: {ex}\n")

    def start_recording(self, user, room_id):
        """
        Start recording live with graceful stop support
        """
        live_url = self.tiktok.get_live_url(room_id)
        if not live_url:
            raise LiveNotFound(TikTokError.RETRIEVE_LIVE_URL)

        current_date = time.strftime("%Y.%m.%d_%H-%M-%S", time.localtime())

        if isinstance(self.output, str) and self.output != '':
            if not (self.output.endswith('/') or self.output.endswith('\\')):
                if os.name == 'nt':
                    self.output = self.output + "\\"
                else:
                    self.output = self.output + "/"

        output = f"{self.output if self.output else ''}TK_{user}_{current_date}_flv.mp4"

        if self.duration:
            logger.info(f"Started recording for {self.duration} seconds")
        else:
            logger.info("🎬 Started recording...")

        buffer_size = 512 * 1024  # 512 KB buffer
        buffer = bytearray()

        logger.info("[Recording can be stopped gracefully via bot commands]")
        
        try:
            with open(output, "wb") as out_file:
                stop_recording = False
                
                while not stop_recording:
                    try:
                        # Check for graceful stop request
                        if self._should_stop():
                            logger.info("🛑 Graceful stop requested, finishing current segment...")
                            stop_recording = True
                            break

                        if not self.tiktok.is_room_alive(room_id):
                            logger.info("📴 User is no longer live. Stopping recording.")
                            break

                        start_time = time.time()
                        
                        # Download stream with periodic stop checks
                        stream_generator = self.tiktok.download_live_stream(live_url)
                        for chunk in stream_generator:
                            # Check stop event more frequently during download
                            if self._should_stop():
                                logger.info("🛑 Graceful stop during download, finishing...")
                                stop_recording = True
                                break
                                
                            buffer.extend(chunk)
                            if len(buffer) >= buffer_size:
                                out_file.write(buffer)
                                buffer.clear()

                            elapsed_time = time.time() - start_time
                            if self.duration and elapsed_time >= self.duration:
                                stop_recording = True
                                break

                    except ConnectionError:
                        if self.mode == Mode.AUTOMATIC:
                            logger.error(Error.CONNECTION_CLOSED_AUTOMATIC)
                            time.sleep(TimeOut.CONNECTION_CLOSED * TimeOut.ONE_MINUTE)

                    except (RequestException, HTTPException):
                        time.sleep(2)

                    except KeyboardInterrupt:
                        logger.info("🛑 Recording stopped by user (Ctrl+C).")
                        stop_recording = True

                    except Exception as ex:
                        logger.error(f"❌ Unexpected error during recording: {ex}")
                        stop_recording = True

                    finally:
                        # Always write remaining buffer
                        if buffer:
                            out_file.write(buffer)
                            buffer.clear()
                        out_file.flush()

        except Exception as e:
            logger.error(f"❌ Failed to create output file {output}: {e}")
            return

        logger.info(f"📹 Recording finished: {output}")
        
        # Critical: Convert file before process ends
        # This ensures the file is properly converted even during graceful stop
        logger.info("🔄 Converting FLV to MP4...")
        try:
            VideoManagement.convert_flv_to_mp4(output)
            logger.info("✅ File conversion completed successfully")
        except Exception as e:
            logger.error(f"❌ File conversion failed: {e}")

        # Upload to Telegram if enabled
        if self.use_telegram:
            try:
                final_output = output.replace('_flv.mp4', '.mp4')
                logger.info("📤 Uploading to Telegram...")
                Telegram().upload(final_output)
                logger.info("✅ Telegram upload completed")
            except Exception as e:
                logger.error(f"❌ Telegram upload failed: {e}")

    def check_country_blacklisted(self):
        is_blacklisted = self.tiktok.is_country_blacklisted()
        if not is_blacklisted:
            return False

        if self.room_id is None:
            raise TikTokRecorderError(TikTokError.COUNTRY_BLACKLISTED)

        if self.mode == Mode.AUTOMATIC:
            raise TikTokRecorderError(TikTokError.COUNTRY_BLACKLISTED_AUTO_MODE)

        elif self.mode == Mode.FOLLOWERS:
            raise TikTokRecorderError(TikTokError.COUNTRY_BLACKLISTED_FOLLOWERS_MODE)

        return is_blacklisted