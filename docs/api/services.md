# DestinyServiceManager

```python
from destiny_service_manager import DestinyServiceManager

mgr = DestinyServiceManager()
print(mgr.list_all())
mgr.start("monitor")
print(mgr.status("monitor"))
mgr.stop("monitor")
```

Windows nutzt PID-Dateien unter `runtime/services/`. Linux bevorzugt systemd.
