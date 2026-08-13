from pathlib import Path

import pytest

from destiny_layer import DestinyLayer, bootstrap_demo_db


@pytest.fixture
def layer(tmp_path: Path) -> DestinyLayer:
    return DestinyLayer(tmp_path / "test.db")


def test_put(layer: DestinyLayer):
    layer.put("test_key", "test_value")
    result = layer.get("test_key")
    assert len(result) >= 1
    assert result[0]["value"] == "test_value"


def test_stats(layer: DestinyLayer):
    layer.put("key1", "value1")
    layer.put("key2", "value2")
    stats = layer.stats()
    assert stats["entries"] >= 2


def test_bootstrap(tmp_path: Path):
    db = tmp_path / "demo.db"
    first = bootstrap_demo_db(db)
    second = bootstrap_demo_db(db)
    assert first.stats()["entries"] == second.stats()["entries"]
    assert first.stats()["entries"] >= 2
