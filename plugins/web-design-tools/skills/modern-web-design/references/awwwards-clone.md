# Reference:擷取參考網站「設計語言」→ 重建 + 客製(非照抄)

## ⚠️ 先講原則(務必遵守)

- **目標是「取靈感、學設計語言」,不是抄襲。** 只擷取 **可抽象化的設計決策**:配色、字體配對、間距節奏、版面結構、動效類型、互動模式。
- **絕對不可**:像素級照搬、盜用對方的圖片/影片/Logo/文案/品牌、複製其專有素材。
- **一定要客製化**:換主題(影片示例:狗→貓→火箭→燈泡)、換素材、換內容、調整版面,做出 **原創差異**。直接照抄他人網站有 **法律(著作權/商標)風險**。
- 直接把整個網址丟給 Claude Code 通常 **會失敗**(尤其帶複雜動畫的站)——所以先用下面的方法把「設計語言」結構化擷取出來,再重建。

## 步驟

### 1) 擷取設計參考(本 skill 腳本)
用 Playwright 打開參考網站,抓出 computed 樣式統計、調色盤、字體、區塊結構與素材清單,輸出成一份 JSON「靈感 brief」:

```bash
# 需求:pip install playwright && playwright install chromium
python scripts/extract_design_reference.py --url https://example-awwwards-site.com \
  --out ./design-ref.json --screenshot ./design-ref.png
```
產出包含:
- **palette**:頁面實際用到的主要顏色(依出現頻率排序)。
- **fonts**:`font-family` 清單與用在哪些層級(標題/內文)。
- **type/spacing**:標題與內文的字級、行高、常見間距值。
- **sections**:由上到下的版面區塊(hero / nav / 卡片網格 / footer…)與大致佈局。
- **assets**:圖片/影片/Lottie/`<canvas>`/Three.js 等素材與動效類型(只列清單供判斷,**不下載盜用**)。
- **screenshot**:整頁截圖,給 Claude 看「設計語言」用。

### 2) 由 Claude Code 重建
把 `design-ref.json` + 截圖交給 Claude:
> 「參考這份設計語言(配色/字體/節奏/區塊結構/動效類型),用 Next.js + Tailwind + shadcn/ui **重建一個結構相近但內容與主題全換成 ___ 的網站**。動效用 Framer Motion / GSAP ScrollTrigger 重做,不要使用對方的任何素材。」

### 3) 換素材與主題(做出你的版本)
- **主體換掉**:狗→貓、飲料→漢堡之類;用影像/3D 生成工具產你自己的素材。
- **3D 模型材質替換**(若參考站用 Three.js):3D 模型 = 模型 + 材質;可請 Gemini 生成 **新的包裝材質/貼圖** 替換,或用 **Hyper3D** 從多張圖生成新模型(效果需「抽卡」)。
- **能用逐幀動畫就別做真 3D**(見 scroll-animation-pipeline)——使用者不會真的轉動它。

### 4) 微調對齊
擷取重建後各區塊常有小差異(定位/間距),逐區塊微調即可達到「神似但原創」。**重點是設計語言到位,不是 1:1。**

## 心法

> 「動畫特效再炫都不是重點。」復刻只是學習手段——學到對方 **為什麼好看**(層級、留白、節奏、色彩),套到 **你自己的受眾與目標** 上(見 design-strategy reference),才是真正的價值。
