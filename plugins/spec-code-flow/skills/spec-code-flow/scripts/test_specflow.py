"""specflow 的自我測試(unittest,零依賴):契約變更分類表、規格解析、check 的基本行為。

執行: python test_specflow.py
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import specflow as S  # noqa: E402

BASE = {"contracts": {"M": {"order": ["a", "b"], "latency_ms": 10, "fields": {
    "a": {"type": "int", "unit": "ms", "range": [0, 100], "default": 0},
    "b": {"type": "int", "scale": 0.5, "polarity": "1=on", "base": 0, "enum": {"X": 0, "Y": 1}},
}}}}


def mut(fn):
    d = copy.deepcopy(BASE)
    fn(d["contracts"]["M"])
    return d


# (名稱, 變更函式, 預期類別集合)
CASES = [
    ("移除欄位", lambda m: m["fields"].pop("b"), {"structural"}),
    ("型別改變", lambda m: m["fields"]["a"].update(type="str"), {"structural"}),
    ("新增必填欄位", lambda m: m["fields"].update(c={"type": "int", "required": True}), {"structural"}),
    ("新增選填欄位", lambda m: m["fields"].update(c={"type": "int"}), {"compatible"}),
    ("單位 ms→us", lambda m: m["fields"]["a"].update(unit="us"), {"semantic"}),
    ("縮放改變", lambda m: m["fields"]["b"].update(scale=0.25), {"semantic"}),
    ("極性反轉", lambda m: m["fields"]["b"].update(polarity="0=on"), {"semantic"}),
    ("索引基底", lambda m: m["fields"]["b"].update(base=1), {"semantic"}),
    ("預設值改變", lambda m: m["fields"]["a"].update(default=5), {"semantic"}),
    ("範圍放寬", lambda m: m["fields"]["a"].update(range=[0, 200]), {"boundary"}),
    ("範圍收窄", lambda m: m["fields"]["a"].update(range=[0, 50]), {"compatible"}),
    ("enum 新增值", lambda m: m["fields"]["b"]["enum"].update(Z=2), {"boundary"}),
    ("enum 重編號", lambda m: m["fields"]["b"].update(enum={"X": 1, "Y": 0}), {"semantic"}),
    ("enum 移除值", lambda m: m["fields"]["b"].update(enum={"X": 0}), {"semantic"}),
    ("欄位順序改變", lambda m: m.update(order=["b", "a"]), {"behavior"}),
    ("延遲上限改變", lambda m: m.update(latency_ms=50), {"behavior"}),
    ("純文件變更(無屬性差異)", lambda m: None, set()),
]


class ContractClassify(unittest.TestCase):
    def test_table(self) -> None:
        for name, fn, want in CASES:
            got = {c["cls"] for c in S.classify_contract_change(BASE, mut(fn))}
            self.assertEqual(got, want, name)


class CheckBasics(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "specs").mkdir()
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "specs" / "r.md").write_text(
            "## R-A-01 · 上限\n- kind: external\n- owner: t\n- constants: LIMIT=8\n\nSHALL ≤ LIMIT。\n", encoding="utf-8")
        (self.root / "src" / "a.py").write_text("LIMIT = 8\n\ndef f(x):\n    # @spec R-A-01\n    return x <= LIMIT\n", encoding="utf-8")
        (self.root / "tests" / "t.py").write_text("# @covers R-A-01\n", encoding="utf-8")
        (self.root / "specflow.json").write_text(json.dumps({"gates": []}), encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_sf(self, *args: str) -> tuple[int, str]:
        r = subprocess.run([sys.executable, str(HERE / "specflow.py"), "--path", str(self.root), *args],
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout + r.stderr

    def test_clean_after_stamp(self) -> None:
        self.assertEqual(self.run_sf("stamp", "--all")[0], 0)
        self.assertEqual(self.run_sf("check")[0], 0)

    def test_const_drift_is_broken(self) -> None:
        self.run_sf("stamp", "--all")
        (self.root / "src" / "a.py").write_text("LIMIT = 9\n\ndef f(x):\n    # @spec R-A-01\n    return x <= LIMIT\n", encoding="utf-8")
        code, out = self.run_sf("check")
        self.assertEqual(code, 1)
        self.assertIn("CONST-DRIFT", out)

    def test_stale_after_spec_edit(self) -> None:
        self.run_sf("stamp", "--all")
        p = self.root / "specs" / "r.md"
        p.write_text(p.read_text(encoding="utf-8").replace("SHALL", "SHALL NOT"), encoding="utf-8")
        code, out = self.run_sf("check")
        self.assertEqual(code, 1)
        self.assertIn("STALE", out)

    def test_open_question_is_needs_human_not_broken(self) -> None:
        self.run_sf("stamp", "--all")
        self.assertEqual(self.run_sf("question", "含糊", "--assume", "A", "--refs", "R-A-01")[0], 0)
        code, out = self.run_sf("check")
        self.assertEqual(code, 3, out)

    def test_orphan_tag(self) -> None:
        self.run_sf("stamp", "--all")
        (self.root / "src" / "b.py").write_text("# @spec R-ZZ-99\n", encoding="utf-8")
        code, out = self.run_sf("check")
        self.assertEqual(code, 1)
        self.assertIn("ORPHAN-SPEC-TAG", out)


if __name__ == "__main__":
    unittest.main()
