#!/usr/bin/env python3
"""Inspect archive layout of a real, community-published Hamster .hskin."""
import urllib.request, zipfile, io
url = "https://raw.githubusercontent.com/BlackCCCat/ResourceforHamster/main/Skin_Keyboard/%E4%B8%87%E8%B1%A1-%E4%BB%93/26%E9%94%AE-%E4%B8%87%E8%B1%A1.hskin"
req = urllib.request.Request(url, headers={"User-Agent":"rime-wubi-qingjian-skin-probe"})
with urllib.request.urlopen(req, timeout=80) as response:
    body = response.read(8 * 1024 * 1024)
print("reference byte count:", len(body), "signature:", repr(body[:16]))
if not zipfile.is_zipfile(io.BytesIO(body)):
    raise SystemExit("Reference .hskin is not ZIP")
with zipfile.ZipFile(io.BytesIO(body)) as z:
    paths = z.namelist()
    print("first 35 filenames:")
    for p in paths[:35]: print(repr(p))
    print("root entries:", sorted({p.split('/')[0] for p in paths})[:35])
    print("config matches:", [p for p in paths if p.endswith("/config.yaml") or p == "config.yaml"])
    print("has config.yaml at top level:", "config.yaml" in paths)
    print("is root folder wrapped:", len({p.split('/')[0] for p in paths if '/' in p})==1)
