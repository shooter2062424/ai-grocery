#!/usr/bin/env python3
"""specflow:spec ⇄ code 工作流的命令列工具(只用標準函式庫,Python 3.9+)。

提供「知識庫」的建立、查詢、漂移檢查、變更影響分析、護欄與關卡品質探測。
知識庫就是 repo 內的 Markdown 規格檔加上本工具產生的 ``.specflow/index.json``,
不綁任何資料庫產品;要接向量庫或 MCP 時,只要讀 index.json 即可。

退出碼(兩類紅燈要分開,是本工作流的核心):
    0  全部通過
    1  壞掉了(孤兒標註、規格已變但程式未確認、常數與規格不符、護欄違規…),要修
    3  需要人決定(未解決的 SPEC QUESTION、決策常數被改動),不要自己猜
    2  用法或設定錯誤

子命令: init / index / check / query / impact / stamp / question / guard / contract-diff / mutate
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

# 退出碼
OK, BROKEN, USAGE, NEEDS_HUMAN = 0, 1, 2, 3

ID_RE = r"[A-Z][A-Z0-9]*-[A-Za-z0-9][A-Za-z0-9-]*"
HEAD_RE = re.compile(rf"^(#{{1,6}})\s+({ID_RE})\b\s*[·:\-–—]?\s*(.*)$")
BULLET_RE = re.compile(r"^\s*[-*]\s+([a-z_]+)\s*:\s*(.*?)\s*$")
TAG_RE = re.compile(rf"@(spec|covers)\s+({ID_RE}(?:\s*,\s*{ID_RE})*)")
USES_RE = re.compile(r"@uses\s+([A-Za-z_][\w]*\.[\w.]+(?:\s*,\s*[A-Za-z_][\w]*\.[\w.]+)*)")
CODE_EXT = {".py", ".c", ".h", ".cc", ".cpp", ".hpp", ".cxx", ".java", ".kt", ".go", ".rs", ".js", ".ts", ".tsx",
            ".cs", ".swift", ".rb", ".php", ".scala", ".lua", ".sh", ".sql"}

DEFAULT_CONFIG: dict[str, Any] = {
    "spec_dirs": ["specs"],
    "code_dirs": ["src"],
    "test_dirs": ["tests"],
    "protected": ["tests/golden/**"],
    "contracts": "specs/contracts.json",
    "gates": ["python -m pytest -q"],
    "state_dir": ".specflow",
}


# ----------------------------------------------------------------------------- 基礎

def root_of(path: str | None) -> Path:
    """回傳專案根目錄(含 specflow.json 的資料夾;找不到就用 ``path`` 或目前目錄)。"""
    start = Path(path or os.getcwd()).resolve()
    for p in [start, *start.parents]:
        if (p / "specflow.json").exists():
            return p
    return start


def load_config(root: Path) -> dict[str, Any]:
    """讀 specflow.json 並補上預設值。"""
    cfg = dict(DEFAULT_CONFIG)
    f = root / "specflow.json"
    if f.exists():
        cfg.update(json.loads(f.read_text(encoding="utf-8")))
    return cfg


def sha(text: str) -> str:
    """回傳文字正規化(去行尾空白與空行首尾)後的短 sha1。"""
    norm = "\n".join(line.rstrip() for line in text.strip().splitlines())
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def iter_files(root: Path, dirs: Iterable[str], exts: set[str] | None = None) -> Iterable[Path]:
    """列出 ``dirs`` 底下的檔案(略過隱藏資料夾與 __pycache__)。"""
    for d in dirs:
        base = root / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            parts = set(p.relative_to(root).parts)
            if any(x.startswith(".") or x == "__pycache__" or x == "node_modules" for x in parts):
                continue
            if exts is None or p.suffix.lower() in exts:
                yield p


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


# ----------------------------------------------------------------------------- 解析規格

def parse_specs(root: Path, cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """解析所有 Markdown 規格,回傳 ``{id: 條目}``。

    條目格式:標題 ``## R-XXX-01 · 標題``,其後連續的 ``- key: value`` 為屬性,
    內容到下一個 ID 標題為止。hash 涵蓋標題、屬性與內文。
    """
    reqs: dict[str, dict[str, Any]] = {}
    for f in iter_files(root, cfg["spec_dirs"], {".md"}):
        lines = f.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            m = HEAD_RE.match(lines[i])
            if not m:
                i += 1
                continue
            level, rid, title = len(m.group(1)), m.group(2), m.group(3).strip()
            j = i + 1
            while j < len(lines):
                h = HEAD_RE.match(lines[j])
                if h and len(h.group(1)) <= level:
                    break
                if re.match(r"^#{1,%d}\s" % level, lines[j]) and not HEAD_RE.match(lines[j]):
                    break
                j += 1
            block = lines[i:j]
            attrs: dict[str, str] = {}
            for ln in block[1:]:
                b = BULLET_RE.match(ln)
                if b:
                    attrs[b.group(1)] = b.group(2)
                elif ln.strip() == "":
                    if attrs:
                        break
                else:
                    if attrs:
                        break
            body = "\n".join(block)
            if rid in reqs:
                reqs[rid].setdefault("dups", []).append(f"{rel(root, f)}:{i + 1}")
            else:
                reqs[rid] = {
                    "id": rid, "title": title, "file": rel(root, f), "line": i + 1,
                    "kind": attrs.get("kind", "external" if rid.startswith("R-") else
                                      "decision" if rid.startswith("D-") else
                                      "question" if rid.startswith("Q-") else "internal"),
                    "owner": attrs.get("owner", ""),
                    "status": attrs.get("status", "open" if rid.startswith("Q-") else "active"),
                    "release": attrs.get("release", ""),
                    "depends": [x.strip() for x in attrs.get("depends", "").split(",") if x.strip()],
                    "constants": parse_constants(attrs.get("constants", "")),
                    "refs": [x.strip() for x in attrs.get("refs", "").split(",") if x.strip()],
                    "text": body, "hash": sha(body),
                }
            i = j
    return reqs


def parse_constants(s: str) -> dict[str, str]:
    """把 ``A=1, B=2`` 解成字典;只寫名稱(不含 =)者值為空字串,代表僅受保護、不比對數值。"""
    out: dict[str, str] = {}
    for part in [p.strip() for p in s.split(",") if p.strip()]:
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
        else:
            out[part] = ""
    return out


def scan_tags(root: Path, cfg: dict[str, Any]) -> tuple[dict, dict, dict, dict[str, list[str]]]:
    """掃描程式與測試的追溯標註。

    Returns:
        (code_refs, test_refs, uses, files_without_tag):前三者為 ``{key: ["file:line", ...]}``,
        最後是「有程式但沒有任何 @spec」的檔案清單。
    """
    code: dict[str, list[str]] = {}
    tests: dict[str, list[str]] = {}
    uses: dict[str, list[str]] = {}
    untagged: list[str] = []
    test_dirs = [str(Path(d)) for d in cfg["test_dirs"]]
    for d, bucket, is_code in [(cfg["code_dirs"], code, True), (cfg["test_dirs"], tests, False)]:
        for f in iter_files(root, d, CODE_EXT):
            had = False
            for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for m in TAG_RE.finditer(line):
                    kind = m.group(1)
                    target = tests if (kind == "covers" or not is_code) else code
                    for rid in re.split(r"\s*,\s*", m.group(2)):
                        target.setdefault(rid, []).append(f"{rel(root, f)}:{n}")
                        had = had or (is_code and kind == "spec")
                for m in USES_RE.finditer(line):
                    for key in re.split(r"\s*,\s*", m.group(1)):
                        uses.setdefault(key, []).append(f"{rel(root, f)}:{n}")
            if is_code and not had:
                untagged.append(rel(root, f))
    _ = test_dirs
    return code, tests, uses, {"files": untagged}


def find_constant(root: Path, cfg: dict[str, Any], name: str) -> list[tuple[str, int, str]]:
    """在程式碼中找 ``NAME = VALUE`` / ``NAME: VALUE`` / ``#define NAME VALUE`` 形式的定義。"""
    pat = re.compile(rf"(?:^|[\s;,(])(?:#define\s+)?(?:const\s+|static\s+|final\s+|let\s+|var\s+|constexpr\s+)*"
                     rf"(?:[A-Za-z_][\w:<>\s\*]*\s+)?{re.escape(name)}\s*(?:=|:|\s)\s*([^;,\n#/]+)")
    hits: list[tuple[str, int, str]] = []
    for f in iter_files(root, cfg["code_dirs"], CODE_EXT):
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = pat.search(line)
            if m and re.search(rf"\b{re.escape(name)}\b", line):
                hits.append((rel(root, f), n, m.group(1).strip().rstrip(",;").strip()))
    return hits


