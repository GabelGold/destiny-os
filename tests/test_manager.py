from destiny_manager import DestinyManager


def test_initialize():
    mgr = DestinyManager()
    result = mgr.initialize()
    assert result.get("system") == "initialized"


def test_health_check():
    mgr = DestinyManager()
    result = mgr.health_check()
    assert result.get("status") in ["healthy", "recovered"]


def test_status_includes_services():
    mgr = DestinyManager()
    snap = mgr.status()
    assert "services" in snap
    assert "core" in snap["services"]
