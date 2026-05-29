#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_memory.py — 從股癌(Gooaye)逐字稿包建立「標的提及時間軸 + 近期加權排名」記憶。

用途:
  1. 下載 https://whatmkreallysaid.com/transcripts.json.br(brotli,~10MB,含全部集數)
  2. 對每一集的逐字稿,用個股/題材字典做確定性比對,統計每集提及次數
  3. 產出兩個記憶檔到 ../references/:
       - mention-timeline.json  機器可讀:每個標的/題材的逐集提及時間軸
       - ranking.json           近期加權排名 + 趨勢(用於 recency-ranking.md / skill 推理)

設計原則:
  - 集數(n)遞增 = 時間遞增;同時保留真實日期(d)。
  - 純確定性比對(無 LLM),快、可重現、零幻覺。情緒/傾向的質化判讀由 AI 另外在
    recent-stance.md 完成(讀最近約 60 集的 desc/逐字稿)。
  - 拉丁代號(NVDA/0050…)用「非英數邊界」比對,讓中文字相鄰時也算邊界。

每週更新:cron 只要重跑本腳本即可(會抓最新 pack、重算全部),再請 AI 刷新 recent-stance.md。

用法:
  python build_memory.py                 # 自動下載最新 pack 後建立記憶
  python build_memory.py --pack PATH     # 用本機既有 pack(.br 或已解壓 .json)
