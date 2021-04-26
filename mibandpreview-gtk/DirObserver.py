#!/usr/bin/env python3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def __init__(self, cbk):
        super()
        self.cbk = cbk

    def on_modified(self, event):
        self.cbk.on_change()

    def on_created(self, event):
        self.cbk.on_change()

    def on_deleted(self, event):
        pass

    def on_moved(self, event):
        self.cbk.on_change()

def new(path, callback):
    d = DirObserver()
    d.watch(path, callback)
    return d

class DirObserver:
    def watch(self, path, callback):
        observer = Observer()
        observer.schedule(Handler(callback), path=path+"/", recursive=True)
        observer.start()
        self.obs = observer
        print("Watcher started for "+path)

    def stop(self):
        print("Stopping watcher...")
        self.obs.stop()
