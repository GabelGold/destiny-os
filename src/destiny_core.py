from datetime import datetime

class DestinyCoreBrain:
    def __init__(self, log_func=print):
        self.log = log_func
        self.state = {"mood":"neutral","tasks":[]}

    def observe(self, event):
        self.log(f"[CORE] Event erkannt: {event}")
        self.state["last_event"] = event

    def decide(self):
        task = {"timestamp":datetime.now().isoformat(),"action":"optimize"}
        self.state["tasks"].append(task)
        self.log(f"[CORE] Entscheidung getroffen: {task}")
        return task

    def reflect(self):
        self.log(f"[CORE] Zustand: {self.state}")
