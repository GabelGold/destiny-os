import os, time, json

class DestinySync:
    def __init__(self, base):
        self.base = base

    def sync(self):
        ts = time.time()
        with open(f"{self.base}/sync.log","a") as f:
            f.write(f"{ts}: sync executed\n")
