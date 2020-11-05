#!/usr/bin/env python3
import os, time, subprocess, threading
from datetime import datetime, timedelta

def new(path, callback):
    d = DirObserver()
    d.watch(path, callback)
    return d

class DirObserver:
    def __init__(self):
        self.last_event = datetime.fromtimestamp(0)

    def watch(self, path, callback):
        self.callback = callback
        self.path = path

        self.proc = subprocess.Popen(["inotifywait", "-mrq", "--format", "%e", self.path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t = threading.Thread(target=self.reader, args=(self.proc,))
        t.start()
        print("Watcher started for "+path)

    def stop(self):
        print("Stopping watcher...")
        self.proc.terminate()

    def reader(self, proc):
        for line in iter(proc.stdout.readline, b''):
            line = line.decode("utf-8")
            if "CLOSE_WRITE" in line or "DELETE" in line or "CREATE" in line:
                if datetime.today()-self.last_event > timedelta(seconds=0.5):
                    t = threading.Timer(0.25, self.callback.on_change)
                    t.start()
                    self.last_event = datetime.today()
