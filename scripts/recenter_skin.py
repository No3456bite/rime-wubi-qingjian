#!/usr/bin/env python3
"""Fix letter and bottom-key label alignment in an existing Hamster .hskin.

Requires a v5-compatible package with one top-level skin folder. Does not
change the Rime input scheme, key action, key sizes, theme colors, or layout.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

LETTER = re.compile(r"^r[012]_\d+Foreground$")
TEXT_EXTRA = frozenset({
    "numbersKeyForeground", "commaKeyForeground", "periodKeyForeground",
    "abcKeyForeground", "backKeyForeground", "switchKeyForeground",
    "symbolsKeyForeground",
})

def recenter(document: dict) -> tuple[int, int]:
    letters = others = 0
    for key, value in document.items():
        if not isinstance(value, dict) or not isinstance(value.get("center"), dict):
            continue
        if LETTER.fullmatch(key):
            value["center"]["y"] = 0.80
            letters += 1
        elif key in TEXT_EXTRA:
            value["center"]["y"] = 0.78
            others += 1
    return letters, others

def transform(source: Path, output: Path) -> None:
    if source.resolve() == output.resolve():
        raise ValueError("Input and output must differ")
    layouts = letters = others = 0
    with ZipFile(source) as original, ZipFile(output, "w", compression=ZIP_DEFLATED) as result:
        files = original.namelist()
        roots = {name.split("/")[0] for name in files if name.strip("/")}
        if len(roots) != 1 or next(iter(roots)) + "/config.yaml" not in files:
            raise ValueError("A single skin directory containing config.yaml is required")
        root = next(iter(roots))
        if root != "native-clear-ios-v5":
            raise ValueError("This v6 patch expects the native-clear-ios-v5 skin")
        for entry in original.infolist():
            content = original.read(entry.filename)
            if entry.filename.endswith(".yaml") and (
                "/light/" in entry.filename or "/dark/" in entry.filename
            ):
                document = json.loads(content)
                lc, oc = recenter(document)
                if lc:
                    layouts += 1
                    letters += lc
                others += oc
                content = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode()
            if entry.filename == root + "/config.yaml":
                manifest = json.loads(content)
                manifest["name"] = "原生·清晰 v6 / Native Clear v6"
                content = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
            destination = entry.filename.replace(root + "/", "native-clear-ios-v6/", 1)
            result.writestr(destination, content)
    with ZipFile(output) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP archive integrity check failed")
    if layouts != 4 or letters != 104 or others != 48:
        raise ValueError(f"Unexpected patch coverage: {layouts} layouts, {letters} letters, {others} labels")
    print(f"PASS {layouts} QWERTY layouts / {letters} letter labels / {others} function labels")
    print(f"Written: {output}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    transform(args.input, args.output)

if __name__ == "__main__":
    main()
