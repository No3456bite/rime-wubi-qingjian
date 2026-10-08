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

# Reference: user screenshot of compact iPhone keyboard, not Apple's assets.
# The very low-alpha board lets iOS' native background blur show through.
LIGHT = {
    "key": "FFFFFF", "pressed": "E6E7EB", "function": "B6BEC9",
    "function_pressed": "A0A9B7", "ink": "222328", "muted": "76777D",
    "board": "D1D5DB03", "border": "BFC3CB", "edge": "8C919A",
    "enter": "B6BEC9", "enter_pressed": "A0A9B7", "enter_ink": "222328",
    "comment": "6B6F78", "preferred": "222328", "candidate_bg": "FFFFFF16",
}
DARK = {
    "key": "4A4A4E", "pressed": "66666A", "function": "58595E",
    "function_pressed": "6B6C71", "ink": "F5F5F7", "muted": "D0D0D5",
    "board": "2C2C2E03", "border": "28282A", "edge": "29292D",
    "enter": "58595E", "enter_pressed": "6B6C71", "enter_ink": "F5F5F7",
    "comment": "C3C4C9", "preferred": "F9F9FC", "candidate_bg": "FFFFFF0C",
}

LETTER_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
EMOJI_ROWS = ("😀😁😂🤣😊🥰😍😘🙂😉", "😭😅😎🤔😴😇🥳🤩😋😢", "👍👏🙏💪❤️🔥🎉✅💯💡")
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
        "preeditHeight": 12 if landscape else 10,
        "toolbarHeight": 27 if landscape else 34,
        "keyboardHeight": 158 if landscape else 200,
        "preedit": {"foregroundStyle": "preeditText", "insets": {"left": 10, "top": 2}},
        "preeditText": {"textColor": palette["muted"], "fontSize": 14, "fontWeight": "medium"},
        "toolbar": {
            "primaryButtonStyle": "toolbarSymbol0",
            "secondaryButtonStyle": ["toolbarSymbol1", "toolbarSymbol2", "toolbarSymbol3",
                                     "toolbarSymbol4", "toolbarSymbol5"],
            "horizontalCandidateStyle": "horizontalCandidates",
            "verticalCandidateStyle": "verticalCandidates",
        },
        "toolbarButtonBackground": {
            "normalColor": "00000000", "highlightColor": "FFFFFF12",
        },
        "horizontalCandidates": {
            "insets": {"left": 5, "right": 4},
            "preferredBackgroundColor": palette["candidate_bg"],
            "preferredTextColor": palette["preferred"],
            "preferredCommentColor": palette["comment"],
            "textColor": palette["ink"], "commentColor": palette["comment"],
            "indexColor": palette["muted"], "preferredIndexColor": palette["muted"],
            "highlightBackgroundColor": palette["function"],
            "textFontSize": 18, "textFontWeight": "medium",
            "commentFontSize": 11.5, "commentFontWeight": "medium",
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
            "textFontSize": 18, "textFontWeight": "medium",
            "commentFontSize": 13, "commentFontWeight": "medium",
            "indexFontSize": 11, "indexFontWeight": "medium",
        },
        "letterBackground": {
            "type": "original",
            "insets": {"top": 5, "bottom": 5, "left": 3, "right": 3},
            "normalColor": palette["key"], "highlightColor": palette["pressed"],
            "cornerRadius": 8.5, "normalLowerEdgeColor": palette["edge"],
        },
        "functionBackground": {
            "type": "original",
            "insets": {"top": 5, "bottom": 5, "left": 3, "right": 3},
            "normalColor": palette["function"], "highlightColor": palette["function_pressed"],
            "cornerRadius": 8.5, "normalLowerEdgeColor": palette["edge"],
        },
        "spaceBackground": {
            "type": "original",
            "insets": {"top": 5, "bottom": 5, "left": 3, "right": 3},
            "normalColor": palette["key"], "highlightColor": palette["pressed"],
            "cornerRadius": 8.5, "normalLowerEdgeColor": palette["edge"],
        },
        "enterBackground": {
            "type": "original",
            "insets": {"top": 5, "bottom": 5, "left": 3, "right": 3},
            "normalColor": palette["enter"], "highlightColor": palette["enter_pressed"],
            "cornerRadius": 8.5, "normalLowerEdgeColor": palette["edge"],
        },
    }
    # Official Hamster v2 layout requires a keyboardStyle entry for the region.
    # Without it, key backgrounds can render over an opaque/default area.
    result["keyboardStyle"] = {"backgroundStyle": "keyboardBackground"}
    result["keyboardBackground"] = {
        "type": "original",
        "normalColor": palette["board"],
        "highlightColor": palette["board"],
    }
    result["toolbar"]["backgroundStyle"] = "keyboardBackground"
    result["preedit"]["backgroundStyle"] = "keyboardBackground"
    # Small native-style punctuation toolbar, replacing the oversized lone ⌘.
    for index, symbol in enumerate(("?", "，", "。", "!", "、", "……")):
        button_name = f"toolbarSymbol{index}"
        result[button_name] = {
            "backgroundStyle": "toolbarButtonBackground",
            "foregroundStyle": button_name + "Text",
            "action": {"symbol": symbol},
        }
        result[button_name + "Text"] = {
            "text": symbol, "normalColor": palette["muted"],
            "highlightColor": palette["ink"], "fontSize": 16,
            "fontWeight": "medium", "center": {"y": 0.53},
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
            "fontWeight": "medium",
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
                "letter", width, 21 if kind == "qwerty" else 18.5,
            ))
        return result_row

    if kind == "qwerty":
        rows.append(row(add_text_row(LETTER_ROWS[0], 0, .1)))
        items = []
        # Two small transparent outer cells match iPhone's staggered second row.
        result["leftIndent"] = {"size": {"width": {"percentage": .05}}}
        result["rightIndent"] = {"size": {"width": {"percentage": .05}}}
        items.append(("leftIndent", .05))
        items += add_text_row(LETTER_ROWS[1], 1, .1)
        items.append(("rightIndent", .05))
        rows.append(row(items))
        items = [add_button("shiftKey", "⇧", "shift", "function", .15, 23)]
        items += add_text_row(LETTER_ROWS[2], 2, .1)
        items.append(add_button("deleteKey", "⌫", "backspace", "function", .15, 24))
        rows.append(row(items))
    else:
        texts = NUMERIC_ROWS if kind == "numeric" else SYMBOL_ROWS if kind == "symbolic" else EMOJI_ROWS
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

    # Screenshot-matched bottom row: compact 123, emoji, wide space, neutral return.
    bottom = []
    if kind == "qwerty":
        bottom.append(add_button("numbersKey", "123", {"keyboardType": "numeric"}, "function", .12, 15))
        bottom.append(add_button("emojiKey", "☺", {"keyboardType": "emoji"}, "function", .12, 20))
    elif kind == "numeric":
        bottom.append(add_button("backKey", "ABC", {"keyboardType": "pinyin"}, "function", .12, 14))
        bottom.append(add_button("symbolsKey", "#+=", {"keyboardType": "symbolic"}, "function", .12, 15))
    elif kind == "symbolic":
        bottom.append(add_button("backKey", "ABC", {"keyboardType": "pinyin"}, "function", .12, 14))
        bottom.append(add_button("numbersKey", "123", {"keyboardType": "numeric"}, "function", .12, 15))
    else:
        bottom.append(add_button("backKey", "ABC", {"keyboardType": "pinyin"}, "function", .12, 14))
        bottom.append(add_button("numbersKey", "123", {"keyboardType": "numeric"}, "function", .12, 15))
    bottom.append(add_button("spaceKey", "", "space", "space", .53, 14))
    bottom.append(add_button("enterKey", "↵", "enter", "enter", .23, 25))
    rows.append(row(bottom))
    # On iPhone the system already provides a globe key below the keyboard.
    # Avoid duplicating it in the Rime-controlled row.
    if kind == "qwerty":
        result["spaceKey"]["foregroundStyle"] = ["spaceKeyForeground", "spaceHint"]
        result["spaceHint"] = {
            "text": "五笔", "normalColor": palette["muted"], "highlightColor": palette["muted"],
            "fontSize": 10.5, "fontWeight": "regular", "center": {"x": .87, "y": .84},
        }
    for ref, sf in (("shiftKey","shift"), ("deleteKey","delete.left"), ("enterKey","return"),
                    ("emojiKey","face.smiling")):
        if ref in result:
            fg = result[ref]["foregroundStyle"]
            result[fg].pop("text", None)
            result[fg]["systemImageName"] = sf
            result[fg]["fontSize"] = 20 if ref != "enterKey" else 22
    if "numbersKey" in result:
        result["numbersKey"]["swipeDownAction"] = {"shortcutCommand": "#RimeSwitcher"}
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
        "emoji": locations("emoji"),
    }

