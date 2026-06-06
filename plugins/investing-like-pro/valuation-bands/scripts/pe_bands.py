#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pe_bands.py — 用「該股歷史本益比(PE)分位 × EPS」算出五檔價:特價/便宜/合理/昂貴/瘋狂,並判斷現價落在哪一檔。

方法論(孫慶龍式「固定本益比情境分析」):
  1. 取該股「自己」過去 N 年的 PE 分布,算分位當五個倍數:
       特價=P10、便宜=P25、合理(中位)=P50、昂貴=P75、瘋狂=P90
  2. 五檔價 = EPS × 各檔 PE。EPS 優先用使用者給的「預估(forward)EPS」;沒給就用 TTM EPS 當保守代理(會標明)。
  3. 看「現價 / 現在 PE」落在哪一檔 → 特價/便宜/合理/昂貴/瘋狂。

資料來源:
  - 台股(純數字代號):FinMind 開放 API(免 token;設環境變數 FINMIND_TOKEN 可拉高額度)。
      TaiwanStockPER(歷史 PER/PBR/殖利率)、TaiwanStockPrice(收盤價)。
  - 美股(英文代號):yfinance。用「近 N 年股價 / TTM EPS」近似歷史 PE 分布;trailing/forward EPS 取自 info。

用法:
  python pe_bands.py 2330                 # 台股,用 TTM EPS 當代理
  python pe_bands.py 2330 --eps 135       # 指定預估 EPS(例:孫慶龍估台積電 2029 EPS 135)
  python pe_bands.py NVDA --years 5       # 美股
  python pe_bands.py 2330 --json          # 機器可讀

