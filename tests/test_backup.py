from pathlib import Path

from destiny_backup_agent import refresh_latest, rotate_backups


def test_rotate_and_latest(tmp_path: Path):
    src = tmp_path / "archive"
    src.mkdir()
    (src / "note.txt").write_text("x", encoding="utf-8")
    backup = tmp_path / "backups"
    for i in range(7):
        d = backup / f"backup_{i}"
        d.mkdir(parents=True)
        (d / "f.txt").write_text(str(i), encoding="utf-8")
    rotate_backups(backup, max_backups=5)
    remaining = list(backup.glob("backup_*"))
    assert len(remaining) == 5
    latest = refresh_latest(src, backup)
    assert latest is not None
    assert (latest / "note.txt").exists()
