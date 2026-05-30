#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_design_reference.py — 用 Playwright 從參考網站擷取「設計語言」當靈感 brief。

⚠️ 僅供「學習設計語言、再原創重建」用途,不可像素級照抄或盜用對方素材/品牌/文案。
輸出一份 JSON(配色、字體、字級/間距、區塊結構、素材與動效類型)+ 整頁截圖,
交給 Claude Code 參考,用 Next.js + Tailwind + shadcn/ui 重建並換成你自己的主題。

需求:
  pip install playwright
  playwright install chromium

用法:
  python extract_design_reference.py --url https://example.com \
      --out design-ref.json --screenshot design-ref.png
"""
import argparse, json, sys
from collections import Counter


JS_COLLECT = r"""
() => {
  const RGBA = (s) => (s||'').trim();
  const freq = (arr) => {
    const m = {}; arr.forEach(x => { if(!x) return; m[x]=(m[x]||0)+1; });
    return Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,16);
  };
  const els = Array.from(document.querySelectorAll('body *')).slice(0, 4000);
  const bg=[], color=[], fonts=[];
  els.forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.backgroundColor && cs.backgroundColor!=='rgba(0, 0, 0, 0)') bg.push(cs.backgroundColor);
    if (cs.color) color.push(cs.color);
    if (cs.fontFamily) fonts.push(cs.fontFamily.split(',')[0].replace(/["']/g,'').trim());
  });
  // 標題 vs 內文 字級/行高
  const sizeOf = (sel) => {
    const e = document.querySelector(sel); if(!e) return null;
    const cs = getComputedStyle(e);
    return { fontFamily: cs.fontFamily.split(',')[0].replace(/["']/g,'').trim(),
             fontSize: cs.fontSize, lineHeight: cs.lineHeight, fontWeight: cs.fontWeight,
             letterSpacing: cs.letterSpacing };
  };
  // 由上而下的主要區塊
  const blocks = Array.from(document.querySelectorAll('header,nav,section,main,footer,[class*=hero],[class*=section]'))
    .map(e => {
      const r = e.getBoundingClientRect();
      return { tag: e.tagName.toLowerCase(),
               cls: (e.className && e.className.toString ? e.className.toString().slice(0,80) : ''),
               y: Math.round(r.top + window.scrollY), h: Math.round(r.height) };
    })
    .filter(b => b.h > 40)
    .sort((a,b)=>a.y-b.y)
    .slice(0, 40);
  // 素材與動效類型(只列清單,不下載)
  const assets = {
    images: document.querySelectorAll('img').length,
    videos: document.querySelectorAll('video').length,
    svgs: document.querySelectorAll('svg').length,
    canvas: document.querySelectorAll('canvas').length,
    lottie: document.querySelectorAll('[class*=lottie],lottie-player,dotlottie-player').length,
    iframes: document.querySelectorAll('iframe').length,
  };
  const libs = {
    three: !!(window.THREE) || !!document.querySelector('canvas[data-engine],canvas'),
    gsap: !!(window.gsap || window.ScrollTrigger),
    framerMotion: !!document.querySelector('[data-framer-name],[style*="transform"]'),
  };
  return {
    palette_bg: freq(bg), palette_text: freq(color),
    fonts: freq(fonts),
    typography: { h1: sizeOf('h1'), h2: sizeOf('h2'), body: sizeOf('p') },
    sections: blocks, assets, libs,
    title: document.title,
    viewport: { w: window.innerWidth, h: window.innerHeight,
                docHeight: document.body.scrollHeight },
  };
}
"""


def main():
    ap = argparse.ArgumentParser(description="擷取參考網站的設計語言(靈感用,非照抄)")
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", default="design-ref.json")
    ap.add_argument("--screenshot", default="design-ref.png")
    ap.add_argument("--wait", type=int, default=3000, help="載入後等待毫秒(讓動畫/字體就緒)")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("ERROR: 未安裝 playwright。請執行:pip install playwright && playwright install chromium")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        try:
            page.goto(args.url, wait_until="networkidle", timeout=60000)
        except Exception:
            page.goto(args.url, timeout=60000)
        page.wait_for_timeout(args.wait)
        # 緩慢捲到底觸發 lazy / 進場動畫,再回頂端
        try:
            page.evaluate("""async () => {
              await new Promise(r => { let y=0; const t=setInterval(()=>{ y+=600; window.scrollTo(0,y);
                if (y >= document.body.scrollHeight) { clearInterval(t); r(); } }, 100); });
            }""")
            page.wait_for_timeout(800)
            page.evaluate("window.scrollTo(0,0)")
        except Exception:
            pass

        data = page.evaluate(JS_COLLECT)
        data["url"] = args.url
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        try:
            page.screenshot(path=args.screenshot, full_page=True)
        except Exception as e:
            print("（截圖失敗,可忽略）", e)
        browser.close()

    print(f"完成:設計語言 brief → {args.out};截圖 → {args.screenshot}")
    print("下一步:把這兩個檔給 Claude Code,請它『參考設計語言、用 Next.js+Tailwind+shadcn 重建並換成你的主題』。")
    print("⚠️ 只取設計語言當靈感,不要照抄或盜用對方素材/品牌。")


if __name__ == "__main__":
    main()
