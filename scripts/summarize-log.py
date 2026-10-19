#!/usr/bin/env python3
"""Summarize rust_team2 lifecycle lines from a saved dmesg or new.log file."""
import json
import re
import sys
from pathlib import Path

LOADED = re.compile(
    r"event=loaded count=(?P<count>\d+) sum=(?P<sum>\d+) "
    r"min=(?P<min>\d+) max=(?P<max>\d+)"
)
DETAIL = re.compile(r"event=stats_detail average=(?P<average>\d+) range=(?P<range>\d+)")
UNLOAD = re.compile(r"event=unload_begin retained=(?P<retained>\d+) sum=(?P<sum>\d+)")


def summarize(text: str) -> dict:
    loaded = [match.groupdict() for match in LOADED.finditer(text)]
    details = [match.groupdict() for match in DETAIL.finditer(text)]
    unloads = [match.groupdict() for match in UNLOAD.finditer(text)]
    return {
        "loaded_events": len(loaded),
        "stats_detail_events": len(details),
        "unload_events": len(unloads),
        "statistics": {key: int(value) for key, value in loaded[-1].items()} if loaded else None,
        "extended_statistics": {
            key: int(value) for key, value in details[-1].items()
        } if details else None,
        "last_unload": {key: int(value) for key, value in unloads[-1].items()} if unloads else None,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: summarize-log.py NEW_LOG_OR_EVIDENCE_DIRECTORY", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if path.is_dir():
        path /= "new.log"
    try:
        result = summarize(path.read_text(encoding="utf-8"))
    except OSError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
