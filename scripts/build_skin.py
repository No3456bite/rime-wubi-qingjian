#!/usr/bin/env python3
"""Build an original, dependency-free Hamster .hskin keyboard theme.

The resulting YAML documents use the JSON subset of YAML 1.2, so they can
be parsed without third-party Python packages.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

LIGHT = {
    "key": "FFFFFF", "pressed": "D5D8DF", "function": "ADB5C0",
    "function_pressed": "919AA8", "ink": "20232B", "muted": "606979",
    "board": "E4E6EB", "border": "C4C7CE", "edge": "9BA1AA",
    "enter": "397DDB", "enter_pressed": "296FC6", "enter_ink": "FFFFFF",
    "comment": "5B6779", "preferred": "161A22", "candidate_bg": "E5EAF2",
}
DARK = {
    "key": "56575F", "pressed": "777982", "function": "3C414C",
    "function_pressed": "555C69", "ink": "F7F7FA", "muted": "BBC1CD",
    "board": "2C2D34", "border": "24252D", "edge": "23242A",
    "enter": "3985E8", "enter_pressed": "2C70CD", "enter_ink": "FFFFFF",
    "comment": "B9C1CF", "preferred": "FFFFFF", "candidate_bg": "3E4857",
}

LETTER_ROWS = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")
NUMERIC_ROWS = (
    "1234567890", "@#$%&*-+()", "!?/:;.,'\"",
)
SYMBOL_ROWS = (
    "[]{}<>^~\\|", "€£¥_=+×÷•", "。，！？：；、",
)

def key(name: str, label: str, action: object, style: str,
        width: float, palette: dict, size: float = 21) -> dict:
    return {
        "size": {"width": {"percentage": width}},
        "backgroundStyle": style + "Background",
        "foregroundStyle": name + "Foreground",
        "action": action,
    }

def row(items: list[tuple[str, float]]) -> dict:
    return {"HStack": {"subviews": [{"Cell": name} for name, _ in items]}}

def make_keyboard(palette: dict, kind: str, landscape: bool = False) -> dict:
    dark = palette is DARK
    result: dict = {
        "preeditHeight": 18 if landscape else 24,
        "toolbarHeight": 40 if landscape else 48,
        "keyboardHeight": 164 if landscape else 224,
        "preedit": {"foregroundStyle": "preeditText", "insets": {"left": 10, "top": 2}},
        "preeditText": {"textColor": palette["muted"], "fontSize": 14, "fontWeight": "medium"},
        "toolbar": {
            "primaryButtonStyle": "toolbarMenu",
            "horizontalCandidateStyle": "horizontalCandidates",
            "verticalCandidateStyle": "verticalCandidates",
        },
        "toolbarMenu": {
            "backgroundStyle": "toolbarButtonBackground",
            "foregroundStyle": "toolbarMenuLabel",
            "action": {"shortcutCommand": "#方案切换"},
        },
        "toolbarButtonBackground": {
            "normalColor": palette["board"], "highlightColor": palette["pressed"],
        },
        "toolbarMenuLabel": {
            "text": "⌘", "normalColor": palette["muted"],
            "fontSize": 16, "fontWeight": "semibold", "center": {"y": 0.60},
        },
        "horizontalCandidates": {
            "insets": {"left": 5, "right": 4},
            "preferredBackgroundColor": palette["candidate_bg"],
            "preferredTextColor": palette["preferred"],
            "preferredCommentColor": palette["comment"],
            "textColor": palette["ink"], "commentColor": palette["comment"],
            "indexColor": palette["muted"], "preferredIndexColor": palette["muted"],
            "highlightBackgroundColor": palette["function"],
            "textFontSize": 18.5, "textFontWeight": "semibold",
            "commentFontSize": 12.5, "commentFontWeight": "medium",
            "indexFontSize": 10, "indexFontWeight": "medium",
            "itemSpacing": 10,
        },
        "verticalCandidates": {
            "candidateStyle": "verticalCandidateItems",
            "bottomRowHeight": 42,
        },
        "verticalCandidateItems": {
            "backgroundColor": palette["board"],
            "separatorColor": palette["border"],
            "preferredTextColor": palette["preferred"],
            "preferredCommentColor": palette["comment"],
            "textColor": palette["ink"], "commentColor": palette["comment"],
            "preferredIndexColor": palette["muted"], "indexColor": palette["muted"],
            "textFontSize": 19, "textFontWeight": "semibold",
            "commentFontSize": 13, "commentFontWeight": "medium",
            "indexFontSize": 11, "indexFontWeight": "medium",
        },
        "letterBackground": {
            "type": "original",
            "insets": {"top": 4, "bottom": 5, "left": 2.5, "right": 2.5},
            "normalColor": palette["key"], "highlightColor": palette["pressed"],
            "cornerRadius": 6.5, "normalLowerEdgeColor": palette["edge"],
        },
        "functionBackground": {
            "type": "original",
            "insets": {"top": 4, "bottom": 5, "left": 2.5, "right": 2.5},
            "normalColor": palette["function"], "highlightColor": palette["function_pressed"],
            "cornerRadius": 6.5, "normalLowerEdgeColor": palette["edge"],
        },
        "spaceBackground": {
            "type": "original",
            "insets": {"top": 4, "bottom": 5, "left": 2.5, "right": 2.5},
            "normalColor": palette["key"], "highlightColor": palette["pressed"],
            "cornerRadius": 6.5, "normalLowerEdgeColor": palette["edge"],
        },
        "enterBackground": {
            "type": "original",
            "insets": {"top": 4, "bottom": 5, "left": 2.5, "right": 2.5},
            "normalColor": palette["enter"], "highlightColor": palette["enter_pressed"],
            "cornerRadius": 6.5, "normalLowerEdgeColor": palette["edge"],
        },
    }
    rows: list[dict] = []
    def add_button(name: str, label: str, action: object, style: str,
                   width: float, font_size: float = 21) -> tuple[str, float]:
        result[name] = key(name, label, action, style, width, palette)
        result[name + "Foreground"] = {
            "text": label,
            "normalColor": palette["enter_ink"] if style == "enter" else palette["ink"],
            "highlightColor": palette["enter_ink"] if style == "enter" else palette["ink"],
            "fontSize": font_size,
            "fontWeight": "semibold" if style in ("letter", "enter") else "medium",
            "center": {"x": 0.5, "y": 0.60 if len(label) <= 1 else 0.62},
        }
        return name, width

    def add_text_row(text: str, row_index: int, width: float, uppercase: bool = False) -> list[tuple[str,float]]:
        result_row = []
        for position, char in enumerate(text):
            label = char.upper() if uppercase else char.lower()
            result_row.append(add_button(
                f"k{row_index}_{position}", label, {"character": char.lower()}
                if kind == "qwerty" else {"symbol": char},
                "letter", width, 21.5 if kind == "qwerty" else 19,
            ))
        return result_row

    if kind == "qwerty":
        rows.append(row(add_text_row(LETTER_ROWS[0], 0, .1, True)))
        items = []
        # Two small transparent outer cells match iPhone's staggered second row.
        result["leftIndent"] = {"size": {"width": {"percentage": .05}}}
        result["rightIndent"] = {"size": {"width": {"percentage": .05}}}
        items.append(("leftIndent", .05))
        items += add_text_row(LETTER_ROWS[1], 1, .1, True)
        items.append(("rightIndent", .05))
        rows.append(row(items))
        items = [add_button("shiftKey", "⇧", "shift", "function", .15, 23)]
        items += add_text_row(LETTER_ROWS[2], 2, .1, True)
        items.append(add_button("deleteKey", "⌫", "backspace", "function", .15, 24))
        rows.append(row(items))
    else:
        texts = NUMERIC_ROWS if kind == "numeric" else SYMBOL_ROWS
        for i, text in enumerate(texts):
            has_delete = i == len(texts) - 1
            width = (0.85 if has_delete else 1.0) / len(text)
            result_row = []
            for j, char in enumerate(text):
                result_row.append(add_button(
                    f"k{i}_{j}", char, {"symbol": char}, "letter", width, 19.5,
                ))
            if has_delete:
                result_row.append(add_button("deleteKey", "⌫", "backspace", "function", .15, 24))
            rows.append(row(result_row))

    # The bottom row retains the essential iOS function keys in every mode.
    bottom = []
    if kind == "qwerty":
        bottom.append(add_button("numbersKey", "123", {"keyboardType": "numeric"}, "function", .17, 15))
        bottom.append(add_button("languageKey", "中/英", {"shortcutCommand": "#中英切换"}, "function", .15, 13))
    elif kind == "numeric":
        bottom.append(add_button("backKey", "ABC", {"keyboardType": "pinyin"}, "function", .17, 15))
        bottom.append(add_button("symbolsKey", "#+=", {"keyboardType": "symbolic"}, "function", .15, 15))
    else:
        bottom.append(add_button("backKey", "ABC", {"keyboardType": "pinyin"}, "function", .17, 15))
        bottom.append(add_button("numbersKey", "123", {"keyboardType": "numeric"}, "function", .15, 15))
    bottom.append(add_button("globeKey", "◎", "nextKeyboard", "function", .11, 21))
    bottom.append(add_button("spaceKey", "空格", "space", "space", .38, 13))
    bottom.append(add_button("enterKey", "↵", "enter", "enter", .19, 23))
    rows.append(row(bottom))
    result["keyboardLayout"] = rows
    return result

def make_manifest() -> dict:
    def locations(key: str) -> dict:
        return {
            "iPhone": {"portrait": key + "_portrait", "landscape": key + "_landscape"},
            "iPad": {
                "portrait": key + "_landscape", "landscape": key + "_landscape",
                "floating": key + "_portrait",
            },
        }
    return {
        "name": "原生·清晰 / Native Clear",
        "author": "rime-wubi-qingjian contributors",
        "pinyin": locations("qwerty"),
        "alphabetic": locations("qwerty"),
        "numeric": locations("numeric"),
        "symbolic": locations("symbolic"),
    }

def serialized(data: dict) -> bytes:
    # JSON is a well-defined YAML 1.2 subset; no parser-sensitive YAML anchors,
    # custom tags, or implicit numbers. Hamster reads these as YAML mappings.
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

def make_files() -> dict[str, bytes]:
    files = {"config.yaml": serialized(make_manifest())}
    for mode, palette in (("light", LIGHT), ("dark", DARK)):
        files[mode + "/resources/"] = b""
        for kind in ("qwerty", "numeric", "symbolic"):
            for orientation in ("portrait", "landscape"):
                name = f"{mode}/{kind}_{orientation}.yaml"
                files[name] = serialized(make_keyboard(palette, kind, orientation == "landscape"))
    return files

def validate(files: dict[str, bytes]) -> None:
    manifest = json.loads(files["config.yaml"])
    assert set(("pinyin", "alphabetic", "numeric", "symbolic")).issubset(manifest)
    for mode in ("light", "dark"):
        for group in ("pinyin", "alphabetic", "numeric", "symbolic"):
            for device, selections in manifest[group].items():
                for orientation, stem in selections.items():
                    path = f"{mode}/{stem}.yaml"
                    assert path in files, path
                    doc = json.loads(files[path])
                    assert len(doc["keyboardLayout"]) == 4
                    assert doc["toolbar"]["horizontalCandidateStyle"] == "horizontalCandidates"
                    assert doc["horizontalCandidates"]["commentFontWeight"] == "medium"
                    for row_def in doc["keyboardLayout"]:
                        refs = [c["Cell"] for c in row_def["HStack"]["subviews"]]
                        for ref in refs:
                            assert ref in doc, (path, ref)
                        sized = [doc[ref]["size"]["width"]["percentage"] for ref in refs]
                        assert abs(sum(sized) - 1) < 1e-6, (path, sum(sized))
                    assert doc["spaceKey"]["action"] == "space"
                    assert doc["enterKey"]["action"] == "enter"
                    assert doc["deleteKey"]["action"] == "backspace"

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--output", default="dist/native-clear-ios.hskin")
    args = p.parse_args()
    files = make_files()
    validate(files)
    if args.check:
        print("PASS skin validation: 12 keyboard configurations + manifest, no unresolved keys")
        return
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
    print(f"Built {output} ({output.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
