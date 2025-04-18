# import subprocess
# import time
# import sys
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# class RestartHandler(FileSystemEventHandler):
#     def __init__(self, command):
#         self.command = command
#         self.process = self.start_process()

#     def start_process(self):
#         print("Starting Flask server...")
#         return subprocess.Popen(self.command, shell=True)

#     def on_any_event(self, event):
#         print(f"Detected change in: {event.src_path}")
#         self.process.kill()
#         time.sleep(1)
#         self.process = self.start_process()

# if __name__ == "__main__":
#     watch_path = "D:/POC - CONFLUENCE/storage-server(v2)/data"  
#     command = "python app.py"  

#     event_handler = RestartHandler(command)
#     observer = Observer()
#     observer.schedule(event_handler, watch_path, recursive=True)
#     observer.start()

#     print(f"Watching for changes in '{watch_path}'...")
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()


import subprocess
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import Config

class RestartHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.restart_pending = False
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.kill()
            time.sleep(1)  # Give it time to shut down
        print("Starting Flask server...")
        self.process = subprocess.Popen(self.command, shell=True)
        self.restart_pending = False

    def on_modified(self, event):
        if not event.is_directory:
            config = Config()
            data_files = {
                config.INDEX_FILE,
                config.TITLES_FILE,
                config.CONTENTS_FILE
            }
            if event.src_path in data_files:
                print(f"Detected change in data file: {event.src_path}")
                if not self.restart_pending:
                    self.restart_pending = True
                    # Small delay to catch multiple simultaneous saves
                    time.sleep(0.5)
                    self.start_process()

if __name__ == "__main__":
    config = Config()
    watch_path = config.DATA_DIR
    command = "python app.py"
    
    print(f"Watching for changes in '{watch_path}'...")
    event_handler = RestartHandler(command)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()