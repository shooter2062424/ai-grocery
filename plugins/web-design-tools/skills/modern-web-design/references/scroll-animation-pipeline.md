# Reference:捲動逐幀動畫管線(不靠 3D 模型)

## 核心洞見

要做「漢堡邊滑邊炸開」「樹生長」「冰箱打開」這種捲動動畫,**不需要真的做 3D 模型**——因為使用者 **不會真的去轉動它**,只是隨捲動播放一段固定動作。**用「逐幀圖序列 + ScrollTrigger」呈現即可**,又快又穩。

## 完整管線

```mermaid
flowchart LR
    A["一張主體圖<br/>(漢堡)"] -->|"影像生成+爆裂 prompt<br/>(如 Google Whisk)"| B["喜歡的關鍵畫面"]
    B -->|"首尾幀生影片<br/>首=完整 尾=炸裂<br/>(如 Google Flow)"| C["過場影片 mp4"]
    C -->|"拆幀(本 skill 腳本/ezgif)"| D["frame_0001.png ... frame_00NN.png"]
    D -->|"丟資料夾 + 套 ScrollTrigger"| E["邊捲動邊逐幀播放的元件"]
```

> ⚠️ **步驟 1–3(影像/影片生成)是外部工具,無法程式化**:請使用者用 Whisk(影像)、Flow(首尾幀生影片,有免費小額度)等產出影片或幀序列,再交給 skill 接續。效果不理想就重調 prompt 再生一次(會「抽卡」)。

## 拆幀(本 skill 提供腳本)

兩種輸入都支援:
- **使用者給「影片」** → 用 `scripts/extract_frames.py`(底層 ffmpeg)拆成編號 PNG。
  ```bash
  python scripts/extract_frames.py --video burger.mp4 --out public/frames/burger --fps 30
  # 產生 public/frames/burger/frame_0001.png ...(零補位、依序)
  ```
  需本機有 **ffmpeg**(`ffmpeg -version` 可驗證)。
- **使用者已用 ezgif 等拆好、給「資料夾」** → 直接用,跳過拆幀;必要時用腳本重新命名成零補位連號:
  ```bash
  python scripts/extract_frames.py --frames-dir ./my_frames --out public/frames/burger
  ```

**幀數建議:** 60–120 幀通常夠順;太多會肥。圖片先壓縮(webp 更佳)。

## ScrollTrigger 逐幀元件(React/Next.js + GSAP)

把整個 frames 資料夾的圖預載,捲動時依進度切換顯示的幀(canvas 畫最省效能):

```tsx
"use client";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

const FRAME_COUNT = 96;                 // 與實際幀數一致
const url = (i: number) =>
  `/frames/burger/frame_${String(i + 1).padStart(4, "0")}.png`;

export function ScrollFrames() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const images: HTMLImageElement[] = [];
    const state = { frame: 0 };

    // 預載所有幀
    for (let i = 0; i < FRAME_COUNT; i++) {
      const img = new Image();
      img.src = url(i);
      images.push(img);
    }
    const render = () => {
      const img = images[state.frame];
      if (!img?.complete) return;
      canvas.width = img.width; canvas.height = img.height;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
    };
    images[0].onload = render;

    // 捲動驅動幀數(scrub:捲動進度=動畫進度)
    const st = gsap.to(state, {
      frame: FRAME_COUNT - 1, snap: "frame", ease: "none",
      scrollTrigger: { trigger: wrapRef.current, start: "top top",
        end: "+=2000", scrub: 0.5, pin: true },
      onUpdate: render,
    });
    return () => { st.scrollTrigger?.kill(); st.kill(); };
  }, []);

  return (
    <div ref={wrapRef} className="h-screen grid place-items-center">
      <canvas ref={canvasRef} className="max-h-[80vh] w-auto" />
    </div>
  );
}
```

要點:
- **`scrub`** 讓動畫進度跟著捲動;**`pin`** 在播放時固定區塊;`end:"+=2000"` 控制要捲多長播完。
- 用 **canvas** 畫單一幀,比同時掛 N 個 `<img>` 省記憶體;大量幀務必 **預載 + 壓縮**。
- 尊重 `prefers-reduced-motion`:偵測到就直接顯示最終幀、不綁捲動。

## 其他主題(同管線)

樹生長、書中跑出角色、投影機投影、冰箱打開展示生鮮、市區白天→夜晚……只要能生出「首→尾」的過場影片,都能套同一條管線。Lottie(向量動畫,LottieFiles 找現成或自畫)、Three.js(真 3D,需要可互動才用)是進階選項。
