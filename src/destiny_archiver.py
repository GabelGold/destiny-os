#!/usr/bin/env python3
"""
🤖 DESTINY ARCHIVER
Chat-Recorder + Script-Sorter + Metadaten-Engine
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import json
import re
from typing import List, Dict, Optional

from destiny_paths import DestinyPaths
from destiny_sorter import DestinyScriptSorter

ARCHIVE_BASE = DestinyPaths.archive()
ARCHIVE_BASE.mkdir(parents=True, exist_ok=True)


@dataclass
class ChatMeta:
    timestamp: str
    project: str
    source: str
    code_blocks: int
    tokens_estimate: int
    tags: List[str]


class DestinyChatSorterPro:
    def __init__(self, base_dir: Path = ARCHIVE_BASE):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.script_sorter = DestinyScriptSorter(base_dir=self.base_dir / "scripts")

    def _detect_project(self, chat_text: str, fallback: str = "default") -> str:
        m = re.search(r"\[PROJEKT:(.+?)\]", chat_text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return fallback

    def _extract_code_blocks(self, chat_text: str) -> List[str]:
        blocks = re.findall(r"```(?:[a-zA-Z0-9_+-]+)?\n(.*?)```", chat_text, re.DOTALL)
        return [b.strip() for b in blocks if b.strip()]

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))

    def store_chat(self, chat_text: str, project: Optional[str] = None, source: str = "manual") -> Path:
        if not chat_text.strip():
            raise ValueError("Chat ist leer.")

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        proj = project or self._detect_project(chat_text)
        proj_dir = self.base_dir / proj
        proj_dir.mkdir(parents=True, exist_ok=True)

        code_blocks = self._extract_code_blocks(chat_text)
        tokens = self._estimate_tokens(chat_text)

        meta = ChatMeta(
            timestamp=ts,
            project=proj,
            source=source,
            code_blocks=len(code_blocks),
            tokens_estimate=tokens,
            tags=["chat", "archive"]
        )

        chat_path = proj_dir / f"chat_{ts}.txt"
        meta_path = proj_dir / "project_meta.json"

        chat_path.write_text(chat_text, encoding="utf-8")

        existing: Dict[str, Dict] = {}
        if meta_path.exists():
            try:
                existing = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                existing = {}

        existing[ts] = asdict(meta)
        meta_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

        for block in code_blocks:
            self.script_sorter.store_script_block(block, project=proj, origin_chat=str(chat_path.name))

        return chat_path

    def ping(self) -> bool:
        """Health probe used by DestinyManager.health_check()."""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            return self.base_dir.exists() and self.base_dir.is_dir()
        except Exception:
            return False

    def repair(self):
        """Recreate archive root and script sorter target if missing."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.script_sorter = DestinyScriptSorter(base_dir=self.base_dir / "scripts")
        return True


def cli():
    sorter = DestinyChatSorterPro()
    print("🤖 Destiny Archiver CLI")
    print("📥 Chat eingeben (END in neuer Zeile zum Speichern):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    chat = "\n".join(lines)
    if not chat.strip():
        print("⚠ Kein Inhalt, nichts gespeichert.")
        return
    path = sorter.store_chat(chat, source="cli")
    print(f"✅ Chat gespeichert unter: {path}")


if __name__ == "__main__":
    cli()
