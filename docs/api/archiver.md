# DestinyChatSorterPro

Kanonischer Archiver.

```python
from destiny_archiver import DestinyChatSorterPro

archiver = DestinyChatSorterPro()
path = archiver.store_chat("Chat-Text [PROJEKT:meinprojekt]")
blocks = archiver._extract_code_blocks("```python\nprint('hello')\n```")
print(archiver.list_projects())
print(archiver.stats())
```
