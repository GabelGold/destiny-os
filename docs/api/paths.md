# DestinyPaths

```python
from destiny_paths import DestinyPaths

root = DestinyPaths.root()
logs = DestinyPaths.logs()
archive = DestinyPaths.archive()
backup = DestinyPaths.backup()

if DestinyPaths.is_windows():
    print("Windows", DestinyPaths.disk_root())
else:
    print("Linux", DestinyPaths.disk_root())
```

Alle Pfade sind relativ zum Projektroot oder zum Benutzerprofil. Keine hardcodierten `/home/...`-Pfade.