⚠️ 教育性工具,非投資建議。分位是「相對自己歷史」的便宜/貴,不代表絕對價值;EPS 預估含假設、可能有誤。
"""
import os, sys, json, argparse, datetime, urllib.request, urllib.parse

FINMIND = "https://api.finmindtrade.com/api/v4/data"
TOKEN = os.environ.get("FINMIND_TOKEN", "")
LEVELS = [("特價", 10), ("便宜", 25), ("合理", 50), ("昂貴", 75), ("瘋狂", 90)]


def _get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def finmind(dataset, data_id, start_date):
    q = {"dataset": dataset, "data_id": data_id, "start_date": start_date}
    if TOKEN:
        q["token"] = TOKEN
    d = _get(FINMIND + "?" + urllib.parse.urlencode(q))
    if d.get("status") != 200:
        raise RuntimeError(f"{dataset}: {d.get('msg')}")
    return d.get("data", [])


def percentile(sorted_vals, pct):
    """線性插值百分位(pct 為 0-100)。"""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = k - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def years_ago(years):
    t = datetime.date.today()
    try:
        return t.replace(year=t.year - years).isoformat()
    except ValueError:
        return t.replace(year=t.year - years, day=28).isoformat()


def classify(current_pe, bands):
    """bands: dict 等級->PE。回傳現價的等級判定。"""
    if current_pe is None:
        return "無法判定(缺現價 PE)"
    if current_pe <= bands["特價"]:
        return "特價"
    if current_pe <= bands["便宜"]:
        return "便宜"
    if current_pe <= bands["昂貴"]:   # 介於 便宜(P25) 與 昂貴(P75) 之間視為「合理」
        return "合理"
    if current_pe <= bands["瘋狂"]:
        return "昂貴"
    return "瘋狂"


def build(per_series, current_pe, current_price, eps, eps_kind, years, market, extra):
    pes = sorted(p for p in per_series if p and p > 0)
    if len(pes) < 20:
        raise RuntimeError(f"PE 樣本太少({len(pes)} 筆),無法可靠估分位")
    bands = {name: round(percentile(pes, pct), 2) for name, pct in LEVELS}
    rows = []
    for name, pct in LEVELS:
        pe = bands[name]
        rows.append({"level": name, "percentile": pct, "pe": pe,
                     "price": round(eps * pe, 2) if eps else None})
    verdict = classify(current_pe, bands)
    return {
        "market": market, "years": years,
        "eps": eps, "eps_kind": eps_kind,
        "current_price": current_price, "current_pe": round(current_pe, 2) if current_pe else None,
        "pe_sample": len(pes),
        "pe_low": round(min(pes), 2), "pe_high": round(max(pes), 2),
        "bands": rows, "verdict": verdict, **extra,
    }


def fetch_tw(stock_id, eps_override, years):
    per = finmind("TaiwanStockPER", stock_id, years_ago(years))
    per = [r for r in per if r.get("PER")]
    if not per:
        raise RuntimeError("查無 PER 歷史(代號是否正確?)")
    per.sort(key=lambda x: x.get("date", ""))
    series = [r["PER"] for r in per]
    current_pe = per[-1]["PER"]
    # 現價
    current_price = None
    try:
        px = finmind("TaiwanStockPrice", stock_id, years_ago(0) if False else
                     (datetime.date.today() - datetime.timedelta(days=10)).isoformat())
        px = [r for r in px if r.get("close")]
        if px:
            px.sort(key=lambda x: x.get("date", ""))
            current_price = px[-1]["close"]
    except Exception:
        pass
    # TTM EPS = 現價 / 現在 PE(隱含),作為沒指定預估 EPS 時的代理
    ttm_eps = round(current_price / current_pe, 2) if (current_price and current_pe) else None
    eps = eps_override if eps_override else ttm_eps
    eps_kind = "使用者預估(forward)" if eps_override else "TTM 代理(現價/現PE)"
    return build(series, current_pe, current_price, eps, eps_kind, years, "TW",
                 {"implied_ttm_eps": ttm_eps})


def fetch_us(ticker, eps_override, years):
    try:
        import yfinance as yf
    except ImportError:
        raise RuntimeError("未安裝 yfinance(pip install yfinance),無法取美股")
    t = yf.Ticker(ticker)
    info = t.info
    eps_ttm = info.get("trailingEps")
    eps_fwd = info.get("forwardEps")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    # 用「近 N 年股價 / TTM EPS」近似歷史 PE 分布
    series = []
    if eps_ttm and eps_ttm > 0:
        hist = t.history(period=f"{years}y")
        series = [float(c) / eps_ttm for c in hist["Close"].tolist() if c and c > 0]
    current_pe = info.get("trailingPE") or (current_price / eps_ttm if (current_price and eps_ttm) else None)
    eps = eps_override if eps_override else (eps_fwd or eps_ttm)
    eps_kind = ("使用者預估(forward)" if eps_override else
                ("forwardEps" if eps_fwd else "trailingEps(TTM)"))
    return build(series, current_pe, current_price, eps, eps_kind, years, "US",
                 {"trailing_eps": eps_ttm, "forward_eps": eps_fwd,
                  "note": "美股 PE 分布以『股價/TTM EPS』近似,僅供參考"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stock", help="台股純數字代號(2330)或美股英文代號(NVDA)")
    ap.add_argument("--eps", type=float, default=None, help="指定預估(forward)EPS;省略則用 TTM 代理")
    ap.add_argument("--years", type=int, default=5, help="歷史 PE 取樣年數(預設 5)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    s = args.stock.strip().upper()
    out = fetch_tw(s, args.eps, args.years) if s.isdigit() else fetch_us(s, args.eps, args.years)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return

    print(f"\n=== {s}({out['market']}) 本益比五檔價 ===")
    print(f"EPS = {out['eps']}（{out['eps_kind']}）")
    print(f"歷史 PE 取樣:{out['pe_sample']} 筆 / 近 {out['years']} 年,範圍 {out['pe_low']}–{out['pe_high']}")
    print(f"現價 {out['current_price']}  現在 PE {out['current_pe']}")
    print("-" * 44)
    print(f"{'等級':<6}{'PE(分位)':<14}{'對應價':<12}")
    for r in out["bands"]:
        print(f"{r['level']:<6}{str(r['pe'])+' (P'+str(r['percentile'])+')':<14}{str(r['price']):<12}")
    print("-" * 44)
    print(f"=> 現價判定:【{out['verdict']}】")
    print("\n⚠️ 教育性工具,非投資建議。分位是『相對自己歷史』的便宜/貴;EPS 預估含假設、可能有誤。")


if __name__ == "__main__":
    main()
