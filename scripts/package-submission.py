#!/usr/bin/env python3
"""Package Git-visible project files and an integrity manifest, excluding build products."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "build/rust-openeuler-module-submission.zip")
    args = parser.parse_args()
    listing = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    names = sorted(set(name.decode("utf-8") for name in listing.split(b"\0") if name))
    excluded = {".ko", ".o", ".exe", ".pyc", ".zip", ".key", ".pem", ".iso", ".vmdk"}
    files = []
    for name in names:
        path = root / name
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix.lower() in excluded or any(part in {".git", "target", "build", "__pycache__", ".ssh"} for part in path.relative_to(root).parts):
            continue
        if path.name == ".env" or path.name.startswith(".env."):
            continue
        if path.stat().st_size > 32 * 1024 * 1024:
            raise SystemExit(f"Refusing unexpected large file: {name}")
        files.append((name, path.read_bytes()))
    manifest = {"scope": "source, documentation and saved evidence; no VM or kernel binary",
                "files": [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                          for name, data in files]}
    output = args.output.resolve()
    if output == Path(__file__).resolve() or output.is_dir():
        raise SystemExit("Invalid output path")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files:
            archive.writestr("rust-openeuler-module/" + name, data)
        archive.writestr("rust-openeuler-module/SUBMISSION-MANIFEST.json",
                         json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise SystemExit("Archive integrity check failed")
    print(f"Packaged {len(files)} files: {output}")
    print("SHA256: " + hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
