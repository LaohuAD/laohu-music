"""Regression tests for locked lyrics and structural identity (stdlib only)."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("lyrics_checker", ROOT / "tools/check_controlled_lyrics.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class LockedLyricsTests(unittest.TestCase):
    def test_pure_lyrics_reject_chat_headings_and_false_tags(self):
        for text in ["**［主歌一］**\n旧扇", "[Verse 1]\n旧扇", "[final chorus]\n旧扇", "[chorus ｜ softly]\n旧扇", "[chorus]\n[(softly)]\n旧扇"]:
            with self.subTest(text=text):
                self.assertTrue(checker.validate_pure_lyrics(text))

    def test_pure_lyrics_accept_varied_structure_and_repetition(self):
        for text in ["[verse 1]\n旧扇 春山\n\n[chorus]\n晚安 晚安", "[chorus]\n摇啊摇\n\n[chorus]\n摇啊摇", "[intro]\n\n[verse]\n花落\n\n[interlude]\n\n[outro]\n风过"]:
            self.assertEqual(checker.validate_pure_lyrics(text), [])

    def test_pure_lyrics_reject_empty_unlabelled_and_punctuation(self):
        for text in ["", "[intro]", "旧扇", "[verse]\n你好吗？", "[verse]\n我｜你", "[verse]\n我/你", "[verse]\n男：你好", "[verse]\n旧扇\n\n制作备注：轻唱"]:
            self.assertTrue(checker.validate_pure_lyrics(text))

    def test_pure_lyrics_cli_returns_failure_without_comparison_file(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as folder:
            path = Path(folder) / "lyrics.txt"
            for text, code in [("**［副歌］**\n旧扇", 1), ("[chorus]\n旧扇", 0)]:
                path.write_text(text, encoding="utf-8")
                result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/check_controlled_lyrics.py"), "--lyrics", str(path), "--pure-format", "--json"], capture_output=True, text=True)
                self.assertEqual(result.returncode, code, result.stderr)

    def test_different_sections_are_not_equal(self):
        for a, b in [("Drop", "Breakdown"), ("Refrain", "Hook"), ("Unknown A", "Unknown B")]:
            with self.subTest(a=a, b=b):
                self.assertNotEqual(checker.normalize(f"[{a}]\n啦啦啦"), checker.normalize(f"[{b}]\n啦啦啦"))

    def test_unknown_section_cannot_be_deleted(self):
        self.assertNotEqual(checker.normalize("[Unlisted section]\n啦"), checker.normalize("啦"))

    def test_sections_are_not_counted_as_controls(self):
        self.assertEqual(checker.count_controls("[Drop]\n啦\n[Breakdown]\n啦"), 0)

    def test_unknown_brackets_do_not_prove_controls_present(self):
        self.assertEqual(checker.count_controls("[Unlisted section]\n啦"), 0)

    def test_controls_and_reflow_preserve_lyrics(self):
        locked = "[Verse 1]\n等不到\n看不见\n[Drop]\n啦啦"
        generated = "[Verse 1 ｜ connected]\n[(soft)]\n等不到 看不见\n[Drop ｜ full drums]\n啦啦"
        self.assertEqual(checker.normalize(locked, True), checker.normalize(generated, True))
        self.assertNotEqual(checker.normalize(locked), checker.normalize(generated))

    def test_lyric_punctuation_and_order_are_protected(self):
        locked = "[Verse]\n我爱你。\n[Chorus]\n你爱我"
        for changed in [locked.replace("。", "！"), locked.replace("我爱你", "我恨你"), "[Chorus]\n你爱我\n[Verse]\n我爱你。"]:
            self.assertNotEqual(checker.normalize(locked, True), checker.normalize(changed, True))

    def test_aliases_still_work(self):
        self.assertEqual(checker.normalize("[Pre Chorus 1]\n你"), checker.normalize("[pre-chorus]\n你"))

    def test_cli_fails_on_section_change_without_lint(self):
        # Keep even small task temporaries on the same external work volume.
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as folder:
            a, b = Path(folder) / "locked.txt", Path(folder) / "generated.txt"
            a.write_text("[Drop]\n啦", encoding="utf-8")
            b.write_text("[Breakdown]\n啦", encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/check_controlled_lyrics.py"), "--lyrics", str(a), "--ai-lyrics", str(b)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
