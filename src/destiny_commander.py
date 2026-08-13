import time, os
import json
import subprocess
from pathlib import Path

LOG = Path("/media/christians/EprimoSpeicher/Projektmappe/destiny_system/commander.log")

def log(msg):
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a") as f:
        f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")
    print("⚡", msg)

COMMAND_MAP = {
    "restart gui": "systemctl restart destiny_gui.service",
    "restart core": "systemctl restart destiny_core.service",
    "update now": "systemctl restart destiny_updater.service",
    "heal": "systemctl restart destiny_watchdog.service",
    "backup now": "systemctl restart destiny_backup.service",
}

def run(cmd):
    log(f"Running: {cmd}")
    os.system(cmd)

def main():
    log("Commander online")
    inbox = Path("/media/christians/EprimoSpeicher/Projektmappe/destiny_system/commander_in.txt")
    while True:
        if inbox.exists():
            cmd = inbox.read_text().strip().lower()
            log(f"Received command: {cmd}")
            inbox.unlink()
            for key, action in COMMAND_MAP.items():
                if key in cmd:
                    run(action)
                    break
            else:
                log("❓ Unknown command")
        time.sleep(2)


if __name__ == "__main__":
    main()