def serialized(data: dict) -> bytes:
    # JSON is a well-defined YAML 1.2 subset; no parser-sensitive YAML anchors,
    # custom tags, or implicit numbers. Hamster reads these as YAML mappings.
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

def make_files() -> dict[str, bytes]:
    files = {"config.yaml": serialized(make_manifest())}
    for mode, palette in (("light", LIGHT), ("dark", DARK)):
        files[mode + "/resources/"] = b""
        for kind in ("qwerty", "numeric", "symbolic", "emoji"):
            for orientation in ("portrait", "landscape"):
                name = f"{mode}/{kind}_{orientation}.yaml"
                files[name] = serialized(make_keyboard(palette, kind, orientation == "landscape"))
    return files

def validate(files: dict[str, bytes]) -> None:
    manifest = json.loads(files["config.yaml"])
    assert set(("pinyin", "alphabetic", "numeric", "symbolic", "emoji")).issubset(manifest)
    for mode in ("light", "dark"):
        for group in ("pinyin", "alphabetic", "numeric", "symbolic", "emoji"):
            for device, selections in manifest[group].items():
                for orientation, stem in selections.items():
                    path = f"{mode}/{stem}.yaml"
                    assert path in files, path
                    doc = json.loads(files[path])
                    assert len(doc["keyboardLayout"]) == 4
                    assert doc["toolbar"]["horizontalCandidateStyle"] == "horizontalCandidates"
                    assert doc["horizontalCandidates"]["commentFontWeight"] == "medium"
                    assert doc["toolbarHeight"] <= 34
                    assert doc["preeditHeight"] <= 12
                    assert doc["keyboardHeight"] <= 200
                    assert doc["keyboardBackground"]["normalColor"].endswith("03")
                    assert doc["enterBackground"]["normalColor"] == doc["functionBackground"]["normalColor"]
                    assert doc["toolbar"]["primaryButtonStyle"] == "toolbarSymbol0"
                    assert len(doc["toolbar"]["secondaryButtonStyle"]) == 5
                    assert "globeKey" not in doc
                    assert doc["k0_0Foreground"]["text"] in ("q", "1", "[", "😀")
                    for row_def in doc["keyboardLayout"]:
                        refs = [c["Cell"] for c in row_def["HStack"]["subviews"]]
                        for ref in refs:
                            assert ref in doc, (path, ref)
                        sized = [doc[ref]["size"]["width"]["percentage"] for ref in refs]
                        assert abs(sum(sized) - 1) < 1e-6, (path, sum(sized))
                    assert doc["spaceKey"]["action"] == "space"
                    assert doc["enterKey"]["action"] == "enter"
                    assert doc["deleteKey"]["action"] == "backspace"
                    assert doc["keyboardStyle"]["backgroundStyle"] in doc
                    assert doc["toolbar"]["backgroundStyle"] in doc
                    assert doc["preedit"]["backgroundStyle"] in doc

