# valuation-bands 方法論:EPS × 本益比五檔價

固定本益比情境分析(孫慶龍式)。把「貴不貴」從直覺變成可計算的五檔。

## 兩條獨立的計算

1. **目標五檔價** = `EPS × 各檔 PE`
   - 各檔 PE = 該股**過去 N 年自己**的 PE 分布分位:特價 P10、便宜 P25、合理 P50(中位)、昂貴 P75、瘋狂 P90。
   - **EPS 來源【預設鎖定高盛 (Goldman Sachs)】**,優先序:
     ① **上網查高盛對目標年度的 forward EPS**(務必註明年度/數值/報告日),以 `--eps` 帶入、`--source "高盛"` 標記 →
     ② 使用者明確指定其他券商時才覆寫(改 `--source`)→
     ③ **高盛未覆蓋該股 / 查不到** → fallback 用 consensus 或 **TTM EPS 代理**(= 現價 / 現在 PE),輸出明確標註 `⚠️ 已 fallback`、`eps_source=null`。
   - ⚠️ **無法全自動抓高盛**:高盛 EPS 出自付費研究,無公開 API 可按券商拆分;故採「來源鎖定高盛、數字由人/AI 查得後帶入並標記」。
   - ⚠️ 高盛多為**最樂觀的單一機構觀點(常為離群值)**,務必對照 consensus 中位數一起看,別當基準預期。
2. **現價貴賤判定** = 看**現在 PE** 落在哪個分位:
   - ≤P10 特價 · ≤P25 便宜 · P25–P75 合理 · ≤P90 昂貴 · >P90 瘋狂。
   - 注意:判定只看「現在 PE 的歷史分位」,**與你用哪個 EPS 算目標價無關**。

## 資料來源
- 台股(純數字):FinMind `TaiwanStockPER`(歷史 PER)+ `TaiwanStockPrice`(收盤)。免 token;`FINMIND_TOKEN` 可拉高額度。
- 美股(英文代號):yfinance。歷史 PE 以「近 N 年股價 / TTM EPS」近似;trailing/forward EPS 取自 `info`。

## 限制與陷阱(判讀務必講)
- **相對自己歷史,非絕對價值**:產業結構性衰退時整段 PE 下移,低 PE 可能是**價值陷阱**。
- **景氣循環股**:高檔常低 PE(賣點)、谷底常高 PE/虧損——別純用 PE 分位判,要配合循環位置(見 gooaye agent 框架 F 節)。
- **成長股**:用過去 EPS 會低估;務必用合理的 forward EPS(可用「營收成長×淨利率÷股數」推)。
- **PE 樣本不足**(<20 筆)會拒算;新股、長期虧損(無 PE)不適用本法。
- ⚠️ 教育用途、非投資建議。

## 用法
```bash
python scripts/pe_bands.py 2330 --eps 135      # 台股 + 指定預估 EPS
python scripts/pe_bands.py 2330                 # 台股 + TTM 代理
python scripts/pe_bands.py NVDA --years 5 --json
```
