#!/usr/bin/env python3
import time
from pathlib import Path

from destiny_paths import DestinyPaths

DestinyPaths.ensure()
LOG = DestinyPaths.logs() / "monitor.log"
ADVISOR_LOG = DestinyPaths.logs() / "advisor.log"


def evaluate_line(line):
    if "Alive=False" in line:
        return "⚠️ Tunnel down → Restart good, check connection stability."
    if "Reconnects" in line and "5" in line:
        return "⚠️ Too many reconnects → network unstable or blocked."
    return "✔️ System OK."


def advisor_loop():
    last_seen = 0
    ADVISOR_LOG.parent.mkdir(parents=True, exist_ok=True)

    while True:
        if LOG.exists():
            lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()

            for i, line in enumerate(lines[last_seen:], start=last_seen):
                result = evaluate_line(line)
                with open(ADVISOR_LOG, "a", encoding="utf-8") as f:
                    f.write(f"{time.ctime()} | advice: {result}\n")

            last_seen = len(lines)

        time.sleep(6)


if __name__ == "__main__":
    advisor_loop()