"""

import os, re, sys, json, argparse, datetime, urllib.request

PACK_URL = "https://whatmkreallysaid.com/transcripts.json.br"
MANIFEST_URL = "https://whatmkreallysaid.com/pack_manifest.json"
HERE = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.normpath(os.path.join(HERE, "..", "references"))

# 近期加權的衰減係數(以「集」為單位)。0.97 ≈ 約 23 集半衰期,凸顯她最近的傾向。
DECAY = 0.97
RECENT_WINDOW = 60   # 最近 N 集視為「近期」

# ── 個股字典:canonical -> {type, aliases:[...]} ──────────────────────────
# aliases 同時放中文名與代號/英文;拉丁字串會以非英數邊界比對。
STOCKS = {
    # 半導體 / 晶圓 / 封測
    "台積電(2330/TSMC)": ["台積電", "台積", "2330", "TSMC", "TSM"],
    "聯發科(2454)": ["聯發科", "2454", "MediaTek"],
    "聯電(2303)": ["聯電", "2303", "UMC"],
    "日月光(3711)": ["日月光", "3711"],
    "創意(3443)": ["創意電子", "3443", "GUC"],
    "世芯(3661)": ["世芯", "3661", "Alchip"],
    "力旺(3529)": ["力旺", "3529"],
    "信驊(5274)": ["信驊", "5274", "Aspeed"],
    "譜瑞(4966)": ["譜瑞", "4966"],
    "祥碩(5269)": ["祥碩", "5269"],
    "矽力(6415)": ["矽力", "6415"],
    # AI 伺服器 / 代工 / 板卡
    "緯穎(6669)": ["緯穎", "6669", "Wiwynn"],
    "廣達(2382)": ["廣達", "2382", "Quanta"],
    "緯創(3231)": ["緯創", "3231", "Wistron"],
    "鴻海(2317)": ["鴻海", "2317", "Foxconn", "鴻準"],
    "英業達(2356)": ["英業達", "2356"],
    "技嘉(2376)": ["技嘉", "2376"],
    "微星(2377)": ["微星", "2377"],
    "華碩(2357)": ["華碩", "2357", "ASUS"],
    "智邦(2345)": ["智邦", "2345"],
    # 電源 / 散熱 / 連接
    "台達電(2308)": ["台達電", "2308", "Delta"],
    "光寶(2301)": ["光寶", "2301"],
    "奇鋐(3017)": ["奇鋐", "3017"],
    "雙鴻(3324)": ["雙鴻", "3324"],
    # PCB / 載板
    "台光電(2383)": ["台光電", "2383"],
    "金像電(2368)": ["金像電", "2368"],
    "欣興(3037)": ["欣興", "3037"],
    "南電(8046)": ["南電", "8046"],
    # 記憶體
    "南亞科(2408)": ["南亞科", "2408"],
    "華邦電(2344)": ["華邦電", "2344"],
    "旺宏(2337)": ["旺宏", "2337"],
    "群聯(8299)": ["群聯", "8299"],
    "威剛(3260)": ["威剛", "3260"],
    # 被動元件
    "國巨(2327)": ["國巨", "2327", "Yageo"],
    "華新科(2492)": ["華新科", "2492"],
    # 重電 / 電網
    "華城(1519)": ["華城", "1519"],
    "士電(1503)": ["士電", "1503", "士林電機"],
    "中興電(1513)": ["中興電", "1513"],
    "亞力(1514)": ["亞力電機", "1514"],
    # 光學 / 光通訊
    "大立光(3008)": ["大立光", "3008"],
    "玉晶光(3406)": ["玉晶光", "3406"],
    # 航運
    "長榮(2603)": ["長榮海運", "2603"],
    "陽明(2609)": ["陽明海運", "2609"],
    "萬海(2615)": ["萬海", "2615"],
    # 金融
    "富邦金(2881)": ["富邦金", "2881"],
    "國泰金(2882)": ["國泰金", "2882"],
    # ETF
    "0050 元大台灣50": ["0050", "元大台灣50", "台灣50"],
    "0056 高股息": ["0056", "元大高股息"],
    "00878": ["00878"],
    "00929": ["00929"],
    "00940": ["00940"],
    # 美股 / 國際
    "NVDA 輝達": ["NVDA", "Nvidia", "輝達", "輝噠", "黃仁勳"],
    "AMD 超微": ["AMD", "超微"],
    "TSLA 特斯拉": ["TSLA", "Tesla", "特斯拉"],
    "AAPL 蘋果": ["AAPL", "蘋果"],
    "MSFT 微軟": ["MSFT", "微軟", "Microsoft"],
    "GOOGL 谷歌": ["GOOGL", "GOOG", "谷歌", "Google", "Alphabet"],
    "AMZN 亞馬遜": ["AMZN", "亞馬遜", "Amazon"],
    "META": ["META", "臉書", "Meta"],
    "AVGO 博通": ["AVGO", "博通", "Broadcom"],
    "MU 美光": ["美光", "Micron"],
    "SMCI 美超微": ["SMCI", "美超微", "Supermicro"],
    "PLTR": ["PLTR", "Palantir"],
    "ARM": ["ARM"],
    "INTC 英特爾": ["INTC", "英特爾", "Intel"],
    "ASML": ["ASML", "艾司摩爾"],
    "MSTR / 比特幣財庫": ["MSTR", "MicroStrategy", "Strategy"],
    "COIN": ["COIN", "Coinbase"],
    "SpaceX / 馬斯克": ["SpaceX", "馬斯克", "Musk", "Starlink", "星鏈"],
}

# ── 題材 / 產業字典 ──────────────────────────────────────────────────────
THEMES = {
    "AI": ["AI", "人工智慧", "人工智能"],
    "CoWoS / 先進封裝": ["CoWoS", "先進封裝", "advanced packaging"],
    "HBM 高頻寬記憶體": ["HBM", "高頻寬記憶體"],
    "ASIC 客製晶片": ["ASIC", "客製化晶片"],
    "矽光子 / CPO": ["矽光子", "CPO", "silicon photonics"],
    "散熱 / 液冷": ["散熱", "液冷", "水冷"],
    "重電 / 電網": ["重電", "電網", "電力建設", "輸配電"],
    "被動元件": ["被動元件", "MLCC"],
    "記憶體循環": ["記憶體", "DRAM", "NAND"],
    "機器人 / 人形機器人": ["機器人", "人形機器人", "humanoid"],
    "衛星 / 低軌衛星 / 衛星算力": ["低軌衛星", "衛星算力", "太空資料中心", "衛星"],
    "軍工 / 國防": ["軍工", "國防", "軍火"],
    "電動車": ["電動車", "EV"],
    "加密貨幣 / 比特幣": ["比特幣", "Bitcoin", "BTC", "加密貨幣", "以太幣", "Ethereum"],
    "核能 / SMR": ["核能", "核電", "SMR", "小型模組化反應爐"],
    "資料中心": ["資料中心", "data center", "datacenter"],
    "ETF / 被動投資": ["ETF", "被動投資", "定期定額"],
}


def is_latin(s):
    return bool(re.fullmatch(r"[A-Za-z0-9.\-]+", s))


def build_matchers(table):
    """回傳 {canonical: [(alias, compiled_regex), ...]}。拉丁用非英數邊界,中文用 literal。"""
    out = {}
    for canon, aliases in table.items():
        ms = []
        for a in aliases:
            if is_latin(a):
                pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(a) + r"(?![A-Za-z0-9])")
            else:
                pat = re.compile(re.escape(a))
            ms.append(pat)
        out[canon] = ms
    return out


def count_in_text(text, matchers):
    c = 0
    for pat in matchers:
        c += len(pat.findall(text))
    return c


def load_pack(pack_path):
    raw = open(pack_path, "rb").read()
    if pack_path.endswith(".br"):
        import brotli
        raw = brotli.decompress(raw)
    return json.loads(raw)


def download_pack(dest):
    req = urllib.request.Request(PACK_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        open(dest, "wb").write(r.read())
    return dest


def render_markdown(ranking, eps, path):
    """把 ranking.json 渲染成人類/AI 可讀的 recency-ranking.md(確定性產生,中文正確)。"""
    m = ranking["meta"]
    TREND = {"rising": "📈 升溫", "fading": "📉 退燒", "steady": "➡️ 持平"}

    def table(rows, n=25):
        out = ["| # | 標的 | 近期加權分 | 趨勢 | 最近60集 | 前60集 | 總提及 | 出現集數 | 首/末集 |",
               "|---|---|---:|---|---:|---:|---:|---:|---|"]
        for i, x in enumerate(rows[:n], 1):
            out.append(f'| {i} | {x["name"]} | {x["recency_score"]} | {TREND[x["trend"]]} '
                       f'| {x["recent60"]} | {x["prev60"]} | {x["total"]} | {x["episodes"]} '
                       f'| EP{x["first_ep"]}–EP{x["last_ep"]} |')
        return "\n".join(out)

    rising_s = [x["name"] for x in ranking["stocks_by_recency"] if x["trend"] == "rising"][:10]
    rising_t = [x["name"] for x in ranking["themes_by_recency"] if x["trend"] == "rising"][:8]
    fading_s = [x["name"] for x in ranking["stocks_by_recency"][:30] if x["trend"] == "fading"][:8]

    md = f"""# 股癌「標的記憶」近期加權排名(自動產生,勿手改)

