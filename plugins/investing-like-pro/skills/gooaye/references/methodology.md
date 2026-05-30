# 記憶建立方法與更新流程(methodology)

## 兩層架構(重要)

本 skill 分兩層,**評斷股票以「框架層」為主、「記憶層」只是輔助**:

1. **框架層(主):`investment-framework.md`** —— 從 EP1–最新集全部逐字稿萃取的「評斷準則」
   (分型 + 七大維度的指標/決策規則/紅旗 + verdict 模板)。這是判斷一支股票好不好的大腦,變動慢。
   搭配 `scripts/fetch_indicators.py` 動態撈他看重的指標。
2. **記憶層(輔):`recent-stance.md` / `recency-ranking.md` / `ranking.json` / `mention-timeline.json`**
   —— 由 `build_memory.py` 從逐字稿確定性統計「他最近常談什麼」。**只當輕度輔助**(框架算完後微調信心),
   不可拿「他最近有沒有推薦」當股票好壞的判準。

> 下面說明的是「記憶層」的建立與每週更新;框架層只在股癌明顯改變選股邏輯時才需要重萃。

## 資料來源
- 非官方逐字稿庫 **whatmkreallysaid.com**(AI 聽寫,標註「僅供學習交流、不構成投資建議」,著作權屬原節目)。
- 全部集數打包在 `https://whatmkreallysaid.com/transcripts.json.br`(brotli,~10MB);`pack_manifest.json` 提供 `episode_count` 與版本,用來判斷有沒有新集數。
- 每筆欄位:`n`(集數,遞增=時間遞增)、`t`(標題)、`d`(ISO 日期)、`desc`(摘要)、`tx`(全文逐字稿)。

## 建立方式(混合法)
1. **程式確定性抽取(`scripts/build_memory.py`)**:用個股/題材字典掃每集 `tx`,統計提及次數 → 產生
   - `mention-timeline.json`:每個標的/題材的逐集提及時間軸。
   - `ranking.json` + `recency-ranking.md`:**近期加權排名**。加權分 = Σ(該集次數 × 0.97^(最新集−該集)),近的權重高;趨勢比較「最近 60 集 vs 前 60 集」。
2. **AI 質化摘要(`recent-stance.md`)**:讀最近約 60 集的 `desc`/逐字稿,整理她對主要標的/題材的看多看空、操作心態。這部分是 **人工/AI 判讀**,程式不做情緒分析。

## 重要限制與注意
- **頻率 ≠ 看多**:提及次數高也可能是唱衰、當對照組、或被聽眾問。看多看空以 `recent-stance.md` 為準。
- **字典覆蓋有限**:`build_memory.py` 的字典聚焦股癌常談的個股與題材,**不是全市場**;新冒出的標的可能要手動補進字典(`STOCKS` / `THEMES`)。
- **逐字稿是 AI 聽寫**:可能有錯字/同音字(已為部分別名加容錯,如「輝噠」)。
- **日期 vs 集數**:pack 內 `d` 是真實日期;排序與加權一律以 `n`(集數)為準。

## 每週更新流程(cron,週日與其他排程同批)
1. 抓 `pack_manifest.json`,比對 `episode_count` 是否 > `mention-timeline.json` 的 `meta.built_at_ep`。沒有新集就略過(不空 commit)。
2. 有新集 → 在 `scripts/` 跑:`python build_memory.py`(會自動下載最新 pack、重算三個機器記憶檔,跑完刪暫存 pack)。
3. 由 AI 依「最近約 60 集」重寫 `recent-stance.md`(更新基準集數、升溫/退燒、各標的傾向)。
4. `git commit`(繁中訊息,無 BOM UTF-8)→ `git push`(SSH)。
5. 回報新增到第幾集、近期升溫/退燒有何變化。

## 手動重建
```bash
cd plugins/investing-like-pro/skills/gooaye/scripts
python build_memory.py            # 自動下載最新 pack 並重算
# 或用本機既有 pack:
python build_memory.py --pack /path/to/transcripts.json.br
```
需要 `pip install brotli`。
