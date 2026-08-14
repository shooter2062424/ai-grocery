# ai-grocery

**Claude Code plugin marketplace** —— 收錄各類給 Claude 用的 skills / hooks / commands / agents,集中管理、方便安裝與分享。

## 架構

採 **multi-plugin marketplace**:一個 marketplace 底下可掛多個 plugin,各 plugin 依類別獨立,可分別安裝、各自演進。

```
ai-grocery/
├─ .claude-plugin/
│  └─ marketplace.json              # marketplace 清單(列出所有 plugin)
└─ plugins/
   ├─ agent-essentials/             # 「用 AI Agent 一定要裝的那一包」:輸出風格 + 文件/簡報產出
   │  ├─ .claude-plugin/plugin.json
   │  ├─ output-styles/eli5.md      # 整個 session 講白話(解釋給指定對象聽)
   │  ├─ commands/setup.md          # /agent-essentials:setup 一次補齊相依 plugin
   │  └─ skills/
   │     ├─ eli5/                   # 單次觸發版的 ELI5 解釋
   │     ├─ humanizer-zh-tw/        # 去除文字的 AI 生成痕跡(繁中)
   │     └─ html-artifacts/         # 該用版面說清楚的內容 → 單檔 HTML
   ├─ knowledge-tools/              # 知識/學習類工具
   │  ├─ .claude-plugin/plugin.json
   │  └─ skills/rapid-learning/SKILL.md
   └─ investing-like-pro/           # 投資類工具
      ├─ .claude-plugin/plugin.json
      ├─ agents/                    # subagents(.md;委派時機寫在 frontmatter description)
      │  ├─ gooaye.md               # 用股癌投資思維框架評斷一支股票
      │  ├─ google-nexus.md         # 用 Google Nexus 五代理人框架做時序預測
      │  └─ valuation-bands.md      # 用 EPS×本益比歷史分位判 特價/便宜/合理/昂貴/瘋狂
      ├─ gooaye/                    # gooaye agent 的資源(用 ${CLAUDE_PLUGIN_ROOT} 取用)
      │  ├─ scripts/                #   fetch_indicators.py / build_memory.py
      │  └─ references/             #   investment-framework.md / recent-stance / ranking…
      ├─ google-nexus/             # google-nexus agent 的資源
      │  ├─ scripts/fetch_series.py
      │  └─ references/nexus-framework.md
      ├─ valuation-bands/          # valuation-bands agent 的資源
      │  ├─ scripts/pe_bands.py     #   EPS×PE 歷史分位 → 五檔價 + 現價判定
      │  └─ references/methodology.md
      └─ skills/trading-math/       # 交易贏家數學 skill(期望值/變異數/風險)
         └─ scripts/trading_math.py #   期望值/breakeven/復原/部位大小/破產風險 Monte Carlo
```

## 目前收錄的 plugin

