from pathlib import Path

from destiny_sorter import DestinyScriptSorter


def test_detect_and_store(tmp_path: Path):
    sorter = DestinyScriptSorter(tmp_path)
    code = "import os\n\ndef hello():\n    return 1\n"
    path = sorter.store_script_block(code, project="demo", origin_chat="chat.txt")
    assert path.exists()
    assert "python" in path.parts
    assert "def hello" in path.read_text(encoding="utf-8")


def test_language_bash(tmp_path: Path):
    sorter = DestinyScriptSorter(tmp_path)
    assert sorter._detect_language("#!/bin/bash\necho hi") == "bash"
