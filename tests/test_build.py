import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build import SCHEMA, gloss_to_opencc, main, rename_wubi_dict


class BuildTests(unittest.TestCase):
    def test_gloss_first_translation_and_nbsp(self):
        raw = "苹果\tn. apple\n机器学习\tn. machine learning\n开发\tv. develop\tdevelopment\n坏行\n".encode()
        out, count = gloss_to_opencc(raw)
        self.assertEqual(count, 3)
        self.assertIn("机器学习\tn.\u00a0machine\u00a0learning\n", out.decode())
        self.assertIn("开发\tv.\u00a0develop\n", out.decode())
        self.assertNotIn("坏行\n", out.decode())

    def test_isolated_wubi_namespace(self):
        raw = "---\nname: wubi86\nversion: '0.7'\n...\n苹果\tagjs\t100\n".encode()
        out = rename_wubi_dict(raw).decode()
        self.assertIn("name: wubi86_qj", out)
        self.assertIn("苹果\tagjs\t100", out)

    def test_filter_and_switch(self):
        for field in ["simplifier@qingjian_en", "show_in_comment: true",
                      "option_name: qingjian_en", "dictionary: wubi86_qj"]:
            self.assertIn(field, SCHEMA)

    def test_build_zip_with_offline_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "gloss.tsv").write_text("苹果\tn. apple\n编程\tn. programming\n", encoding="utf8")
            (p / "dict.yaml").write_text(
                "---\nname: wubi86\nversion: '0.7'\n...\n苹果\tagjs\t100\n", encoding="utf8")
            (p / "wubi_license.txt").write_text("test license only", encoding="utf8")
            output = p / "output.zip"
            args = ["build.py", "--glossary", str(p / "gloss.tsv"),
                    "--wubi-dict", str(p / "dict.yaml"),
                    "--wubi-license", str(p / "wubi_license.txt"),
                    "--no-compile", "--output", str(output)]
            with patch.object(sys, "argv", args):
                main()
            with zipfile.ZipFile(output) as z:
                names = z.namelist()
                self.assertIn("wubi86_qj.schema.yaml", names)
                self.assertIn("wubi86_qj.dict.yaml", names)
                self.assertIn("default.custom.yaml", names)
                self.assertIn("opencc/qingjian_en.txt", names)
                self.assertIn("opencc/qingjian_en.json", names)
                self.assertFalse(any(x.startswith("package/") for x in names))
                self.assertEqual(z.read("opencc/qingjian_en.json").decode().count("qingjian_en.txt"), 2)


if __name__ == "__main__":
    unittest.main()