def state_dir(root: Path, cfg: dict[str, Any]) -> Path:
    d = root / cfg["state_dir"]
    d.mkdir(exist_ok=True)
    return d


def build_index(root: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    """建立並寫出 ``.specflow/index.json``,同時回傳。"""
    reqs = parse_specs(root, cfg)
    code, tests, uses, extra = scan_tags(root, cfg)
    rev: dict[str, list[str]] = {}
    for rid, r in reqs.items():
        for d in r["depends"]:
            rev.setdefault(d, []).append(rid)
    idx = {"version": 1, "reqs": reqs, "code": code, "tests": tests, "uses": uses,
           "dependents": rev, "untagged_files": extra["files"]}
    (state_dir(root, cfg) / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
    return idx


def load_stamps(root: Path, cfg: dict[str, Any]) -> dict[str, dict[str, str]]:
    f = state_dir(root, cfg) / "stamps.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


# ----------------------------------------------------------------------------- 命令

def cmd_init(a: argparse.Namespace) -> int:
    """建立 specflow.json、specs/、範例規格與 .specflow/。已存在的檔案不覆蓋。"""
    root = Path(a.path or ".").resolve()
    root.mkdir(parents=True, exist_ok=True)
    cfgf = root / "specflow.json"
    if not cfgf.exists():
        cfgf.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    cfg = load_config(root)
    for d in cfg["spec_dirs"]:
        (root / d).mkdir(parents=True, exist_ok=True)
    sample = root / cfg["spec_dirs"][0] / "requirements.md"
    if not sample.exists():
        sample.write_text(
            "# 需求\n\n"
            "## R-DEMO-01 · 範例需求\n"
            "- kind: external\n- owner: team-a\n- status: active\n- constants: DEMO_LIMIT=8\n\n"
            "系統 SHALL 最多處理 DEMO_LIMIT 筆。程式在函式註解寫 `@spec R-DEMO-01`,測試寫 `@covers R-DEMO-01`。\n\n"
            "## D-DEMO-01 · 範例內部決定\n"
            "- kind: decision\n- owner: team-hw\n- status: active\n- depends: R-DEMO-01\n- constants: BUDGET_US\n\n"
            "BUDGET_US 是硬體小組擁有的數字:改動它要 owner 簽核,不得為了讓測試通過自行調整。\n",
            encoding="utf-8")
    state_dir(root, cfg)
    gi = root / ".gitignore"
    print(f"initialized specflow in {root}")
    if gi.exists() and ".specflow/index.json" not in gi.read_text(encoding="utf-8"):
        print("提示: .specflow/index.json 為產生物,可加入 .gitignore;stamps.json 與 specs/ 建議進版控")
    return OK


def cmd_index(a: argparse.Namespace) -> int:
    root = root_of(a.path)
    cfg = load_config(root)
    idx = build_index(root, cfg)
    print(f"indexed: {len(idx['reqs'])} items, {sum(map(len, idx['code'].values()))} code refs, "
          f"{sum(map(len, idx['tests'].values()))} test refs, {len(idx['uses'])} @uses keys")
    return OK


def cmd_check(a: argparse.Namespace) -> int:
    """漂移檢查。回傳 0 / 1(壞掉)/ 3(需人決定)。"""
    root = root_of(a.path)
    cfg = load_config(root)
    idx = build_index(root, cfg)
    reqs, code, tests = idx["reqs"], idx["code"], idx["tests"]
    stamps = load_stamps(root, cfg)
    errors: list[str] = []
    human: list[str] = []
    warns: list[str] = []

    for rid, r in reqs.items():
        for d in r.get("dups", []):
            errors.append(f"DUP-ID {rid} 重複定義於 {d}(首次 {r['file']}:{r['line']})")
        for dep in r["depends"]:
            if dep not in reqs:
                errors.append(f"BAD-DEPENDS {rid} 依賴不存在的 {dep}")
    for rid in code:
        if rid not in reqs:
            errors.append(f"ORPHAN-SPEC-TAG 程式標註 {rid} 但規格中不存在: {code[rid][0]}")
    for rid in tests:
        if rid not in reqs:
            errors.append(f"ORPHAN-COVERS-TAG 測試標註 {rid} 但規格中不存在: {tests[rid][0]}")
    for rid, r in reqs.items():
        if r["kind"] == "question":
            continue
        st = r["status"]
        if st == "deprecated":
            if rid in code:
                warns.append(f"DEPRECATED-IN-USE {rid} 已棄用但仍被程式引用: {code[rid][0]}")
            continue
        if st == "draft":
            continue
        s = stamps.get(rid)
        if rid in code and s is not None and s.get("hash") != r["hash"]:
            errors.append(f"STALE {rid} 規格自上次確認(stamp)後已變更,程式需複查後 stamp: {r['file']}:{r['line']}")
        if rid in code and s is None:
            warns.append(f"UNSTAMPED {rid} 程式已標註但從未 stamp 過")
        if r["kind"] != "decision" and rid not in code:
            warns.append(f"UNIMPLEMENTED {rid} 規格無任何 @spec 程式標註")
        if r["kind"] != "decision" and rid not in tests:
            warns.append(f"UNTESTED {rid} 規格無任何 @covers 測試標註")
        for name, val in r["constants"].items():
            if not val:
                continue
            hits = find_constant(root, cfg, name)
            if not hits:
                errors.append(f"CONST-MISSING {rid} 規格常數 {name}={val},程式中找不到定義")
            for (f, n, v) in hits:
                if _norm_val(v) != _norm_val(val):
                    errors.append(f"CONST-DRIFT {rid} {name}: 規格={val} 程式={v} ({f}:{n})")
    for rid, r in reqs.items():
        if r["kind"] == "question" and r["status"] == "open":
            human.append(f"OPEN-QUESTION {rid} {r['title']} (owner={r['owner'] or '未指定'})")
    # depends 循環
    for cyc in _cycles(reqs):
        errors.append("DEPENDS-CYCLE " + " -> ".join(cyc))
    # 契約欄位被引用但契約檔無此欄位
    cpath = root / cfg["contracts"]
    if cpath.exists():
        contracts = json.loads(cpath.read_text(encoding="utf-8")).get("contracts", {})
        for key, locs in idx["uses"].items():
            c, _, fld = key.partition(".")
            if c not in contracts or (fld and fld.split(".")[0] not in contracts[c].get("fields", {})):
                errors.append(f"UNKNOWN-CONTRACT-USE @uses {key} 在契約檔中不存在: {locs[0]}")
    if a.untagged and idx["untagged_files"]:
        warns.append("UNTAGGED-FILES 以下程式檔沒有任何 @spec: " + ", ".join(idx["untagged_files"]))

    for e in errors:
        print("ERROR ", e)
    for h in human:
        print("HUMAN ", h)
    for w in (warns if a.verbose else warns[:10]):
        print("WARN  ", w)
    if not a.verbose and len(warns) > 10:
        print(f"WARN   …另有 {len(warns) - 10} 筆(--verbose 全列)")
    print(f"summary: {len(errors)} error, {len(human)} needs-human, {len(warns)} warn")
    if a.json:
        print(json.dumps({"errors": errors, "needs_human": human, "warns": warns}, ensure_ascii=False))
    if errors:
        return BROKEN
    if human or (a.strict and warns):
        return NEEDS_HUMAN if human else BROKEN
    return OK


def _norm_val(v: str) -> str:
    return re.sub(r"[\s'\"]", "", v).rstrip("uUlL").lower()


def _cycles(reqs: dict[str, dict[str, Any]]) -> list[list[str]]:
    out: list[list[str]] = []
    state: dict[str, int] = {}
    stack: list[str] = []

    def dfs(n: str) -> None:
        state[n] = 1
        stack.append(n)
        for d in reqs.get(n, {}).get("depends", []):
            if d not in reqs:
                continue
            if state.get(d) == 1:
                out.append(stack[stack.index(d):] + [d])
            elif state.get(d) is None:
                dfs(d)
        stack.pop()
        state[n] = 2

    for n in reqs:
        if state.get(n) is None:
            dfs(n)
    return out


def cmd_query(a: argparse.Namespace) -> int:
    """從知識庫取一條需求的完整脈絡,或用關鍵字找需求。"""
    root = root_of(a.path)
    cfg = load_config(root)
    idx = build_index(root, cfg)
    reqs = idx["reqs"]
    stamps = load_stamps(root, cfg)
    if a.text:
        toks = [t.lower() for t in re.findall(r"\w+", a.text) if len(t) > 1]
        scored = []
        for rid, r in reqs.items():
            low = r["text"].lower()
            sc = sum(low.count(t) for t in toks)
            if sc:
                scored.append((sc, rid))
        for sc, rid in sorted(scored, reverse=True)[:a.top]:
            print(f"{rid}\t{reqs[rid]['title']}\t(score {sc})")
        return OK
    for rid in a.ids:
        r = reqs.get(rid)
        if not r:
            print(f"{rid}: 知識庫中沒有此 ID", file=sys.stderr)
            return USAGE
        s = stamps.get(rid)
        status = "未 stamp" if not s else ("已確認" if s["hash"] == r["hash"] else "STALE(規格已變)")
        print(f"## {rid} {r['title']}  [{r['kind']}/{r['status']}] owner={r['owner'] or '-'} release={r['release'] or '-'}")
        print(f"規格位置: {r['file']}:{r['line']}   程式確認狀態: {status}")
        print(f"依賴: {', '.join(r['depends']) or '-'}   被依賴: {', '.join(idx['dependents'].get(rid, [])) or '-'}")
        print(f"程式: {', '.join(idx['code'].get(rid, [])) or '-'}")
        print(f"測試: {', '.join(idx['tests'].get(rid, [])) or '-'}")
        if r["constants"]:
            print("常數: " + ", ".join(f"{k}={v}" if v else k for k, v in r["constants"].items()))
        print(r["text"])
        print()
    return OK


def impact_of(idx: dict[str, Any], ids: list[str]) -> dict[str, Any]:
    """計算一組變更 ID 的影響範圍(含傳遞依賴)。"""
    reqs = idx["reqs"]
    seen: set[str] = set()
    frontier = list(ids)
    while frontier:
        n = frontier.pop()
        for d in idx["dependents"].get(n, []):
            if d not in seen and d not in ids:
                seen.add(d)
                frontier.append(d)
    affected = list(ids) + sorted(seen)
    code = sorted({loc.split(":")[0] for i in affected for loc in idx["code"].get(i, [])})
    tests = sorted({loc.split(":")[0] for i in affected for loc in idx["tests"].get(i, [])})
    owners = sorted({reqs[i]["owner"] for i in affected if i in reqs and reqs[i]["owner"]})
    decisions = [i for i in affected if i in reqs and reqs[i]["kind"] == "decision"]
    consts = sorted({c for i in affected if i in reqs for c in reqs[i]["constants"]})
    return {"changed": ids, "dependents": sorted(seen), "code_files": code, "test_files": tests,
            "owners": owners, "decisions_to_recheck": decisions, "constants": consts}


def cmd_impact(a: argparse.Namespace) -> int:
    """影響分析。不給 ID 時,以「規格 hash 與 stamp 不同」的條目為變更集。"""
    root = root_of(a.path)
    cfg = load_config(root)
    idx = build_index(root, cfg)
    ids = list(a.ids)
    if not ids:
        stamps = load_stamps(root, cfg)
        ids = [rid for rid, r in idx["reqs"].items()
               if rid in stamps and stamps[rid]["hash"] != r["hash"]]
        ids += [rid for rid in idx["reqs"] if rid not in stamps and rid in idx["code"]]
    bad = [i for i in ids if i not in idx["reqs"]]
    if bad:
        print("未知 ID: " + ", ".join(bad), file=sys.stderr)
        return USAGE
    res = impact_of(idx, ids)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(f"變更項: {', '.join(res['changed']) or '(無)'}")
        print(f"傳遞影響的需求: {', '.join(res['dependents']) or '-'}")
        print(f"需複查的程式檔: {', '.join(res['code_files']) or '-'}")
        print(f"需複查/執行的測試: {', '.join(res['test_files']) or '-'}")
        print(f"需通知的 owner: {', '.join(res['owners']) or '-'}")
        print(f"牽涉的決策項(改前先確認 owner): {', '.join(res['decisions_to_recheck']) or '-'}")
        print(f"相關常數: {', '.join(res['constants']) or '-'}")
    return OK


def cmd_stamp(a: argparse.Namespace) -> int:
    """確認「程式已符合目前規格」:把條目目前 hash 寫入 stamps.json。--all 全部 stamp。"""
    root = root_of(a.path)
    cfg = load_config(root)
    idx = build_index(root, cfg)
    stamps = load_stamps(root, cfg)
    ids = list(idx["reqs"]) if a.all else a.ids
    for rid in ids:
        if rid not in idx["reqs"]:
            print(f"未知 ID {rid}", file=sys.stderr)
            return USAGE
        stamps[rid] = {"hash": idx["reqs"][rid]["hash"], "by": a.by}
    (state_dir(root, cfg) / "stamps.json").write_text(json.dumps(stamps, ensure_ascii=False, indent=1, sort_keys=True),
                                                      encoding="utf-8")
    print(f"stamped {len(ids)} item(s)")
    return OK


def cmd_question(a: argparse.Namespace) -> int:
    """新增一條 SPEC QUESTION(一級產出物:編號、假設、owner、關聯需求)。"""
    root = root_of(a.path)
    cfg = load_config(root)
    reqs = parse_specs(root, cfg)
    nums = [int(m.group(1)) for rid in reqs if (m := re.match(r"Q-(\d+)$", rid))]
    qid = f"Q-{(max(nums) + 1) if nums else 1:03d}"
    f = root / cfg["spec_dirs"][0] / "questions.md"
    head = "" if f.exists() else "# SPEC QUESTION 清單\n\n"
    with f.open("a", encoding="utf-8") as fh:
        fh.write(f"{head}## {qid} · {a.title}\n- kind: question\n- status: open\n- owner: {a.owner}\n"
                 f"- refs: {', '.join(a.refs)}\n\n假設(在人回答前暫用): {a.assume}\n\n")
    print(qid)
    return OK


def _git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git failed")
    return r.stdout


def cmd_guard(a: argparse.Namespace) -> int:
    """護欄:檢查一組變更(預設 = 工作樹對 HEAD)有無違規。

    規則:(1) protected 路徑(凍結的 golden/外部基準)被改且同一變更也改了程式 ⇒ BROKEN;
    (2) 決策項(kind=decision)列出的常數,其定義行在變更中被改 ⇒ NEEDS_HUMAN(要 owner 簽核)。
    """
    root = root_of(a.path)
    cfg = load_config(root)
    idx = build_index(root, cfg)
    try:
        base = a.base or "HEAD"
        files = [x for x in _git(root, "diff", "--name-only", base).splitlines() if x]
        files += [x for x in _git(root, "ls-files", "--others", "--exclude-standard").splitlines() if x]
        diff = _git(root, "diff", "-U0", base)
    except RuntimeError as e:
        print(f"guard 需要 git: {e}", file=sys.stderr)
        return USAGE
    prot = [f for f in files if any(fnmatch.fnmatch(f, pat) for pat in cfg["protected"])]
    code_changed = [f for f in files if any(f.startswith(d.rstrip("/") + "/") for d in cfg["code_dirs"])]
    broken: list[str] = []
    human: list[str] = []
    if prot and code_changed and not a.allow_protected:
        broken.append(f"PROTECTED-CHANGED 凍結基準被修改且同一變更也改了程式: {', '.join(prot)}")
    elif prot and not a.allow_protected:
        human.append(f"PROTECTED-CHANGED 凍結基準被修改(需 owner 簽核): {', '.join(prot)}")
    dec_consts = {c: rid for rid, r in idx["reqs"].items() if r["kind"] == "decision" for c in r["constants"]}
    changed_lines = [ln for ln in diff.splitlines() if ln[:1] in "+-" and ln[:3] not in ("+++", "---")]
    for c, rid in dec_consts.items():
        pat = re.compile(rf"\b{re.escape(c)}\b")
        plus = [ln[1:] for ln in changed_lines if ln[0] == "+" and pat.search(ln)]
        minus = [ln[1:] for ln in changed_lines if ln[0] == "-" and pat.search(ln)]
        if plus or minus:
            human.append(f"DECISION-CONST-CHANGED {rid} 的常數 {c} 被改動(owner={idx['reqs'][rid]['owner'] or '未指定'}),"
                         f"需簽核,不要自行調整讓測試通過")
    for b in broken:
        print("ERROR ", b)
    for h in human:
        print("HUMAN ", h)
    print(f"guard: {len(broken)} error, {len(human)} needs-human, files changed={len(files)}")
    return BROKEN if broken else (NEEDS_HUMAN if human else OK)


# ----------------------------------------------------------------------------- 契約 diff

SEMANTIC_KEYS = ("unit", "scale", "polarity", "base", "default", "encoding")
BOUNDARY_KEYS = ("range", "enum_add")


def classify_contract_change(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, str]]:
    """比較兩份契約檔(``{"contracts": {名稱: {fields: {...}, order: [...], latency_ms: n}}}``)。

    分類:structural(型別/增刪/改名)、semantic(單位/縮放/極性/基底/預設值,型別不變卻會讓 consumer 壞)、
    boundary(範圍放寬、enum 新增)、behavior(順序/延遲)、compatible(只新增選填欄位或文件)。
    """
    out: list[dict[str, str]] = []
    oc, nc = old.get("contracts", {}), new.get("contracts", {})
    for name in sorted(set(oc) | set(nc)):
        if name not in nc:
            out.append({"contract": name, "field": "", "cls": "structural", "what": "契約被移除"})
            continue
        if name not in oc:
            out.append({"contract": name, "field": "", "cls": "compatible", "what": "新增契約"})
            continue
        of, nf = oc[name].get("fields", {}), nc[name].get("fields", {})
        for f in sorted(set(of) | set(nf)):
            if f not in nf:
                out.append({"contract": name, "field": f, "cls": "structural", "what": "欄位被移除(或改名)"})
            elif f not in of:
                req = nf[f].get("required", False)
                out.append({"contract": name, "field": f, "cls": "structural" if req else "compatible",
                            "what": "新增必填欄位" if req else "新增選填欄位"})
            else:
                a, b = of[f], nf[f]
                if a.get("type") != b.get("type"):
                    out.append({"contract": name, "field": f, "cls": "structural",
                                "what": f"型別 {a.get('type')} → {b.get('type')}"})
                for k in SEMANTIC_KEYS:
                    if a.get(k) != b.get(k):
                        out.append({"contract": name, "field": f, "cls": "semantic",
                                    "what": f"{k}: {a.get(k)} → {b.get(k)}(型別不變,schema diff 看不到)"})
                if a.get("range") != b.get("range") and a.get("range") and b.get("range"):
                    lo0, hi0 = a["range"]
                    lo1, hi1 = b["range"]
                    if lo1 < lo0 or hi1 > hi0:
                        out.append({"contract": name, "field": f, "cls": "boundary",
                                    "what": f"範圍放寬 {a['range']} → {b['range']}"})
                    elif (lo1, hi1) != (lo0, hi0):
                        out.append({"contract": name, "field": f, "cls": "compatible",
                                    "what": f"範圍收窄 {a['range']} → {b['range']}"})
                ea, eb = a.get("enum"), b.get("enum")
                if ea is not None and eb is not None and ea != eb:
                    removed = [k for k in ea if k not in eb]
                    renum = [k for k in ea if k in eb and ea[k] != eb[k]]
                    added = [k for k in eb if k not in ea]
                    if removed or renum:
                        out.append({"contract": name, "field": f, "cls": "semantic",
                                    "what": f"enum 值移除/重編號: {removed + renum}"})
                    if added:
                        out.append({"contract": name, "field": f, "cls": "boundary",
                                    "what": f"enum 新增值 {added}(嚴格 consumer 會丟例外)"})
        if oc[name].get("order") != nc[name].get("order") and oc[name].get("order") is not None:
            of_, nf_ = oc[name].get("order"), nc[name].get("order")
            same_set = sorted(map(str, of_)) == sorted(map(str, nf_ or []))
            out.append({"contract": name, "field": "", "cls": "behavior" if same_set else "structural",
                        "what": "欄位/訊息順序改變" if same_set else "位置式欄位集合改變"})
        if oc[name].get("latency_ms") != nc[name].get("latency_ms"):
            out.append({"contract": name, "field": "", "cls": "behavior",
                        "what": f"延遲上限 {oc[name].get('latency_ms')} → {nc[name].get('latency_ms')} ms"})
    return out


ACTION = {
    "structural": "走共存期:新增並存的新欄位/新契約,舊的保留到所有 consumer 遷移完",
    "semantic": "禁止就地改語意:新增帶單位/版本的新欄位並存,consumer 逐一遷移後才移除舊欄位",
    "boundary": "通知受影響 consumer,附邊界案例;consumer 要有 tolerant reader(未知 enum 走預設分支)",
    "behavior": "通知受影響 consumer,補時序/順序測試",
    "compatible": "可自動通過(仍建議 index/check 後 stamp)",
}


def cmd_contract_diff(a: argparse.Namespace) -> int:
    """契約 diff + 以 ``@uses Contract.field`` 標註找出受影響的 consumer。"""
    root = root_of(a.path)
    cfg = load_config(root)
    idx = build_index(root, cfg)
    old = json.loads(Path(a.old).read_text(encoding="utf-8"))
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    changes = classify_contract_change(old, new)
    worst = 0
    order = ["compatible", "behavior", "boundary", "semantic", "structural"]
    for ch in changes:
        key = f"{ch['contract']}.{ch['field']}" if ch["field"] else ch["contract"]
        users = sorted({loc.split(":")[0] for k, locs in idx["uses"].items()
                        if k == key or k.startswith(ch["contract"] + ".") and not ch["field"] for loc in locs})
        ch["consumers"] = users
        ch["action"] = ACTION[ch["cls"]]
        if ch["cls"] != "compatible" and users:
            worst = max(worst, order.index(ch["cls"]))
    if a.json:
        print(json.dumps(changes, ensure_ascii=False, indent=1))
    else:
        for ch in changes:
            tgt = f"{ch['contract']}.{ch['field']}" if ch["field"] else ch["contract"]
            print(f"[{ch['cls']}] {tgt}: {ch['what']}")
            print(f"    consumers: {', '.join(ch['consumers']) or '(manifest 中沒有人 @uses — 可能是動態讀取,需執行期追蹤確認)'}")
            print(f"    action: {ch['action']}")
        if not changes:
            print("契約無差異")
    return NEEDS_HUMAN if any(c["cls"] in ("semantic", "structural", "boundary", "behavior") and c["consumers"]
                              for c in changes) else OK


# ----------------------------------------------------------------------------- 變異探測

MUT_OPS = [
    (re.compile(r"(?<![<>=!])<(?!=)"), "<="), (re.compile(r"<="), "<"),
    (re.compile(r"(?<![<>=!-])>(?![=>])"), ">="), (re.compile(r">="), ">"),
    (re.compile(r"==") , "!="), (re.compile(r"\band\b"), "or"), (re.compile(r"\bor\b"), "and"),
    (re.compile(r"&&"), "||"), (re.compile(r"\|\|"), "&&"),
]
NUM_RE = re.compile(r"(?<![\w.])(\d+)(?![\w.])")


def _mutants(root: Path, cfg: dict[str, Any]) -> list[tuple[str, int, str, str]]:
    """列出可注入的突變 ``(檔案, 行號, 原行, 新行)``;只動程式碼目錄、略過註解與字串標註行。"""
    out: list[tuple[str, int, str, str]] = []
    for f in iter_files(root, cfg["code_dirs"], CODE_EXT):
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            s = line.strip()
            if not s or s.startswith(("#", "//", "/*", "*", '"""', "'''", "import", "from", "def ", "class ")):
                continue
            if "@spec" in line or "print(" in line:
                continue
            for pat, rep in MUT_OPS:
                m = pat.search(line)
                if m:
                    out.append((rel(root, f), n, line, line[:m.start()] + rep + line[m.end():]))
            for m in NUM_RE.finditer(line):
                v = int(m.group(1))
                for nv in {v + 1, max(0, v - 1)} - {v}:
                    out.append((rel(root, f), n, line, line[:m.start()] + str(nv) + line[m.end():]))
    return out


def run_gates(cwd: Path, gates: list[str], timeout: int) -> bool:
    """依序跑關卡指令,全部 exit 0 才回傳 True(= 變異體存活)。

    關卡指令來自使用者自己的 specflow.json / --gate,以 shell 執行(需要 && 與管線);
    不要把不受信任的字串放進 gates。
    """
    for g in gates:
        try:
            r = subprocess.run(g, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False
        if r.returncode != 0:
            return False
    return True


def cmd_mutate(a: argparse.Namespace) -> int:
    """關卡品質探測:在暫存副本注入 N 個隨機突變,看 gates 會不會抓到。存活的突變 = 關卡的盲點。"""
    root = root_of(a.path)
    cfg = load_config(root)
    pool = _mutants(root, cfg)
    if not pool:
        print("找不到可注入的突變點", file=sys.stderr)
        return USAGE
    rnd = random.Random(a.seed)
    rnd.shuffle(pool)
    gates = a.gate or cfg["gates"]
    tmp = Path(tempfile.mkdtemp(prefix="specflow-mut-"))
    work = tmp / "w"
    try:
        shutil.copytree(root, work, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "node_modules"))
        if not run_gates(work, gates, a.timeout):
            print("基線(未突變)關卡就是紅的,先修好再探測", file=sys.stderr)
            return USAGE
        survived, killed = [], 0
        for (f, n, old, new) in pool[:a.n]:
            p = work / f
            txt = p.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            orig = txt[n - 1]
            txt[n - 1] = new + ("\n" if orig.endswith("\n") else "")
            p.write_text("".join(txt), encoding="utf-8")
            alive = run_gates(work, gates, a.timeout)
            txt[n - 1] = orig
            p.write_text("".join(txt), encoding="utf-8")
            if alive:
                survived.append((f, n, old.strip(), new.strip()))
            else:
                killed += 1
        tot = killed + len(survived)
        print(f"mutation: {killed}/{tot} 被關卡抓到 ({100 * killed / max(tot, 1):.0f}%)")
        for f, n, o, nw in survived:
            print(f"SURVIVED {f}:{n}\n    -{o}\n    +{nw}")
        if a.json:
            print(json.dumps({"killed": killed, "total": tot, "survived": survived}, ensure_ascii=False))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return NEEDS_HUMAN if survived else OK


# ----------------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="specflow", description=__doc__.splitlines()[0])
    ap.add_argument("--path", help="專案根目錄(預設往上找 specflow.json)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("init").set_defaults(fn=cmd_init)
    sp.add_parser("index").set_defaults(fn=cmd_index)
    c = sp.add_parser("check")
    c.add_argument("--verbose", action="store_true")
    c.add_argument("--strict", action="store_true", help="警告也視為失敗")
    c.add_argument("--untagged", action="store_true", help="另列出沒有任何 @spec 的程式檔")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_check)
    q = sp.add_parser("query")
    q.add_argument("ids", nargs="*")
    q.add_argument("--text")
    q.add_argument("--top", type=int, default=5)
    q.set_defaults(fn=cmd_query)
    i = sp.add_parser("impact")
    i.add_argument("ids", nargs="*")
    i.add_argument("--json", action="store_true")
    i.set_defaults(fn=cmd_impact)
    s = sp.add_parser("stamp")
    s.add_argument("ids", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--by", default="agent-or-human")
    s.set_defaults(fn=cmd_stamp)
    qq = sp.add_parser("question")
    qq.add_argument("title")
    qq.add_argument("--assume", required=True)
    qq.add_argument("--owner", default="")
    qq.add_argument("--refs", nargs="*", default=[])
    qq.set_defaults(fn=cmd_question)
    g = sp.add_parser("guard")
    g.add_argument("--base")
    g.add_argument("--allow-protected", action="store_true")
    g.set_defaults(fn=cmd_guard)
    cd = sp.add_parser("contract-diff")
    cd.add_argument("old")
    cd.add_argument("new")
    cd.add_argument("--json", action="store_true")
    cd.set_defaults(fn=cmd_contract_diff)
    m = sp.add_parser("mutate")
    m.add_argument("-n", type=int, default=20)
    m.add_argument("--seed", type=int, default=0)
    m.add_argument("--gate", action="append", help="關卡指令(可多次);預設用 specflow.json 的 gates")
    m.add_argument("--timeout", type=int, default=120)
    m.add_argument("--json", action="store_true")
    m.set_defaults(fn=cmd_mutate)
    a = ap.parse_args(argv)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
