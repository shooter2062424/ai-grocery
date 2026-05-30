#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_response.py — 解析中國信託證券交易 API 的回傳字串。

一般回傳格式:
  <rc=#|cookie=#|err=#|msg=#|count=#><F0=..|F1=..|...><F0=..|...>...
帳號格式:
  <ID=..|Name=..|UID=..|Type=..|...><...>
特殊字元跳脫(需還原):& <amp;>  < <lt;>  > <gt;>  | <bar;>  = <equ;>

用法:
  from parse_response import parse_general, parse_records, unescape
  head, records = parse_general(result_str)   # head: dict, records: list[dict]
  accounts = parse_records(account_list_str)   # list[dict]
"""
import re

_UNESCAPE = [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&bar;", "|"), ("&equ;", "=")]


def unescape(s: str) -> str:
    for a, b in _UNESCAPE:
        s = s.replace(a, b)
    return s


def _kv(block: str) -> dict:
    """把 'F0=..|F1=..' 或 'ID=..|Name=..' 解析成 dict(值會 unescape)。"""
    d = {}
    for field in block.split("|"):
        if "=" in field:
            k, v = field.split("=", 1)
            d[k.strip()] = unescape(v)
    return d


def parse_records(s: str) -> list:
    """抓出所有 <...> 區塊各自解析成 dict。適用帳號清單或純 record 串。"""
    return [_kv(m) for m in re.findall(r"<([^<>]*)>", s or "")]


def parse_general(s: str):
    """解析一般回傳:回傳 (head_dict, list_of_record_dicts)。
    head 含 rc/cookie/err/msg/count;records 是後續每個 <F0=..> 區塊。"""
    blocks = re.findall(r"<([^<>]*)>", s or "")
    if not blocks:
        return {}, []
    head = _kv(blocks[0])
    records = [_kv(b) for b in blocks[1:]]
    return head, records


if __name__ == "__main__":
    # 自我測試
    demo = ("<rc=1|cookie=12|err=0|msg=|count=1>"
            "<F0=20601-0101093|F1=20110408|F5=1108|F7=7.38|F8=1000|F14=委託成功>")
    head, recs = parse_general(demo)
    print("head:", head)
    print("records:", recs)
    acc = "<ID=79Z-1234567|Name=證-陳XX|UID=A123456789|Type=1|Credit=1|CanHedge=2>"
    print("accounts:", parse_records(acc))