| Plugin | 內容 |
|---|---|
| **agent-essentials** | 「用 AI Agent 就一定要裝的那一包」。**Output style**:`eli5`(整個 session 都用解釋給指定對象聽的方式回答)。**Skills**:`eli5`(單次觸發版)、`humanizer-zh-tw`(去除文字的 AI 生成痕跡)、`html-artifacts`(該用版面/圖表說清楚的內容改產出單檔 HTML)。**Command**:`/agent-essentials:setup`。另以 marketplace 宣告四個相依 plugin(下方四列),裝完跑一次 setup 就全齊。 |
| ↳ **caveman** | agent-essentials 相依,來源 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)。穴居人講話模式,實測砍約 65% 輸出 token,技術準確度不變(靠 SessionStart hook,裝完要重開 session)。 |
| ↳ **mattpocock-skills** | agent-essentials 相依,來源 [mattpocock/skills](https://github.com/mattpocock/skills)。工程工作流 skills:grilling、TDD、code review、domain modeling、writing-for-agents 等。 |
| ↳ **taste-skill** | agent-essentials 相依,來源 [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)。前端設計美感:brutalist / minimalist / soft / redesign / stitch 與 image-to-code。 |
| ↳ **open-kimi-ppt** | agent-essentials 相依,來源 [shooter2062424/open-kimi-ppt-skill](https://github.com/shooter2062424/open-kimi-ppt-skill)。以 PPTD 格式做簡報的建立/編輯/仿製/匯出,產出可編輯專案 + 內嵌字型的 .pptx。 |
| **knowledge-tools** | 知識與學習類工具。目前含 `rapid-learning` skill(NotebookLM 三提問快速學習法)。 |
| **investing-like-pro** | 投資類工具。**Agents**:`gooaye`(用股癌數百集 podcast 萃取的「投資思維框架」評斷一支股票好不好)、`google-nexus`(用 Google Nexus 五代理人框架做未來 N 日走勢預測+可解釋推理)、`valuation-bands`(用 EPS×本益比歷史分位把股價判成 特價/便宜/合理/昂貴/瘋狂 五檔)。**Skill**:`trading-math`(用期望值/系統設計/變異數/風險四大交易數學概念評斷一套交易系統會不會賺、能不能活久,反推部位大小、破產風險、復原數學,含 Python 計算腳本)。**教育用途,非投資建議。** |
| **finance** | 金融/交易類工具。含 `ctbc-securities-api`(用 Python+pywin32 操作中國信託證券交易 API:登入/下單/查詢/回報,含 headless client 與回傳解析腳本)。**涉及真實下單與真錢,務必先用測試環境;非投資建議。** |
| **web-design-tools** | 前端/網頁設計類工具。目前含 `modern-web-design` skill(Next.js+Tailwind+shadcn/ui 做現代網站:突破 AI 預設風格、捲動逐幀動畫管線、設計參考擷取、依受眾拆設計策略;含 ffmpeg 拆幀與 Playwright 擷取腳本)。 |

## 安裝方式

在終端機執行(`claude plugin` CLI):

```bash
# 1. 加入這個 marketplace(只需一次;後面是 GitHub repo 路徑)
claude plugin marketplace add shooter2062424/ai-grocery

# 2. 安裝想要的 plugin(@ 後面是 marketplace 名稱)
claude plugin install agent-essentials@ai-grocery
claude plugin install knowledge-tools@ai-grocery
claude plugin install investing-like-pro@ai-grocery
claude plugin install finance@ai-grocery
claude plugin install web-design-tools@ai-grocery

# 3. 確認裝好了
claude plugin list
```

已經加過 marketplace 的話,新增的 plugin 要先更新清單才看得到:

```bash
claude plugin marketplace update ai-grocery
```

> 註:GitHub repo 名與 marketplace 名稱已統一為 `ai-grocery`(`marketplace add` 用 repo 路徑、
> `plugin install <plugin>@` 用 marketplace 名稱,兩者現在同名)。
> ⚠️ marketplace 名稱 **不可含 "claude"**,否則會觸發 Claude Code「仿冒官方 marketplace」防衛而被擋。
> 在 Claude Code session 內也可以用對應的 `/plugin marketplace add …` / `/plugin install …` 斜線指令。

之後若新增其他 plugin,使用者再各別 `claude plugin install <plugin>@ai-grocery` 即可。

### agent-essentials 的相依

Claude Code 的 plugin 目前沒有正式的 dependency 欄位,所以這裡用兩層做法:
外部相依(`caveman`、`mattpocock-skills`、`taste-skill`、`open-kimi-ppt`)一律**宣告在本 marketplace 的 `plugins` 陣列**,
指向各自的 GitHub repo;安裝 agent-essentials 後執行一次 `/agent-essentials:setup`,就會把四個一起裝好。

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過改用 marketplace update ai-grocery
claude plugin install agent-essentials@ai-grocery
```

再進 Claude Code session 執行一次 `/agent-essentials:setup`,它等同於幫你跑:

```bash
claude plugin install caveman@ai-grocery
claude plugin install mattpocock-skills@ai-grocery
claude plugin install taste-skill@ai-grocery
claude plugin install open-kimi-ppt@ai-grocery
```

`caveman` 靠 SessionStart hook 生效,裝完要重開一個 session。

不是 plugin 形式(只有一個 SKILL.md、或只能用 `npx skills add` / `git clone` 安裝)的來源,
則直接 vendored 進 `plugins/agent-essentials/skills/` 並在該 plugin 的 README 標註來源與授權。

## 慣例

- **新的「給 Claude 用」的 skill / hook / command / agent** 一律放進這個 repo(依類別歸到對應 plugin,沒有對應類別就新增一個 plugin 並更新 `marketplace.json`)。
- 知識整理類的 **report** 則放到 Knowledge(knowledgedb)倉庫,不放這裡。
