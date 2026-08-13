# DestinyManager

```python
from destiny_manager import DestinyManager

mgr = DestinyManager()
mgr.initialize()
status = mgr.health_check()
mgr.archive_chat("text")
print(mgr.status())
```

Orchestriert Provisioner und Archiver. `status()` liefert den Service-Snapshot.
