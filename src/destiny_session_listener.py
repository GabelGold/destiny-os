#!/usr/bin/env python3
"""
Session Listener Stub – könnte später Chats automatisch abgreifen.
Aktuell nur Platzhalter, damit Imports nicht brechen.
"""

from pathlib import Path
from datetime import datetime
from destiny_archiver import DestinyChatSorterPro


class DestinySessionListener:
    def __init__(self, base_dir: Path | None = None):
        self.archiver = DestinyChatSorterPro()

    def record_snippet(self, text: str, project: str = "session"):
        if not text.strip():
            return
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = f"[SESSION {ts}]\n{text}"
        self.archiver.store_chat(payload, project=project, source="session-listener")
