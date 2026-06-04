# Nexus 框架 — 五代理人時序預測（評斷準則）

> 源自 Google / Penn State 論文 **"Nexus: An Agentic Framework for Time Series Forecasting"**（arXiv:2605.14389v1, 2026-05）。
> 本檔是 google-nexus skill 的「大腦」：定義 5 個推理階段的角色、輸入輸出、推理規則與校準啟發式。
> AI 評斷一支股票的未來走勢時，一律以此檔為主，逐階段執行。

---

## 核心理念

把雜亂的多模態資料（數值序列 + 非結構化文本）拆成 5 個專責推理階段，
**分而治之 → 再合成**，比單一 chain-of-thought 更穩、更可解釋：

```
A_ctx (歷史脈絡)  →  A_macro (top-down 整段軌跡)  ┐
                  →  A_micro (bottom-up 逐日)     ┤→  A_syn (合成最終預測)
                     A_calib (回測校準, 產出 guidelines) ┘
```

論文重點結論：5 階段在「多模態情境預測」相對單一 CoT 顯著改善（MAPE -15%、reasoning 偏好度 +60~97%），
且每個元件（macro/micro/calib）拿掉都會變差（ablation 證實）。temperature 建議 0.1。

---

## 階段 1：A_ctx — 歷史脈絡代理

**任務**：把原始 OHLCV + 新聞/公告/籌碼/基本面，整理成**結構化時間軸**，過濾雜訊、抽取因果事件。
讓下游不會 cognitive overload。

**做法**
- 過濾雜訊：丟 routine filings / 無關產業 roundup；保留實質催化劑（earnings、guidance、訂單、M&A、訴訟、法規、總經衝擊、籌碼異動）。
- 因果配對：每日 close（與漲跌幅）配當日 / 前 1–3 日的事件。
- 規範化：日期 `YYYY-MM-DD`、數值 2 位小數、事件一句話 < 80 字。

**輸出**：結構化 timeline（Date | Close | Δ% | Volume | Drivers）+ 基本面快照 + regime notes（趨勢/量價/support-resistance/ATR）+ 明列資料缺口。

**禁止**：不做預測、不加主觀方向；資料缺失要明說不要捏造。

---

## 階段 2：A_macro — 宏觀推理代理（top-down）

**任務**：對整段 horizon T 給一條**粗顆粒軌跡** + 闡述 regime（bull continuation / consolidation / mean reversion / regime shift / bear）。

**推理步驟（必寫）**
1. 趨勢診斷：方向、強度、量能配合。
2. Regime 判斷：accumulation / mark-up / distribution / mark-down。
3. 總經/產業 overlay：2–4 個影響整段的宏觀因子。
4. 軌跡 rationale：整段曲線形狀（漲/跌/震盪）要對。
5. 風險情境：1 個「macro 假設破壞」的另一條曲線。

**輸出**：`<reasoning>…</reasoning>` + `<forecasted_values>[v1..vT]</forecasted_values>` + `<confidence>low|medium|high</confidence>`。
不做逐日波動；值剛好 T 個。

---

## 階段 3：A_micro — 微觀推理代理（bottom-up）

**任務**：對 horizon 內**每個 timestep** 給預測值 + driver，捕捉短期 catalyst、support/resistance breach、量價背離、即將到來事件（earnings / CPI / Fed / ex-div）。

**做法**
1. 以 last close 為錨，第一天判斷 carryover momentum。
2. 逐日推進：當天有無 catalyst？前日是否觸 key level？短期 momentum？
3. 波動估計：ATR ≈ 過去 20 日 daily range 均值；**不要平滑**，容許單日 ±2–4% 合理波動。

**輸出**：JSON `timestamp_forecasts`（timestamp / date / day_info / movement_label / key_drivers / adjusted_forecast_value）+ `vol_assumption_atr`。
entries 剛好 T 個；date 跳過週末/休市。

---

## 階段 4：A_calib — 校準代理（回測，產出 guidelines）

**任務**：切 n 個 backtest split（預設 6），各用前段當 context、後段當 ground truth，跑 ctx→macro+micro→synth（不含 calib）拿 hypothetical forecast，比對實際，**萃取可機械化的 review guidelines G**；取交集、保留能讓 MAPE 改善 ≥5% 的 rule。

**做不到完整回測時的 heuristic G（按 setup 類型挑）**
- **Momentum extension**：spike(+25%) 後 5 日回吐 >80% → 偏空，反彈視逃命波。
- **Parabolic / 過熱**：RSI>75 且距 200DMA >+80% → 中段偏空 0.5 ATR；漲停隔日不採突破延續。
- **Fallen-angel 反彈**：RSI<35 觸底 + 催化 → 反彈延續，但 200DMA 為強反壓、首測常失敗。
- **Micro-cap squeeze**：單日量 >10× 均量 + 長上影 → 隔日偏空 0.5 ATR；下檔 ATR 倍增；上檔 cap 52W 高。
- **事件驅動**：利多見報當日收黑（sell-the-news）→ 後 2–3 天偏空；回吐 fib 0.5。
- 通用：macro 與 micro day-1 差距 >1 ATR → event 日採 micro、否則 macro。

**輸出**：`<diagnosis>` + `<guidelines>` + `<validation>`（≥5% 改善才 PASS）。

---

## 階段 5：A_syn — 合成代理（最終預測）

**任務**：融合 macro 軌跡 + micro 逐日 + calib guidelines G → 最終 X_{τ+1:τ+T} 與完整 CoT。

**合成原則**
1. 對齊起點：第 1 天以 last close 為錨；macro/micro 差 >1 ATR 時傾向 micro（短期 catalyst 敏感）。
2. 權重 routing：整段方向/regime 看 macro；單日跳動/catalyst 看 micro；衝突要寫出如何裁決。
3. 套用 G：依 setup 類型修正特定日。
4. 連續性檢查：單日 >5 ATR 必須有事件支撐。
5. 完整 CoT：一步步說明調整。

**輸出**：`<reasoning>`（Step1 錨點 → Step2 軌跡形狀 → Step3 逐日調整表 → Step4 sanity check → Step5 guideline 套用）+
`<final_forecast>[v1..vT]</final_forecast>` + `<summary>`（方向 / 終點價 / 關鍵風險 / trade implication）。

---

## 標準輸出報告骨架

```
# Nexus Forecast — <TICKER> @ <date>  (horizon T)
0. Executive Summary（當前價 / 終點預測+區間 / 方向 / 信心 / 主要風險 / 持倉關聯 / trade implication）
1. A_ctx 結構化時間軸 + 基本面快照 + regime + 資料缺口
2. A_macro reasoning + forecast(T) + confidence
3. A_micro 逐日表 + ATR
4. A_calib guidelines（標明 heuristic 或實跑）
5. A_syn 逐日調整表 + final_forecast(T) + summary
```

---

## 鐵則

- ⚠️ **教育性模擬，非投資建議**；數據來自第三方 API 可能有誤，投資自負風險。
- 預測值一律**剛好 T 個**；資料缺口要誠實標示，不捏造。
- 槓桿 / 反向 ETF 提到時標 **decay 風險**。
- 區分「新進場」vs「重評估」：先確認使用者是否已持有。
