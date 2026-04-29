from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel


class SpedRecord(BaseModel):
    REG: str


def stream_lines(path: Path) -> Iterator[list[str]]:
    """Yield SPED record fields (split by '|') for each valid record line.

    Skip non-record lines (certificate ICP-Brasil at end). Encoding ISO-8859-1.
    """
    with path.open("r", encoding="iso-8859-1") as f:
        for line in f:
            if not line.startswith("|"):
                continue
            yield line.strip().strip("|").split("|")


def detect_layout_version(path: Path) -> str | None:
    """Read first record (0000) and return its cod_ver field."""
    for parts in stream_lines(path):
        if parts[0] == "0000":
            return parts[1] if len(parts) > 1 else None
    return None


class UnsupportedLayoutError(Exception):
    pass
