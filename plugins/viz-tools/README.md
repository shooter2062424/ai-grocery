# viz-tools

> 把「講不清楚的系統」跟「一坨數字」變成看得懂的圖。

兩個 vendored skill 加一個外部相依 plugin，覆蓋兩種需求：**圖解**（架構、流程、時序、狀態）與**圖表**（數據、報告）。

## 內含

| 類型 | 名稱 | 用途 |
|---|---|---|
| skill | `archify` | 架構圖 / 工作流程圖 / 時序圖 / 資料流圖 / 生命週期與狀態機。產出的是**可探索的單檔 HTML + inline SVG**，內建深淺色主題與可選的路徑動畫，可匯出 PNG / JPEG / WebP / SVG / WebM。吃自然語言需求，也吃你貼上的 Mermaid（`flowchart` / `sequenceDiagram` / `stateDiagram`），要畫真實程式碼的架構時會去讀 repo。 |
| skill | `lieflat-charts` | 模板驅動的資料視覺化與報告產生器。圖表來自 Lupi / Basics / Glance / Maps / Interactive 五組真實實作的 gallery；報告有 12 套中英文整頁模板。以 Mono 灰階保底，會依資料語義自動挑內建彩色預設，同一份交付不混色系。輸出是雙擊就能開的單檔 HTML。 |
| 相依 plugin | `diagram-design` | 見下。 |

`archify` 跟 `lieflat-charts` 的分工：**archify 畫「東西之間的關係」，lieflat-charts 畫「數字」。** 系統怎麼串、請求怎麼流、狀態怎麼轉 → archify；營收趨勢、問卷結果、比例分佈、要交一份報告 → lieflat-charts。

## 相依 plugin（自動一起安裝）

| Plugin | 來源 | 用途 |
|---|---|---|
| `diagram-design` | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 品牌化的圖表製作：架構圖、流程圖、時序圖、狀態機、ER / 資料模型、時間軸、泳道圖、象限圖、雷達圖、漏斗、樹狀、組織圖、Sankey、魚骨、Wardley map、使用者旅程等數十種版型，輸出 HTML / SVG / PNG。可從網站擷取品牌 token，也能重畫 `.drawio` 與 Mermaid 來源。 |

## 收錄來源與授權

| Skill | 原作者 | 原 repo | 授權 |
|---|---|---|---|
| `archify` | tt-a1i | [tt-a1i/archify](https://github.com/tt-a1i/archify) | MIT（見 `skills/archify/LICENSE`）。上游基於 Cocoon-AI/architecture-diagram-generator (MIT)。 |
| `lieflat-charts` | 躺在廢墟裡（[moxt.ai](https://moxt.ai)） | [larashero3-dotcom/lieflat-charts](https://github.com/larashero3-dotcom/lieflat-charts) | **PolyForm Noncommercial License 1.0.0**（見 `skills/lieflat-charts/LICENSE`） |

> ⚠️ **`lieflat-charts` 是非商業授權。** PolyForm Noncommercial 只允許非商業用途使用與再散布。
> 要拿它產出的圖表或報告做商業用途（客戶交付、對外銷售、營利產品），請先向原作者取得授權。
> 另外上游要求：公開分發用它產生的內容時，請署名或標註開發者。
>
> `archify` 是 MIT，沒有這個限制。

vendored 的原因：兩者上游都不是 Claude Code plugin 形式（安裝方式是 `npx skills add`），
沒有 `plugin.json` 可以被 marketplace 直接參照，所以複製進來並在此標註來源。
`diagram-design` 上游本身就是 marketplace，因此走外部參照，永遠跟著上游最新版。

vendored 時做的唯一修改：在 `SKILL.md` frontmatter 的 `description` 後面**附加**繁中觸發詞，
讓中文提問也叫得動這些 skill。原本的英文/簡中描述與正文一字未動。

為了控制 repo 體積，`archify` 的 `test/` 與 `package-lock.json`、`lieflat-charts` 的 `docs/`（19MB 截圖）未收錄，
不影響 skill 執行。需要那些內容請到上游 repo 看。

## 安裝

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過改用:claude plugin marketplace update ai-grocery
claude plugin install viz-tools@ai-grocery                # diagram-design 會一起裝進來
```

裝 `agent-essentials` 的話這個 plugin 會被當相依一起帶進來，不用重複安裝。

## 注意事項

- `archify` 的 PNG / WebM 匯出需要 headless 瀏覽器；環境沒有時它會退回輸出 HTML / SVG。
- `lieflat-charts` 純 SVG 的圖可離線開；用到 Chart.js、ECharts、地圖 GeoJSON 或線上字型的圖在未內聯依賴時需要連網。
