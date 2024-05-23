# this file use for auto/hot-reload the webGUI using the watchdog. 
# without this, we need to manually re-run the webGUI script everytime we did some change.

import sys
import subprocess
from watchdog import *
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class ReloadEventHandler(PatternMatchingEventHandler):
    def __init__(self, patterns, command):
        super().__init__(patterns=patterns)
        self.command = command
        self.process = subprocess.Popen(self.command)

    def on_modified(self, event):
        self.process.kill()
        self.process = subprocess.Popen(self.command)

    def on_created(self, event):
        self.process.kill()
        self.process = subprocess.Popen(self.command)

if __name__ == "__main__":
    path = sys.argv[1]
    command = sys.argv[2:]

    event_handler = ReloadEventHandler(patterns=["*.py"], command=command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        event_handler.process.kill()

    observer.join()
