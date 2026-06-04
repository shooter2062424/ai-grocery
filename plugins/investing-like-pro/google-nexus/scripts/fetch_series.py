#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_series.py — 撈 Nexus 時序預測所需的 context：OHLCV + 基本面 + 近期新聞 + 技術指標。

設計理念：
  這支腳本是「起手式」。Nexus 框架(../references/nexus-framework.md)依 setup 類型該看的訊號不同
  ——循環股多撈稼動率/報價、題材股查訂單/營收佔比、事件型要確認 catalyst 日——AI 應動態擴充。

資料來源：
  - 台股：FinMind 開放 REST API（https://api.finmindtrade.com；部分 dataset 免 token，
    設環境變數 FINMIND_TOKEN 可拉高額度）。撈日 K、本益比/淨值比/殖利率、三大法人。
  - 美股：yfinance（pip install yfinance）。撈日 K、PE/PEG/毛利、市值、近期新聞。

用法：
  python fetch_series.py 2330               # 台股（純數字代號）
  python fetch_series.py NVDA --horizon 10  # 美股
  python fetch_series.py 2330 --json        # 機器可讀

輸出只是「context 資料」；最終預測請交給 AI 套 nexus-framework.md 的 5 階段流程，並附免責聲明。
"""
import os
import sys
import json
import argparse
import statistics
import urllib.request
import datetime as dt

FINMIND = "https://api.finmindtrade.com/api/v4/data"
TOKEN = os.environ.get("FINMIND_TOKEN", "")
UA = {"User-Agent": "Mozilla/5.0"}


def _get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _finmind(dataset, data_id, start_date, end_date=None):
    q = f"dataset={dataset}&data_id={data_id}&start_date={start_date}"
    if end_date:
        q += f"&end_date={end_date}"
    if TOKEN:
        q += f"&token={TOKEN}"
    try:
        d = _get(f"{FINMIND}?{q}")
        return d.get("data", []) if isinstance(d, dict) else []
    except Exception as e:
        return [{"_error": f"{type(e).__name__}: {e}"}]


# ---------- 技術指標 ----------
def _rsi14(closes):
    if len(closes) < 16:
        return None
    diffs = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    up = [max(d, 0) for d in diffs]
    dn = [max(-d, 0) for d in diffs]
    a = 2 / 15
    ru, rd = up[0], dn[0]
    for i in range(1, len(diffs)):
        ru = a * up[i] + (1 - a) * ru
        rd = a * dn[i] + (1 - a) * rd
    return 100.0 if rd == 0 else round(100 - 100 / (1 + ru / rd), 1)


def _atr14(highs, lows, closes):
    if len(closes) < 15:
        return None
    trs = []
    for i in range(1, len(closes)):
        trs.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
    return round(statistics.mean(trs[-14:]), 2)


def _pct(closes, n):
    if len(closes) <= n or closes[-1 - n] == 0:
        return None
    return round((closes[-1] / closes[-1 - n] - 1) * 100, 2)


def _indicators(bars):
    closes = [b["close"] for b in bars if b["close"] is not None]
    highs = [b["high"] for b in bars if b["high"] is not None]
    lows = [b["low"] for b in bars if b["low"] is not None]
    if not closes:
        return {}
    sma20 = round(statistics.mean(closes[-20:]), 2) if len(closes) >= 20 else None
    sma60 = round(statistics.mean(closes[-60:]), 2) if len(closes) >= 60 else None
    return {
        "last_close": closes[-1],
        "rsi14": _rsi14(closes[-60:]) if len(closes) >= 16 else None,
        "atr14": _atr14(highs[-30:], lows[-30:], closes[-30:]),
        "sma20": sma20, "sma60": sma60,
        "vs_sma20_pct": round((closes[-1] / sma20 - 1) * 100, 2) if sma20 else None,
        "pct_1d": _pct(closes, 1), "pct_5d": _pct(closes, 5),
        "pct_1m": _pct(closes, 21), "pct_3m": _pct(closes, 63),
        "hi_90d": max(highs) if highs else None, "lo_90d": min(lows) if lows else None,
    }


# ---------- 台股 ----------
def fetch_tw(code, days=130):
    start = (dt.date.today() - dt.timedelta(days=days * 2)).isoformat()
    px = _finmind("TaiwanStockPrice", code, start)
    bars = [{"date": r["date"], "open": r.get("open"), "high": r.get("max"),
             "low": r.get("min"), "close": r.get("close"), "volume": r.get("Trading_Volume")}
            for r in px if isinstance(r, dict) and "close" in r]
    bars = bars[-130:]
    per = _finmind("TaiwanStockPER", code, (dt.date.today() - dt.timedelta(days=14)).isoformat())
    per_last = per[-1] if per and isinstance(per[-1], dict) and "PER" in per[-1] else {}
    chip = _finmind("TaiwanStockInstitutionalInvestorsBuySell", code,
                    (dt.date.today() - dt.timedelta(days=20)).isoformat())
    return {
        "market": "TW", "ticker": code, "bars": bars,
        "fundamentals": {"PER": per_last.get("PER"), "PBR": per_last.get("PBR"),
                         "dividend_yield": per_last.get("dividend_yield")},
        "chip_flow_recent": chip[-15:] if isinstance(chip, list) else [],
        "news": [],
    }


# ---------- 美股 ----------
def fetch_us(code, days=130):
    try:
        import yfinance as yf
    except ImportError:
        return {"_error": "需要 yfinance：pip install yfinance"}
    t = yf.Ticker(code)
    hist = t.history(period="9mo")
    bars = []
    for idx, row in hist.iterrows():
        bars.append({"date": str(idx.date()), "open": round(float(row["Open"]), 2),
                     "high": round(float(row["High"]), 2), "low": round(float(row["Low"]), 2),
                     "close": round(float(row["Close"]), 2), "volume": int(row["Volume"])})
    bars = bars[-130:]
    info = {}
    try:
        info = t.info
    except Exception:
        pass
    news = []
    try:
        for n in (t.news or [])[:10]:
            c = n.get("content", {}) if isinstance(n, dict) else {}
            news.append({"title": c.get("title") or n.get("title"),
                         "publisher": (c.get("provider") or {}).get("displayName"),
                         "time": c.get("pubDate")})
    except Exception:
        pass
    return {
        "market": "US", "ticker": code, "bars": bars,
        "fundamentals": {"trailing_pe": info.get("trailingPE"), "forward_pe": info.get("forwardPE"),
                         "peg": info.get("pegRatio"), "market_cap": info.get("marketCap"),
                         "gross_margin": info.get("grossMargins"), "beta": info.get("beta"),
                         "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                         "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                         "sector": info.get("sector"), "industry": info.get("industry")},
        "news": news,
    }


def main():
    ap = argparse.ArgumentParser(description="Nexus context 撈取")
    ap.add_argument("ticker")
    ap.add_argument("--horizon", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    code = args.ticker.strip().upper()
    is_tw = code.isdigit()
    data = fetch_tw(code) if is_tw else fetch_us(code)
    if data.get("_error"):
        print(data["_error"], file=sys.stderr)
        sys.exit(1)
    data["horizon"] = args.horizon
    data["indicators"] = _indicators(data["bars"]) if data["bars"] else {}

    if args.json:
        print(json.dumps(data, ensure_ascii=False, default=str))
        return

    ind = data["indicators"]
    print(f"=== {data['market']} {code} | horizon={args.horizon} 交易日 ===")
    print(f"K 線筆數: {len(data['bars'])}（{data['bars'][0]['date']} ~ {data['bars'][-1]['date']}）" if data["bars"] else "無 K 線")
    print(f"現價={ind.get('last_close')} RSI14={ind.get('rsi14')} ATR14={ind.get('atr14')} "
          f"vs20MA={ind.get('vs_sma20_pct')}%")
    print(f"漲跌 1D={ind.get('pct_1d')}% 5D={ind.get('pct_5d')}% 1M={ind.get('pct_1m')}% 3M={ind.get('pct_3m')}%")
    print(f"90日 高={ind.get('hi_90d')} 低={ind.get('lo_90d')}")
    print(f"基本面: {json.dumps(data['fundamentals'], ensure_ascii=False)}")
    if data.get("news"):
        print("近期新聞:")
        for n in data["news"][:8]:
            print(f"  - {n.get('time','')} | {n.get('title','')}")
    if data.get("chip_flow_recent"):
        print(f"三大法人(近 {len(data['chip_flow_recent'])} 筆) 已撈，詳見 --json")
    print("\n[!] 教育性模擬，非投資建議。請套 ../references/nexus-framework.md 的 5 階段流程產出預測。")


if __name__ == "__main__":
    main()
