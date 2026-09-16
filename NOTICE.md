# NOTICE — 授權清單

這個 repo 是 **MIT**（見 [`LICENSE`](./LICENSE)），但**只蓋自己寫的部分**。
裡面也收了別人寫的 skill，那些檔案**維持原授權，不因為 MIT 而被重新授權**。

這份清單逐一列出每個元件屬於哪一種。

## 一、本 repo 自己的工作 — MIT

Copyright (c) 2026 shooter2062424

- `.claude-plugin/marketplace.json`
- 每個 plugin 的 `.claude-plugin/plugin.json`
- `README.md`、`CLAUDE.md`、各 plugin 的 `README.md`
- 自製的 skills / agents / commands / output-styles：
  - `plugins/agent-essentials/output-styles/eli5.md`
  - `plugins/agent-essentials/commands/setup.md`
  - `plugins/agent-essentials/skills/eli5/`
  - `plugins/knowledge-tools/skills/rapid-learning/`
  - `plugins/career-tools/skills/interview-personality/`
  - `plugins/finance/skills/ctbc-securities-api/`
  - `plugins/web-design-tools/skills/modern-web-design/`
  - `plugins/investing-like-pro/`（agents、scripts、references、`skills/trading-math/`）

## 二、Vendored 第三方 skill — 各自原授權

檔案實際複製在本 repo 內，授權以原作者為準。

| 路徑 | 原作者 | 原 repo | 授權 |
|---|---|---|---|
| `plugins/viz-tools/skills/archify/` | tt-a1i | [tt-a1i/archify](https://github.com/tt-a1i/archify) | MIT（`LICENSE` 隨附；上游基於 Cocoon-AI/architecture-diagram-generator，MIT） |
| `plugins/viz-tools/skills/lieflat-charts/` | 躺在廢墟裡（[moxt.ai](https://moxt.ai)） | [larashero3-dotcom/lieflat-charts](https://github.com/larashero3-dotcom/lieflat-charts) | **PolyForm Noncommercial License 1.0.0**（`LICENSE` 隨附） |
| `plugins/content-tools/skills/viral-hooks/` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT（`LICENSE` 隨附） |
| `plugins/content-tools/skills/storytelling/` | Artem Novitckii | 同上 | MIT（`LICENSE` 隨附） |
| `plugins/content-tools/skills/dumbify/` | Artem Novitckii | 同上 | MIT（`LICENSE` 隨附） |
| `plugins/content-tools/skills/anti-ai-writing/` | Artem Novitckii | 同上 | MIT（`LICENSE` 隨附） |
| `plugins/knowledge-tools/skills/game-theory-skill/` | peterfei | [peterfei/forge-skill-game-theory-skill](https://github.com/peterfei/forge-skill-game-theory-skill) | MIT（上游宣告於 `package.json` 與 README，未附獨立 LICENSE 檔） |
| `plugins/agent-essentials/skills/humanizer-zh-tw/` | kevintsai1202 | [kevintsai1202/Humanizer-zh-TW](https://github.com/kevintsai1202/Humanizer-zh-TW) | 以上游 repo 為準（上游再上游：op7418/humanizer-zh、blader/humanizer） |
| `plugins/agent-essentials/skills/html-artifacts/` | dogum | [dogum/html-artifacts](https://github.com/dogum/html-artifacts) | 以上游 repo 為準 |

### ⚠️ 非商業限制

**`lieflat-charts` 是 PolyForm Noncommercial License 1.0.0，只允許非商業用途。**

要拿它產出的圖表或報告做客戶交付、對外銷售或營利產品，請先向原作者取得授權。
上游另外要求：公開分發用它產生的內容時請署名或標註開發者。

同一個 plugin 裡的 `archify` 是 MIT，沒有這個限制。

### Vendored 時做過的修改

只有一處：在 `SKILL.md` frontmatter 的 `description` **結尾附加**一行繁中觸發詞，
讓中文提問也能觸發。正文、術語、程式碼一字未動。

為控制 repo 體積，部分執行時用不到的檔案未收錄（`archify` 的 `test/` 與
`package-lock.json`、`lieflat-charts` 的 `docs/`）。要看完整內容請到上游 repo。

## 三、外部參照 — 不在本 repo 內

這些只在 `marketplace.json` 存一筆指向上游的指標，**本 repo 不含它們任何檔案**，
安裝時 Claude Code 直接從上游抓。授權完全由上游決定，本 repo 的 MIT 與它們無關。

| Plugin | 原作者 | 來源 |
|---|---|---|
| `caveman` | JuliusBrussee | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) |
| `mattpocock-skills` | Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) |
| `taste-skill` | Leonxlnx | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| `open-kimi-ppt` | shooter2062424 | [shooter2062424/open-kimi-ppt-skill](https://github.com/shooter2062424/open-kimi-ppt-skill) |
| `diagram-design` | Cathryn Lavery | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) |
| `transitions-dev` | Jakub Antalik | [Jakubantalik/transitions.dev](https://github.com/Jakubantalik/transitions.dev) |

### ⚠️ transitions-dev 的授權邊界

上游 [Terms & License](https://transitions.dev/terms.html)：**允許**用在無限個人與商業專案、
自由修改、隨產品出貨；**禁止**把這套集合本身重新打包、轉售或發布成競品
（"you can't repackage, resell, or publish the collection (or a substantial part of it)
as a competing transitions library, template pack, or component kit"）。

這也是它走外部參照而不是 vendored 的原因 —— 本 repo 收的是指標，不是內容。
上游 repo 裡的 MIT 只蓋 Refine 工具與 CLI，**不蓋 transitions 本身**。
Pro transitions 需另行付費（`npx transitions-dev login`）。

## 四、有問題請告知

如果你是上面任何一份作品的作者，認為這裡的收錄方式或標註有誤，
請開 issue 或直接聯絡，我會立刻修正或移除。
