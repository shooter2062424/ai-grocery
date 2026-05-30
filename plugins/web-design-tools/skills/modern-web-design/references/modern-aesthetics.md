# Reference:突破 AI 預設審美 + 現代質感(Tailwind + shadcn/ui)

## 為什麼 AI 預設會「像 2014 年」

模型訓練資料大量集中在 Bootstrap / 扁平化 / 響應式革命時期,**隨手 prompt** 容易產出:置中標題 + 一排三欄卡片 + 圓角陰影 + 通用無襯線字 + 藍紫漸層。要現代質感,**必須給明確設計方針**,而不是「做漂亮一點」。

## 反通用(anti-generic)檢查清單

**字體 — 絕對不要全站只用這些當預設:** `Inter / Roboto / Arial / system-ui`。請刻意挑 **有個性的字體配對**(標題 + 內文各一),例如:
- Editorial/雜誌:襯線標題(如 Fraunces、Playfair、Spectral)+ 乾淨無襯線內文。
- 科技/簡潔:幾何無襯線(如 Geist、Satoshi、Space Grotesk)+ 等寬點綴(JetBrains Mono)。
- 用 `next/font` 載入,定義 `--font-display` / `--font-body`。

**色彩 — 不要藍紫漸層蓋白卡片。** 建一套 **有意圖的調色盤**:1 個主色 + 1 個強調色 + 中性灰階(用 OKLCH 比 hex 更好調);深色模式不是把背景變黑就好,要重配對比。

**版面 — 跳出「三欄卡片」反射。** 用 **非對稱、留白、明確的視覺層級、大標題、克制的動效**;網格可破格(bento、雜誌式分欄)。

**間距/字級 — 用明確的尺度(scale)。** type scale(如 1.25 模數)、一致的 spacing token;標題與內文的對比要夠大。

## 先選一個「美學方向」(避免四不像)

開工前 **明確選 1 種** 並貫徹(別混搭到失焦):
`Editorial 雜誌` · `Swiss/International 瑞士風` · `Brutalist/Neo-brutalism` · `Minimal/Functional` · `Retro-futuristic` · `Organic/手感` · `Dark techno` · `Premium/精品`。
> 若使用者沒指定,先給 2–3 個方向 + 一句定位讓他選,再動手。

## 技術棧起手(Next.js + Tailwind + shadcn/ui)

```bash
# 1) Next.js + Tailwind
npx create-next-app@latest my-site --typescript --tailwind --app --eslint
cd my-site
# 2) shadcn/ui(可複製貼上的 React 元件原始碼,建在 Radix UI + Tailwind 之上)
npx shadcn@latest init
npx shadcn@latest add button card dialog input dropdown-menu navigation-menu sheet badge tabs
```
- **shadcn/ui 不是傳統 component library**,而是把元件原始碼複製進你的專案 → 可自由改樣式,適合做出差異化(不要保留預設樣式原封不動)。
- 字體:`next/font/google` 或 local font;主題 token 放 `globals.css` 的 `@theme` / CSS variables。
- 動效:**Framer Motion**(進場/互動)+ **GSAP ScrollTrigger**(捲動,見 scroll-animation reference)。

## 常見站型 — 別從零寫,先 scaffold

實作經驗:**市面常見站型直接請 AI 起一個底最快**。可快速 scaffold 的型別與重點區塊:

| 站型 | 關鍵區塊 |
|---|---|
| 電商平臺 | 商品網格、篩選、購物車 sheet、結帳流程、商品詳情 |
| 點餐系統 | 分類菜單、品項 modal、購物車、訂單摘要 |
| 音樂串流 | 側欄導覽、播放列、專輯網格、now-playing |
| 旅遊規劃 | 行程時間軸、地圖區、卡片列表、預訂表單 |
| 醫療預約 | 日曆/時段選擇、科別篩選、預約表單、確認 |
| 聊天室 | 對話列表、訊息流、輸入列、即時狀態 |
| 數據分析後台 | 側欄 + 卡片 KPI、圖表(Recharts)、表格、篩選 |

> 起底後再套用上面的「美學方向 + 反通用清單」做差異化,別停在 shadcn 預設樣子。

## 收尾檢查

- **效能**:圖片用 `next/image`、字體 subset、避免過重動畫。
- **無障礙**:語意標籤、對比度、鍵盤可操作、`prefers-reduced-motion` 時關閉動畫。
- **行動裝置**:行動優先;觸控目標夠大;首屏快。
- **一致性**:同一套 token/間距/字級貫穿全站。
