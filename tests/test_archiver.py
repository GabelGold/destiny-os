from pathlib import Path

import pytest

from destiny_archiver import DestinyChatSorterPro


@pytest.fixture
def archiver(tmp_path: Path) -> DestinyChatSorterPro:
    return DestinyChatSorterPro(base_dir=tmp_path)


def test_store_chat(archiver: DestinyChatSorterPro):
    chat = "Test Chat [PROJEKT:test]"
    result = archiver.store_chat(chat)
    assert result is not None
    assert result.exists()
    assert result.parent.name == "test"
    assert "Test Chat" in result.read_text(encoding="utf-8")


def test_detect_project(archiver: DestinyChatSorterPro):
    chat = "[PROJEKT:testprojekt] Inhalt"
    project = archiver._detect_project(chat)
    assert "testprojekt" in project


def test_extract_code_blocks(archiver: DestinyChatSorterPro):
    chat = "```python\nprint('hello')\n```"
    blocks = archiver._extract_code_blocks(chat)
    assert len(blocks) == 1
    assert "print" in blocks[0]


def test_empty_chat_raises(archiver: DestinyChatSorterPro):
    with pytest.raises(ValueError):
        archiver.store_chat("   ")


def test_list_projects_and_stats(archiver: DestinyChatSorterPro):
    archiver.store_chat("Hallo [PROJEKT:alpha]")
    archiver.create_project("beta")
    projects = {p["name"]: p for p in archiver.list_projects()}
    assert "alpha" in projects
    assert "beta" in projects
    stats = archiver.stats()
    assert stats["projects"] >= 2
    assert stats["chats"] >= 1


def test_ping_and_repair(archiver: DestinyChatSorterPro):
    assert archiver.ping() is True
    assert archiver.repair() is True