def pack(output: Path, files: dict[str, bytes], prefix: str = "") -> None:
    """Make a real .hskin or a folder-wrapped ZIP for manual file-manager imports."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # Include explicit root directories: some iOS ZIP importers don't infer them.
        for dirname in ("light/", "dark/", "light/resources/", "dark/resources/"):
            z.writestr(prefix + dirname, b"")
        if prefix:
            z.writestr(prefix, b"")
        for name, content in files.items():
            if name.endswith("/"):
                continue
            z.writestr(prefix + name, content)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert (prefix + "config.yaml") in z.namelist()
        assert (prefix + "light/qwerty_portrait.yaml") in z.namelist()
        assert (prefix + "dark/qwerty_portrait.yaml") in z.namelist()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--output", default="dist/native-clear-ios.hskin")
    args = p.parse_args()
    files = make_files()
    validate(files)
    if args.check:
        print("PASS skin validation: 16 light/dark/orientation configs, 4 keyboard types, all key references")
        return
    official = Path(args.output)
    # Confirmed from published, working 26键-万象.hskin by BlackCCCat:
    # .hskin root contains ONE named theme directory; config.yaml goes INSIDE it.
    # Earlier flat ZIP variants incorrectly imported light/ and dark/ as themes.
    theme_dir = "native-clear-ios/"
    pack(official, files, theme_dir)
    with zipfile.ZipFile(official) as package:
        members = package.namelist()
        assert all(name.startswith(theme_dir) for name in members)
        assert "config.yaml" not in members
        assert theme_dir + "config.yaml" in members
        assert theme_dir + "dark/qwerty_portrait.yaml" in members
        assert theme_dir + "light/qwerty_portrait.yaml" in members
    print(f"Built {official} ({official.stat().st_size:,} bytes)")
    print("Confirmed: one theme root directory, config.yaml inside it")

if __name__ == "__main__":
    main()
