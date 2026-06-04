---
name: google-nexus
description: 用 Google「Nexus」五代理人時序預測框架(arXiv:2605.14389)幫一支股票做未來 N 日走勢預測 + 可解釋推理。把資料拆成 5 個推理階段——歷史脈絡(A_ctx)→宏觀軌跡(A_macro)+微觀逐日(A_micro)→合成(A_syn)，並用回測校準(A_calib)修正——比單一 chain-of-thought 更穩、更可解釋。核心是 references/nexus-framework.md 的階段準則，用 scripts/fetch_series.py 動態撈 OHLCV+基本面+新聞當 context。適用於:「預測 X 股未來走勢」「用 Nexus 幫我看這檔接下來幾天/幾週」「這支短線會漲還是跌」「幫我做時序預測」。台股用純數字(2330)、美股用英文代號(NVDA)。⚠️ 教育性模擬，非投資建議。
---

# google-nexus — 用 Google Nexus 框架做時序預測

## 這個 skill 在做什麼

拿一支股票，**用 Google 的 Nexus 五代理人時序預測框架** 產出「未來 N 個交易日的走勢預測 + 完整可解釋推理」。
不是單一 AI 直接猜，而是把問題拆成 5 個專責推理階段，分而治之再合成：

```
A_ctx (歷史脈絡)  →  A_macro (top-down 整段軌跡)  ┐
                  →  A_micro (bottom-up 逐日)     ┤→  A_syn (合成最終預測)
                     A_calib (回測校準 guidelines) ┘
```

> **核心理念:** 結構化拆解 > 一次性猜測。先把雜亂資料整理成時間軸(ctx)，再從「整段大方向(macro)」
> 與「逐日細節(micro)」兩個角度各算一次，最後用校準規則(calib)合成(syn)。論文證實每個元件都有貢獻。

> ⚠️ **重要聲明(每次回答都要讓使用者意識到):** 這是**統計/啟發式模擬**，**不是投資建議**。
> 預測本質不確定，數據來自第三方 API 可能有誤；投資前自行查證、自負風險。

## 啟動時機

使用者說「預測 X 股未來走勢」「用 Nexus 看這檔接下來幾天/幾週」「這支短線會漲還是跌」
「幫我做時序預測」「X 股 10 天後大概多少」等。

## 核心:先讀框架(references/nexus-framework.md)

**回答前先讀 `references/nexus-framework.md`** ——這是本 skill 的大腦，包含 5 階段的角色、輸入輸出、
推理規則、各種 setup 的校準啟發式(momentum / parabolic / fallen-angel / squeeze / 事件驅動)、
與標準輸出報告骨架。**預測一律以它為主。**

## 執行流程

```
1. 讀 references/nexus-framework.md(核心框架)
2. 撈 context 資料:python scripts/fetch_series.py <代號> [--horizon 10]
     台股用純數字(2330);美股用英文代號(NVDA)。
     回傳:近 ~130 日 OHLCV、基本面快照、近期新聞標題、技術指標(RSI/MA/ATR/漲跌幅)、台股三大法人。
     ★ 動態原則:循環股多撈稼動率/報價、題材股查訂單/營收佔比、事件型確認 catalyst 日——
       必要時擴充本腳本或另查,因為不同 setup 該看的訊號不同(框架已說明)。
3. A_ctx:把資料整理成結構化時間軸 + regime notes + 資料缺口
4. A_macro:top-down 給整段 T 日軌跡 + regime + confidence
5. A_micro:bottom-up 給逐日 T 個預測值 + driver(跳過休市日)
6. A_calib:依 setup 類型挑 heuristic guidelines(無法實跑 6-split 時標明 heuristic)
7. A_syn:融合 macro+micro+G → final_forecast(剛好 T 個) + summary
8. 用框架的報告骨架輸出 + 免責聲明
```

## 參數

- **horizon T**:預設 10 個交易日(~2 週)。使用者指定就用指定值。
- **台股**純數字代號、**美股**英文代號。
- 預測值**剛好 T 個**;日期跳過週末與休市。

## 輸出格式

依 `references/nexus-framework.md` 的「標準輸出報告骨架」:
Executive Summary → A_ctx 時間軸 → A_macro → A_micro 逐日表 → A_calib guidelines → A_syn final_forecast + summary。
每份結尾附 trade implication(僅參考)與免責聲明。

## 鐵則

- ⚠️ 每次回答都要有「教育性模擬，非投資建議」聲明。
- 預測值剛好 T 個;資料缺口誠實標示，不捏造。
- 提到槓桿/反向 ETF 要標 decay 風險。
- 先確認使用者是否已持有(區分「新進場」vs「重評估」)。
- 本 skill 實作了 Google 公開論文的方法，與論文作者/Google **無任何關聯**。