> 由 `scripts/build_memory.py` 從逐字稿包確定性比對產生。**集數遞增=時間遞增。**
> 最新:**EP{m['built_at_ep']}**({m['latest_date']})· 共 {m['episode_count']} 集 ·
> 近期加權衰減係數 {m['decay']}(約 23 集半衰期)· 「近期」=最近 {m['recent_window']} 集。
>
> ⚠️ 這是「她提到什麼、最近提得多不多」的 **頻率訊號**,不等於買進建議,也不直接代表看多/看空
> (看多看空的質化判讀見 `recent-stance.md`)。提及次數高也可能是常被當對照組或唱衰。

## 🔥 最近升溫(rising)— 她近期明顯更常談
- **個股:** {('、'.join(rising_s)) or '—'}
- **題材:** {('、'.join(rising_t)) or '—'}

## 🧊 近期退燒(fading)— 曾熱、最近少談
- **個股:** {('、'.join(fading_s)) or '—'}

---

## 個股:近期加權排名(前 25)
{table(ranking["stocks_by_recency"])}

---

## 題材 / 產業:近期加權排名
{table(ranking["themes_by_recency"], 18)}

---

### 怎麼讀這份排名
- **近期加權分** = Σ(該集提及次數 × {m['decay']}^(最新集 − 該集))。越近的集數權重越高 → 凸顯「她最近更傾向什麼」。
- **趨勢** 比較「最近 60 集」vs「前 60 集」的提及量:升溫(>1.3×)、退燒(<0.7×)、持平。
- **總提及高但近期低** 的標的(如某些早年熱門)代表是長期常客但近期降溫。
"""
    open(path, "w", encoding="utf-8").write(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", help="本機 pack 路徑(.br 或 .json);省略則自動下載")
    ap.add_argument("--out", default=REF_DIR, help="references 輸出目錄")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    pack = args.pack
    if not pack:
        pack = os.path.join(args.out, "_transcripts.json.br")
        print("downloading pack ...")
        download_pack(pack)
    eps = load_pack(pack)
    eps = sorted(eps, key=lambda e: e.get("n", 0))
    max_ep = eps[-1]["n"]
    print(f"loaded {len(eps)} episodes, latest EP{max_ep}")

    stock_m = build_matchers(STOCKS)
    theme_m = build_matchers(THEMES)

    def scan(table_m):
        rec = {canon: {"by_episode": []} for canon in table_m}
        for e in eps:
            tx = e.get("tx", "") or ""
            n, d = e.get("n"), e.get("d", "")
            for canon, ms in table_m.items():
                c = count_in_text(tx, ms)
                if c:
                    rec[canon]["by_episode"].append([n, d, c])
        return rec

    def summarize(rec, kind):
        rows = []
        for canon, data in rec.items():
            be = data["by_episode"]
            if not be:
                continue
            total = sum(x[2] for x in be)
            eps_cnt = len(be)
            first_ep, last_ep = be[0][0], be[-1][0]
            recent = sum(x[2] for x in be if x[0] > max_ep - RECENT_WINDOW)
            prev = sum(x[2] for x in be if max_ep - 2 * RECENT_WINDOW < x[0] <= max_ep - RECENT_WINDOW)
            recency_score = round(sum(x[2] * (DECAY ** (max_ep - x[0])) for x in be), 2)
            trend = "rising" if recent > prev * 1.3 else ("fading" if recent < prev * 0.7 else "steady")
            rows.append({
                "name": canon, "type": kind, "total": total, "episodes": eps_cnt,
                "first_ep": first_ep, "last_ep": last_ep,
                "recent60": recent, "prev60": prev, "recency_score": recency_score, "trend": trend,
            })
        rows.sort(key=lambda r: r["recency_score"], reverse=True)
        return rows

    stock_rec = scan(stock_m)
    theme_rec = scan(theme_m)
    timeline = {
        "meta": {
            "built_at_ep": max_ep,
            "latest_date": eps[-1].get("d", ""),
            "latest_title": eps[-1].get("t", ""),
            "episode_count": len(eps),
            "decay": DECAY, "recent_window": RECENT_WINDOW,
            "note": "n=集數(遞增=時間遞增);count=該集逐字稿中提及次數(確定性比對)。",
        },
        "stocks": stock_rec,
        "themes": theme_rec,
    }
    ranking = {
        "meta": timeline["meta"],
        "stocks_by_recency": summarize(stock_rec, "stock"),
        "themes_by_recency": summarize(theme_rec, "theme"),
    }

    with open(os.path.join(args.out, "mention-timeline.json"), "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=1)
    with open(os.path.join(args.out, "ranking.json"), "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=1)
    render_markdown(ranking, eps, os.path.join(args.out, "recency-ranking.md"))
    # 移除暫存 pack(避免 commit 進 repo)
    tmp = os.path.join(args.out, "_transcripts.json.br")
    if os.path.exists(tmp):
        os.remove(tmp)
    print("wrote mention-timeline.json, ranking.json to", args.out)


if __name__ == "__main__":
    main()
