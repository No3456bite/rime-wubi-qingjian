#!/usr/bin/env python3
"""Build a Hamster-compatible Rime Wubi86 + Qingjian gloss package (Python 3.10+)."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

QINGJIAN_URL = "https://raw.githubusercontent.com/qingjian-team/qingjian/main/assets/glossary/glossary-en.tsv"
WUBI_URL = "https://raw.githubusercontent.com/rime/rime-wubi/master/wubi86.dict.yaml"
WUBI_LICENSE_URL = "https://raw.githubusercontent.com/rime/rime-wubi/master/LICENSE"
SOURCE_MAX_BYTES = 32 * 1024 * 1024

SCHEMA = '''# Rime Wubi86 with Qingjian candidate English annotation
schema:
  schema_id: wubi86_qj
  name: '五笔86 · 英文释义'
  version: '0.1.0'
  description: '五笔86；中文候选旁离线显示英文'

switches:
  - name: ascii_mode
    reset: 0
    states: [中文, 英文]
  - name: qingjian_en
    reset: 1
    states: [英释关, 英释开]
  - name: full_shape
    states: [半角, 全角]
  - name: ascii_punct
    states: ['，。', '，．']

engine:
  processors:
    - ascii_composer
    - recognizer
    - key_binder
    - speller
    - punctuator
    - selector
    - navigator
    - express_editor
  segmentors:
    - ascii_segmentor
    - matcher
    - abc_segmentor
    - punct_segmentor
    - fallback_segmentor
  translators:
    - punct_translator
    - table_translator
  filters:
    - simplifier@qingjian_en
    - uniquifier

speller:
  alphabet: abcdefghijklmnopqrstuvwxyz
  delimiter: " ;'"

translator:
  dictionary: wubi86_qj
  enable_charset_filter: true
  enable_sentence: true
  enable_encoder: true
  encode_commit_history: true
  max_phrase_length: 4

punctuator:
  import_preset: default
key_binder:
  import_preset: default
recognizer:
  import_preset: default

qingjian_en:
  option_name: qingjian_en
  opencc_config: qingjian_en.json
  show_in_comment: true
  tips: all
  inherit_comment: true
  tags: [abc]
'''

# Standalone installation! Back up the previous default.custom.yaml first.
DEFAULT_CUSTOM = '''# Replaces the earlier schema_list; back up your old default.custom.yaml
patch:
  schema_list:
    - schema: wubi86_qj
'''


def load_source(filename: str | None, url: str, desc: str) -> bytes:
    if filename:
        data = Path(filename).read_bytes()
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "rime-wubi-qingjian/0.1"})
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read(SOURCE_MAX_BYTES + 1)
    if not data or len(data) > SOURCE_MAX_BYTES:
        raise ValueError(f"{desc}: empty or >32 MiB input")
    data.decode("utf-8-sig")
    return data


def gloss_to_opencc(raw: bytes, max_chars: int = 96) -> tuple[bytes, int]:
    """Select the first translation; preserve English phrases with NBSP."""
    mapping: dict[str, str] = {}
    for line in raw.decode("utf-8-sig").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) < 2:
            continue
        key = columns[0].strip()
        gloss = re.sub(r"\s+", " ", columns[1].split("|", 1)[0].strip())
        if not key or not gloss or len(gloss) > max_chars or any(c.isspace() for c in key):
            continue
        mapping.setdefault(key, gloss.replace(" ", "\u00a0"))
    if not mapping:
        raise ValueError("No valid English glosses in Qingjian TSV")
    rendered = "".join(f"{word}\t{mapping[word]}\n" for word in sorted(mapping))
    return rendered.encode("utf-8"), len(mapping)


def rename_wubi_dict(raw: bytes) -> bytes:
    txt = raw.decode("utf-8-sig")
    if "name: wubi86" not in txt or "\n...\n" not in txt:
        raise ValueError("Unexpected official Rime Wubi86 dictionary structure")
    header, rest = txt.split("\n...\n", 1)
    header, count = re.subn(r"(?m)^name:\s*wubi86\s*$", "name: wubi86_qj", header, count=1)
    if count != 1:
        raise ValueError("Failed to isolate Wubi86 dictionary namespace")
    return (header + "\n...\n" + rest).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--glossary", help="Local Qingjian TSV path")
    parser.add_argument("--wubi-dict", help="Local Wubi86 YAML dictionary path")
    parser.add_argument("--wubi-license", help="Local Rime Wubi86 LGPL license path")
    parser.add_argument("--output", default="dist/hamster-wubi86-qingjian.zip")
    parser.add_argument("--no-compile", action="store_true", help="Use text OpenCC dictionary")
    args = parser.parse_args()

    glossary = load_source(args.glossary, QINGJIAN_URL, "Qingjian TSV")
    wubi = load_source(args.wubi_dict, WUBI_URL, "Wubi86 dictionary")
    wubi_license = load_source(args.wubi_license, WUBI_LICENSE_URL, "Wubi86 license")
    text_dict, count = gloss_to_opencc(glossary)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        input_txt = base / "qingjian_en.txt"
        input_txt.write_bytes(text_dict)
        kind, filename, payload = "text", "qingjian_en.txt", text_dict

        if not args.no_compile and shutil.which("opencc_dict"):
            out = base / "qingjian_en.ocd2"
            subprocess.run(
                ["opencc_dict", "-i", str(input_txt), "-o", str(out),
                 "-f", "text", "-t", "ocd2"], check=True)
            if not out.exists() or out.stat().st_size == 0:
                raise RuntimeError("opencc_dict returned an empty result")
            kind, filename, payload = "ocd2", "qingjian_en.ocd2", out.read_bytes()

        config = {
            "name": "Qingjian English gloss for Rime",
            "segmentation": {"type": "mmseg", "dict": {"type": kind, "file": filename}},
            "conversion_chain": [{"dict": {"type": kind, "file": filename}}],
        }
        files = {
            "wubi86_qj.schema.yaml": SCHEMA.encode(),
            "wubi86_qj.dict.yaml": rename_wubi_dict(wubi),
            "default.custom.yaml": DEFAULT_CUSTOM.encode(),
            "opencc/qingjian_en.json":
                (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode(),
            "opencc/" + filename: payload,
            "licenses/QINGJIAN_GPL.txt":
                (Path(__file__).resolve().parents[1] / "LICENSE").read_bytes(),
            "licenses/RIME_WUBI_LGPL.txt": wubi_license,
            "licenses/SOURCES.txt":
                (f"Qingjian: {QINGJIAN_URL}\nLicense: GPL-3.0-or-later\n"
                 f"Rime Wubi86: {WUBI_URL}\nLicense: LGPL-3.0\n").encode(),
        }
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for filename, data in sorted(files.items()):
                z.writestr(filename, data)

    print(f"Built {output}: {count} English glosses; OpenCC {kind}; "
          f"{output.stat().st_size:,} bytes")
    print("ZIP entries: " + ", ".join(sorted(files)))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
