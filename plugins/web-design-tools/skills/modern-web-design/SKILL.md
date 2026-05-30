---
name: modern-web-design
description: 用 Next.js + Tailwind + shadcn/ui 做出「有質感的現代網站」,而不是 AI 預設那種像 2014 年的通用樣板。涵蓋四件事:(1) 突破 AI 預設審美、用對的字體/間距/色彩做出現代感;(2) 不靠 3D 模型也能做的「捲動逐幀動畫」管線(圖片→影片→拆幀→ScrollTrigger);(3) 用 Playwright 擷取參考網站的「設計語言」當靈感、再重建+客製(非照抄);(4) 依「網站給誰看、要達成什麼」拆出不同設計策略(找客戶/說故事/最快看懂)。適用於:使用者要做或改網站/landing page、要做捲動動畫特效、要參考某個得獎網站的風格、或不確定網站該怎麼設計。
---

# modern-web-design — 做出有質感的現代網站

## 這個 skill 在做什麼

幫使用者用 **Next.js + Tailwind CSS + shadcn/ui** 做出 **現代、有設計感** 的網站,並避免 AI 的通病——**隨手一個 prompt 就吐出「像 2014 年」的通用樣板**(模型訓練資料大量停在 Bootstrap/扁平化時代)。

> 核心觀念(來自實作經驗):**隨意 prompt → 過時通用風;要靠「明確的設計方針 + 對的工具鏈」才能拉出現代質感。而且——動畫特效再炫都不是重點,「網站是做給誰看的」比任何特效都重要。**

## 啟動時機

使用者說「幫我做/改一個網站或 landing page」「做個有設計感的首頁」「做捲動動畫/scroll 特效」「參考這個得獎網站的風格」「這網站該怎麼設計」等。

## 四個能力(依需求載入對應 reference)

| 需求 | 載入 | 做什麼 |
|---|---|---|
| 要「現代質感、不要 AI 味」、起常見站型 | `references/modern-aesthetics.md` | 反通用審美 rubric、字體/色彩/間距原則、shadcn 起手、常見站型 scaffold |
| 要捲動逐幀動畫(漢堡炸裂、樹生長…) | `references/scroll-animation-pipeline.md` | 圖→影片→拆幀→GSAP ScrollTrigger;`scripts/extract_frames.py` |
| 要參考某個網站/Awwwards 得獎站的風格 | `references/awwwards-clone.md` | `scripts/extract_design_reference.py`(Playwright 擷設計語言)→ 重建+客製 |
| 不確定網站該怎麼設計、要對的版本 | `references/design-strategy.md` | 依受眾/目標拆三種策略、各自結構與追蹤指標 |

> 用 Read 載入需要的 reference,不要一次全塞進 context。

## 建議工作流程

1. **先問「給誰看、要達成什麼」**(別急著做動畫)。若使用者沒想清楚 → 先走 `design-strategy.md` 決定策略與結構,再開工。
2. **起底**:用 `modern-aesthetics.md` 的方針 + shadcn/ui 把站型 scaffold 出來(常見站型別從零寫)。
3. **要動畫**:走 `scroll-animation-pipeline.md`;3D/逐幀效果優先用「逐幀圖序列 + ScrollTrigger」而非真 3D 模型(使用者不會真的轉動它)。
4. **要參考某站風格**:走 `awwwards-clone.md`,用 Playwright 擷「設計語言」當靈感清單,**重建並大幅客製**(換主題/素材),不要照抄。
5. **收尾**:回歸本質——效能、無障礙、行動裝置可用性;特效是為目標服務,不是目的。

## ⚠️ 重要原則與免責

- **不要過度包裝**:華麗動畫常以 **效能差、無障礙低** 為代價;依目標取捨(見 design-strategy)。
- **版權/抄襲**:`awwwards-clone` 只擷取「設計語言(配色/字體/結構/節奏)」當 **靈感參考**,**不可像素級照抄或盜用他人素材/品牌**;務必換主題、換素材、做出原創差異。盜圖盜設計有法律風險。
- 外部生成工具(影像/影片生成,如 Google Whisk/Flow)**無法程式化**,需使用者手動產出素材後交給 skill 接續。

## 應用案例

- **「幫我做一個 SaaS landing page,要現代不要 AI 味」** → 載 modern-aesthetics:選一個明確美學方向(如 editorial/瑞士風)、指定非預設字體與間距尺度、用 shadcn 元件 → scaffold。
- **「首頁要一個漢堡邊滑邊炸開的效果」** → 載 scroll-animation-pipeline:使用者用 Whisk/Flow 生「完整→炸裂」影片 → `extract_frames.py` 拆幀 → 產生 ScrollTrigger 逐幀元件。
- **「照這個 Awwwards 網站的感覺做我的工作室站」** → 載 awwwards-clone:`extract_design_reference.py` 擷設計語言 → 重建並換成你的內容與主題。
- **「我不知道我的個人品牌站該怎麼做」** → 載 design-strategy:依目標(找客戶 vs 說故事 vs 最快看懂)選版本與結構、定追蹤指標。

---

*詳細步驟、程式碼模板與腳本見 `references/` 與 `scripts/`。*
