import multiprocessing  
from multiprocessing.synchronize import Event  
  
# Dictionary untuk melacak proses dan event  
active_recordings = {}  
stop_events = {}  
  
def start_new_recording(username: str):  
    if username in active_recordings and active_recordings[username].is_alive():  
        print(f"   - Recorder: Perekaman untuk '{username}' sudah berjalan.")  
        return None  
  
    print(f"   - Recorder: Memicu proses perekaman untuk {username}...")  
      
    # Buat stop_event untuk komunikasi dengan proses  
    stop_event = multiprocessing.Event()  
      
    # Gunakan botrec.start_recording yang sudah mendukung stop_event  
    from lib.tiktok_recorder.bridge import start_recording  
    process = start_recording(username, stop_event)  
      
    if process and process.is_alive():  
        active_recordings[username] = process  
        stop_events[username] = stop_event  
        print(f"   - Recorder: Perekaman untuk '{username}' berhasil dimulai (PID: {process.pid}).")  
        return process  
    else:  
        print(f"   - KESALAHAN Recorder: Proses untuk '{username}' gagal dimulai.")  
        return None  
  
def stop_a_recording(username: str):  
    process_to_stop = active_recordings.get(username)  
    stop_event = stop_events.get(username)  
      
    if process_to_stop and process_to_stop.is_alive() and stop_event:  
        print(f"   - Mengirim sinyal graceful stop ke proses untuk '{username}' (PID: {process_to_stop.pid})")  
          
        # Set event untuk sinyal graceful stop  
        stop_event.set()  
          
        # Tunggu proses selesai secara graceful (maksimal 30 detik)  
        process_to_stop.join(timeout=30)  
          
        if process_to_stop.is_alive():  
            print(f"   - Proses {username} tidak merespons graceful stop, melakukan terminate...")  
            process_to_stop.terminate()  
          
        # Cleanup  
        if username in active_recordings:  
            del active_recordings[username]  
        if username in stop_events:  
            del stop_events[username]  
              
        return process_to_stop  
    return None