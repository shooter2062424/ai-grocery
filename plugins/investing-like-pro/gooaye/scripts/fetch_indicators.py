#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_indicators.py — 撈「股癌評斷一支股票時看重的指標」，輸出對齊 investment-framework.md 的摘要。

設計理念（重要）：
  這支腳本是「起手式」，不是唯一解。股癌的框架重視的指標會因股票類型而異
  （見 ../references/investment-framework.md），所以 AI 應該「動態」按需求改寫 / 擴充
  本腳本：景氣循環股多撈稼動率/報價、題材股多查營收佔比與純度、成長股多看 forward EPS 與成長率。

資料來源：
  - 台股：FinMind 開放 REST API（https://api.finmindtrade.com，部分 dataset 免 token；
    設環境變數 FINMIND_TOKEN 可拉高額度）。撈 本益比/淨值比/殖利率、月營收(YoY)、
    財報(毛利率/營益率/EPS)、三大法人買賣超。
  - 美股：yfinance（pip install yfinance），撈 trailing/forward PE、PEG、毛利/營益率、
    營收與獲利成長率、市值。

用法：
  python fetch_indicators.py 2330            # 台股（純數字代號）
  python fetch_indicators.py NVDA            # 美股（英文代號）
  python fetch_indicators.py 2330 --json     # 機器可讀

