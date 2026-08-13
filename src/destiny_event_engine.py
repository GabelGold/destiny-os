import threading, time
from datetime import datetime
from destiny_core import DestinyCoreBrain

class DestinyEventEngine:
    def __init__(self):
        self.core = DestinyCoreBrain()
        self.running = True

    def run(self):
        while self.running:
            self.core.observe("heartbeat")
            self.core.decide()
            time.sleep(5)
