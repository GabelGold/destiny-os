# DestinyLayer

```python
from destiny_layer import DestinyLayer

layer = DestinyLayer("destiny_memory.sqlite")
layer.put("key", "value", kind="note")
data = layer.get("key")
stats = layer.stats()
```

Dünner SQLite-Speicher. Für Tests eine temporäre Datei verwenden.