輸出只是「原始指標 + 簡單衍生」，最終的「好不好」判斷請交給 AI 套
investment-framework.md 的決策規則與紅旗去做，並附免責聲明。
"""
import os, sys, json, argparse, urllib.request, urllib.parse, datetime

FINMIND = "https://api.finmindtrade.com/api/v4/data"
TOKEN = os.environ.get("FINMIND_TOKEN", "")


def _get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def finmind(dataset, data_id, start_date, end_date=None):
    q = {"dataset": dataset, "data_id": data_id, "start_date": start_date}
    if end_date:
        q["end_date"] = end_date
    if TOKEN:
        q["token"] = TOKEN
    url = FINMIND + "?" + urllib.parse.urlencode(q)
    d = _get(url)
    if d.get("status") != 200:
        raise RuntimeError(f"{dataset}: {d.get('msg')}")
    return d.get("data", [])


def _yrs_ago(years):
    t = datetime.date.today()
    try:
        return t.replace(year=t.year - years).isoformat()
    except ValueError:  # 2/29
        return t.replace(year=t.year - years, day=28).isoformat()


# ───────────────────────── 台股 ─────────────────────────
def fetch_tw(stock_id):
    out = {"market": "TW", "stock_id": stock_id, "indicators": {}, "notes": []}
    ind = out["indicators"]

    # 1) 估值：本益比 / 淨值比 / 殖利率
    try:
        per = finmind("TaiwanStockPER", stock_id, _yrs_ago(1))
        if per:
            last = per[-1]
            ind["PER"] = last.get("PER")
            ind["PBR"] = last.get("PBR")
            ind["dividend_yield_%"] = last.get("dividend_yield")
            ind["valuation_date"] = last.get("date")
            pers = [x["PER"] for x in per if x.get("PER")]
            if pers:
                ind["PER_1y_low"] = round(min(pers), 1)
                ind["PER_1y_high"] = round(max(pers), 1)
    except Exception as e:
        out["notes"].append(f"PER 取得失敗：{e}")

    # 2) 成長 / 領先指標：月營收 + YoY
    try:
        rev = finmind("TaiwanStockMonthRevenue", stock_id, _yrs_ago(2))
        if rev:
            rev.sort(key=lambda x: (x.get("revenue_year", 0), x.get("revenue_month", 0)))
            last = rev[-1]
            ind["latest_rev_month"] = f"{last.get('revenue_year')}-{last.get('revenue_month'):02d}"
            ind["latest_revenue"] = last.get("revenue")
            # 找去年同月算 YoY
            ly = [x for x in rev if x.get("revenue_year") == last.get("revenue_year") - 1
                  and x.get("revenue_month") == last.get("revenue_month")]
            if ly and ly[0].get("revenue"):
                yoy = (last["revenue"] / ly[0]["revenue"] - 1) * 100
                ind["revenue_YoY_%"] = round(yoy, 1)
            # 近 3 個月 YoY 趨勢
            trend = []
            for r in rev[-3:]:
                m = [x for x in rev if x.get("revenue_year") == r.get("revenue_year") - 1
                     and x.get("revenue_month") == r.get("revenue_month")]
                if m and m[0].get("revenue"):
                    trend.append(round((r["revenue"] / m[0]["revenue"] - 1) * 100, 1))
            if trend:
                ind["revenue_YoY_last3_%"] = trend
    except Exception as e:
        out["notes"].append(f"月營收取得失敗：{e}")

    # 3) 基本面：毛利率 / 營益率 / EPS（最近兩季）
    try:
        fs = finmind("TaiwanStockFinancialStatements", stock_id, _yrs_ago(1))
        if fs:
            by_date = {}
            for row in fs:
                by_date.setdefault(row["date"], {})[row["type"]] = row.get("value")
            quarters = sorted(by_date)[-2:]
            margins = []
            for qd in quarters:
                rec = by_date[qd]
                rev = rec.get("Revenue")
                gp = rec.get("GrossProfit")
                oi = rec.get("OperatingIncome")
                eps = rec.get("EPS")
                m = {"quarter": qd}
                if rev and gp:
                    m["gross_margin_%"] = round(gp / rev * 100, 1)
                if rev and oi:
                    m["op_margin_%"] = round(oi / rev * 100, 1)
                if eps is not None:
                    m["EPS"] = eps
                margins.append(m)
            ind["recent_quarters"] = margins
    except Exception as e:
        out["notes"].append(f"財報取得失敗：{e}")

    # 4) 籌碼（輔助）：近 5 日三大法人合計買賣超（張）
    try:
        ii = finmind("TaiwanStockInstitutionalInvestorsBuySell", stock_id, _yrs_ago(0) if False else
                     (datetime.date.today() - datetime.timedelta(days=14)).isoformat())
        if ii:
            ii.sort(key=lambda x: x.get("date", ""))
            net = {}
            for r in ii:
                d = r.get("date")
                net[d] = net.get(d, 0) + (r.get("buy", 0) - r.get("sell", 0))
            days = sorted(net)[-5:]
            total = sum(net[d] for d in days)
            ind["inst_net_5d_shares"] = int(total)
            ind["inst_net_5d_lots"] = round(total / 1000, 1)  # 1 張 = 1000 股
    except Exception as e:
        out["notes"].append(f"法人買賣超取得失敗：{e}")

    return out


# ───────────────────────── 美股 ─────────────────────────
def fetch_us(ticker):
    out = {"market": "US", "stock_id": ticker, "indicators": {}, "notes": []}
    try:
        import yfinance as yf
    except ImportError:
        out["notes"].append("未安裝 yfinance（pip install yfinance）；無法取美股指標。")
        return out
    try:
        info = yf.Ticker(ticker).info
        g = lambda k: info.get(k)
        ind = out["indicators"]
        ind["trailing_PE"] = g("trailingPE")
        ind["forward_PE"] = g("forwardPE")
        ind["PEG"] = g("trailingPegRatio") or g("pegRatio")
        ind["price_to_sales"] = g("priceToSalesTrailing12Months")
        ind["gross_margin_%"] = round(g("grossMargins") * 100, 1) if g("grossMargins") else None
        ind["op_margin_%"] = round(g("operatingMargins") * 100, 1) if g("operatingMargins") else None
        ind["revenue_growth_%"] = round(g("revenueGrowth") * 100, 1) if g("revenueGrowth") else None
        ind["earnings_growth_%"] = round(g("earningsGrowth") * 100, 1) if g("earningsGrowth") else None
        ind["market_cap"] = g("marketCap")
        ind["dividend_yield_%"] = round(g("dividendYield"), 2) if g("dividendYield") else None
    except Exception as e:
        out["notes"].append(f"yfinance 取得失敗：{e}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stock", help="台股純數字代號（2330）或美股英文代號（NVDA）")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    args = ap.parse_args()

    s = args.stock.strip().upper()
    out = fetch_tw(s) if s.isdigit() else fetch_us(s)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print(f"\n=== {out['stock_id']}（{out['market']}）股癌框架指標速覽 ===")
    for k, v in out["indicators"].items():
        print(f"  {k:24} {v}")
    if out["notes"]:
        print("\n  注意：")
        for n in out["notes"]:
            print(f"   - {n}")
    print("\n  ↑ 以上為原始指標；請套 references/investment-framework.md 的決策規則判讀，"
          "並務必附免責聲明（非投資建議）。")


if __name__ == "__main__":
    main()
