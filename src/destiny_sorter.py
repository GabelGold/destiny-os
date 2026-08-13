#!/usr/bin/env python3
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Optional

@dataclass
class ScriptMeta:
    timestamp: str
    project: str
    origin_chat: str
    language: str
    version: str


class DestinyScriptSorter:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _detect_language(self, code: str) -> str:
        if "docker-compose" in code or "services:" in code:
            return "yaml"
        if "import os" in code or "def " in code:
            return "python"
        if "#!/bin/bash" in code or "bash" in code:
            return "bash"
        if "<html" in code.lower():
            return "html"
        return "text"

    def _next_version(self, target_dir: Path, stem: str) -> str:
        existing = list(target_dir.glob(f"{stem}_v*.txt"))
        if not existing:
            return "v1"
        versions = []
        for p in existing:
            m = re.search(r"_v(\d+)\.txt$", p.name)
            if m:
                versions.append(int(m.group(1)))
        nxt = max(versions) + 1 if versions else 1
        return f"v{nxt}"

    def store_script_block(self, code: str, project: str, origin_chat: str) -> Path:
        lang = self._detect_language(code)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        proj_dir = self.base_dir / project / lang
        proj_dir.mkdir(parents=True, exist_ok=True)

        stem = f"script_{ts}"
        version = self._next_version(proj_dir, stem)
        file_path = proj_dir / f"{stem}_{version}.txt"

        file_path.write_text(code, encoding="utf-8")

        meta_path = proj_dir / "scripts_meta.json"
        meta = ScriptMeta(
            timestamp=ts,
            project=project,
            origin_chat=origin_chat,
            language=lang,
            version=version,
        )
        existing = {}
        if meta_path.exists():
            try:
                existing = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                existing = {}
        existing[file_path.name] = asdict(meta)
        meta_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

        return file_path
