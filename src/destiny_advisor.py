import time
from pathlib import Path

LOG = Path("/home/christians/destiny_system/monitor.log")
ADVISOR_LOG = Path("/home/christians/destiny_system/advisor.log")

def evaluate_line(line):
    if "Alive=False" in line:
        return "⚠️ Tunnel down → Restart good, check connection stability."
    if "Reconnects" in line and "5" in line:
        return "⚠️ Too many reconnects → network unstable or blocked."
    return "✔️ System OK."

def advisor_loop():
    last_seen = 0

    while True:
        if LOG.exists():
            lines = LOG.read_text().splitlines()

            for i, line in enumerate(lines[last_seen:], start=last_seen):
                result = evaluate_line(line)
                with open(ADVISOR_LOG, "a") as f:
                    f.write(f"{time.ctime()} | advice: {result}\n")

            last_seen = len(lines)

        time.sleep(6)

if __name__ == "__main__":
    advisor_loop()
