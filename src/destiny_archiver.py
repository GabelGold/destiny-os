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

    def create_project(self, name: str) -> Path:
        slug = re.sub(r"[^\w\-]+", "_", (name or "").strip()).strip("_") or "projekt"
        path = self.base_dir / slug
        path.mkdir(parents=True, exist_ok=True)
        return path

    def list_projects(self) -> List[Dict]:
        skip = {"incoming", "scripts", "processed"}
        projects = []
        if not self.base_dir.exists():
            return projects
        for proj in sorted(self.base_dir.iterdir()):
            if not proj.is_dir() or proj.name in skip:
                continue
            chats = len(list(proj.glob("chat_*.txt")))
            code_dir = proj / "code"
            scripts_dir = self.base_dir / "scripts" / proj.name
            code_blocks = 0
            if code_dir.exists():
                code_blocks += sum(1 for p in code_dir.rglob("*") if p.is_file())
            if scripts_dir.exists():
                code_blocks += sum(1 for p in scripts_dir.rglob("script_*.txt") if p.is_file())
            projects.append({"name": proj.name, "chats": chats, "code_blocks": code_blocks})
        return projects

    def stats(self) -> Dict:
        projects = self.list_projects()
        return {
            "projects": len(projects),
            "chats": sum(p["chats"] for p in projects),
            "code_blocks": sum(p["code_blocks"] for p in projects),
        }

    def save_chat(self, text: str, source: str = "web", project_override: str = "") -> Dict:
        """Flask-kompatible Hülle um store_chat (kanonischer Einstieg)."""
        project = (project_override or "").strip() or None
        path = self.store_chat(text, project=project, source=source)
        return {
            "project": project or path.parent.name,
            "slug": path.parent.name,
            "chat_file": str(path),
            "code_blocks": self._extract_code_blocks(text).__len__(),
        }


# Kanonischer Archiver für Destiny OS: DestinyChatSorterPro.
# Alle Oberflächen (GUI, Flask, Listener) sollen diese Klasse nutzen.


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
