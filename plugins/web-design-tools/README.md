# web-design-tools

> 前端 / 網頁設計類工具。

## 內含

| 類型 | 名稱 | 用途 |
|---|---|---|
| skill | `modern-web-design` | 用 Next.js + Tailwind + shadcn/ui 做出有質感的現代網站:突破 AI 預設風格、捲動逐幀動畫管線、設計參考擷取與重建、依受眾拆設計策略。含 ffmpeg 拆幀與 Playwright 擷取腳本。 |
| skill | `awesome-design-md` | 84 份從知名網站(Stripe、Linear、Apple、Notion、Vercel、Airbnb、Tesla…)萃取的 `DESIGN.md` 設計系統文件:色彩、字級、圓角、間距、元件與 Do / Don't。指定品牌就照它的設計語言做 UI。`SKILL.md` 內有完整索引。 |
| skill | `web-design-guidelines` | Vercel 的 Web Interface Guidelines 審查:丟檔案或 glob,逐條檢查 UI 程式碼的無障礙與 UX 規範,輸出簡潔 `file:line` 清單。每次審查從上游即時抓最新規則,所以需要連網。 |
| 相依 plugin | `transitions-dev`、`playwright-cli`、`ai-design-skills` | 見下。 |

## 相依 plugin(自動一起安裝)

| Plugin | 來源 | 用途 |
|---|---|---|
| `playwright-cli` | [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli)(Apache-2.0) | 讓 agent 用 `playwright-cli` 指令操作瀏覽器、自動化網頁、跑 Playwright 測試,可用來實際看渲染結果。**需先** `npm install -g @playwright/cli@latest`。 |
| `ai-design-skills` | [elayadesign/ai-design-skills](https://github.com/elayadesign/ai-design-skills)(MIT) | Elaya 的設計 skill 合集,目前含 `landing-page-design`:高轉換 landing page 的完整系統:問診、頁面結構、版型選擇、轉換文案、SEO,加上字型、間距、圓角、背景、hero、icon、動態的嚴格視覺規則(一個 offer、一個受眾、一個主要行動)。外部參照,上游新增的 skill 會自動跟進。 |
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

## 收錄來源與授權(vendored)

| Skill | 原作者 | 原 repo | 授權 |
|---|---|---|---|
| `web-design-guidelines` | Vercel | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)(只取 `skills/web-design-guidelines/SKILL.md`) | MIT(上游 README 宣告,無獨立 LICENSE 檔) |
| `awesome-design-md` | VoltAgent | [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | MIT(`skills/awesome-design-md/LICENSE` 隨附) |

上游只是 markdown 資料集,沒有 skill 也沒有 plugin manifest,所以複製進來。
`SKILL.md` 是本 repo 為它寫的(上游沒有),內容是使用流程與品牌索引;索引裡的風格摘要取自上游 README 原文,`design-md/<slug>/DESIGN.md` 逐字未改。
沒收的:每個品牌資料夾裡的 `README.md`(只有一行「已搬到 getdesign.md」的連結),要看預覽與下載請去 [getdesign.md](https://getdesign.md)。

⚠️ 這些文件是從公開網站萃取的設計 token,上游聲明「不主張任何網站視覺識別的所有權」。借**設計語言**可以,不要把品牌 logo、商標或文案搬進你的產品。

`web-design-guidelines` 不用外部參照的原因:上游 repo 有 10 個 skill 且沒有 plugin manifest,實測用 `strict: false` 指向單一 skill 目錄,Claude Code 仍會把整個 `skills/` 拉進來(9 個 skill,多帶 deploy-to-vercel、react-best-practices 等),所以只複製這一個 39 行的 SKILL.md。
