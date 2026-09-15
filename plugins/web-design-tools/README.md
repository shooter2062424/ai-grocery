# web-design-tools

> 前端 / 網頁設計類工具。

## 內含

| 類型 | 名稱 | 用途 |
|---|---|---|
| skill | `modern-web-design` | 用 Next.js + Tailwind + shadcn/ui 做出有質感的現代網站:突破 AI 預設風格、捲動逐幀動畫管線、設計參考擷取與重建、依受眾拆設計策略。含 ffmpeg 拆幀與 Playwright 擷取腳本。 |
| 相依 plugin | `transitions-dev` | 見下。 |

## 相依 plugin(自動一起安裝)

| Plugin | 來源 | 用途 |
|---|---|---|
| `transitions-dev` | [Jakubantalik/transitions.dev](https://github.com/Jakubantalik/transitions.dev) | 32 個可直接貼上的 CSS transition:modal 開關、dropdown、number pop-in、icon swap、success check、skeleton、shimmer、sliding tabs、tooltip、accordion、toast、like button、checkbox、toggle、streaming text、matrix loader、banner stacking…。每個都 namespaced 在 `t-*`、用語意化 CSS custom property,並附 `prefers-reduced-motion` guard,不綁 framework、不帶 demo 專用 markup。另含 `transitions-polish`,依 duration / distance / scale / blur / easing 五個維度校準既有動態(open/close 不對稱、hover in/out、stagger、intent delay)。 |

`modern-web-design` 管**整體設計策略與版面**,`transitions-dev` 管**單一元件怎麼動**。兩個搭著用。

## 關於 transitions-dev 的收錄方式與授權

這是**純外部參照**:`marketplace.json` 只存一筆指向上游 repo 的指標,
本 repo **不複製上游任何檔案**,安裝時 Claude Code 直接去 [Jakubantalik/transitions.dev](https://github.com/Jakubantalik/transitions.dev) 抓。
上游沒有 `plugin.json`,所以 marketplace entry 用 `"strict": false` + `"skills": ["./skills/"]` 自己描述元件。

⚠️ **授權限制**。上游 [Terms & License](https://transitions.dev/terms.html):

- **允許**:把 transition 用在**無限個人與商業專案**、自由修改、隨產品出貨給你的使用者。
- **禁止**:把這套集合本身重新打包散布 ——
  *"you can't repackage, resell, or publish the collection (or a substantial part of it) as a competing transitions library, template pack, or component kit."*

所以這裡走外部參照而不是 vendored:收錄的是指標,不是內容。
repo 裡的 MIT 只蓋 Refine 工具與 CLI,**不蓋 transitions 本身**。

Pro transitions(confetti burst、drag-drop physics 等)需另行付費:

```bash
npx transitions-dev login
```

## 安裝

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過改用:claude plugin marketplace update ai-grocery
claude plugin install web-design-tools@ai-grocery         # transitions-dev 會一起裝進來
```
