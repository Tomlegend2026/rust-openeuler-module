#!/usr/bin/env python3
"""Extract new dmesg lines; fail if the old cursor has been lost to ring wrap."""
import sys
from pathlib import Path


def extract_new(before: str, after: str) -> str:
    old = before.splitlines(keepends=True)
    new = after.splitlines(keepends=True)
    if not old:
        return after
    # Timestamped raw dmesg lines form the boundary. Refuse ambiguous matches.
    marker = old[-min(3, len(old)):]
    positions = [i + len(marker) for i in range(len(new) - len(marker) + 1)
                 if new[i:i + len(marker)] == marker]
    if len(positions) != 1:
        raise ValueError("dmesg boundary lost/ambiguous; preserve raw logs and rerun in a quieter VM")
    return "".join(new[positions[0]:])


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: extract-new-log.py before.log after.log new.log")
    try:
        result = extract_new(Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text())
    except ValueError as error:
        raise SystemExit(str(error))
    Path(sys.argv[3]).write_text(result)
