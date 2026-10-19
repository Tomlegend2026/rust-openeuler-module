#!/usr/bin/env python3
"""Audit saved lifecycle evidence; this does not run or load a kernel module."""
import argparse
import csv
import importlib.util
import json
import re
from pathlib import Path

spec = importlib.util.spec_from_file_location("extract_log", Path(__file__).with_name("extract-new-log.py"))
extract_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract_log)


def audit(run: Path, rounds: int = 10) -> dict:
    if rounds < 1:
        raise ValueError("rounds must be positive")
    required = ("before.log", "after.log", "new.log", "final.log", "rounds.tsv", "result.txt", "commands.log")
    for name in required:
        if not (run / name).is_file():
            raise ValueError(f"missing evidence: {name}")
    if (run / "result.txt").read_text(encoding="utf-8").strip() != "EXIT_STATUS=0":
        raise ValueError("lifecycle command did not report success")
    with (run / "rounds.tsv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if len(rows) != rounds:
        raise ValueError(f"expected {rounds} rounds, found {len(rows)}")
    for number, row in enumerate(rows, 1):
        expected = {"round": str(number), "load": "0", "listed_after_load": "yes",
                    "unload": "0", "absent_after_unload": "yes"}
        if row != expected:
            raise ValueError(f"invalid lifecycle row {number}")
    incremental = extract_log.extract_new((run / "before.log").read_text(encoding="utf-8"), (run / "after.log").read_text(encoding="utf-8"))
    if incremental != (run / "new.log").read_text(encoding="utf-8"):
        raise ValueError("new.log does not match raw log boundary")
    loads = incremental.count("[rust_team2] event=loaded count=6 sum=23 min=1 max=9")
    unloads = incremental.count("[rust_team2] event=unload_begin retained=6 sum=23")
    if (loads, unloads) != (rounds, rounds):
        raise ValueError(f"unexpected load/unload log counts: {loads}/{unloads}")
    details = incremental.count("[rust_team2] event=stats_detail average=3 range=8")
    if details not in (0, rounds):
        raise ValueError(f"unexpected extended-stat log count: {details}")
    if re.search(r"BUG:|Oops:|WARNING:|kernel panic", incremental, re.I):
        raise ValueError("new warning/error requires manual review")
    return {"status": "PASS", "rounds": rounds, "loads": loads, "unloads": unloads,
            "extended_stats": details,
            "evidence": str(run), "scope": "saved evidence audit, not a new kernel run"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--rounds", type=int, default=10)
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.run, args.rounds), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
