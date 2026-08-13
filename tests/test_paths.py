import sys

from destiny_paths import DestinyPaths


def test_root():
    assert DestinyPaths.root().exists()
    assert (DestinyPaths.root() / "src").exists()


def test_logs():
    logs = DestinyPaths.logs()
    assert logs.name == "logs"
    assert logs.parent == DestinyPaths.root()


def test_archive():
    archive = DestinyPaths.archive()
    assert archive.name == "destiny_archive"


def test_backup():
    assert DestinyPaths.backup().name == "destiny_backups"


def test_is_windows():
    if sys.platform == "win32":
        assert DestinyPaths.is_windows() is True
    else:
        assert DestinyPaths.is_windows() is False


def test_disk_root():
    disk = DestinyPaths.disk_root()
    assert disk
    if DestinyPaths.is_windows():
        assert disk.endswith("\\")
    else:
        assert disk == "/"


def test_has_git():
    assert DestinyPaths.has_git() is True
