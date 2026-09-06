# ai-grocery

**Claude Code plugin marketplace** —— 收錄各類給 Claude 用的 skills / hooks / commands / agents,集中管理、方便安裝與分享。

## 架構

採 **multi-plugin marketplace**:一個 marketplace 底下可掛多個 plugin,各 plugin 依類別獨立,可分別安裝、各自演進。

```
ai-grocery/
├─ CLAUDE.md                        # 給 Claude 的維護指南(怎麼把別人的 repo 整合進來)
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
   ├─ viz-tools/                    # 圖解與圖表(vendored:archify、lieflat-charts;相依:diagram-design)
   │  ├─ .claude-plugin/plugin.json
   │  └─ skills/
   │     ├─ archify/                # 架構/時序/資料流/狀態機圖 → 可探索單檔 HTML+SVG
   │     └─ lieflat-charts/         # 模板驅動的 HTML 圖表與 12 套整頁報告
   ├─ content-tools/                # 內容寫作產線(vendored:四個 content-skills)
   │  ├─ .claude-plugin/plugin.json
   │  └─ skills/
   │     ├─ viral-hooks/            # 開頭第一句 / 前兩秒鉤子
   │     ├─ storytelling/           # 口說與故事型內容的留人結構
   │     ├─ dumbify/                # 降低閱讀門檻與心智負擔
   │     └─ anti-ai-writing/        # 最後一道去 AI 味的濾網
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
| **agent-essentials** | 「用 AI Agent 就一定要裝的那一包」。**Output style**:`eli5`(整個 session 都用解釋給指定對象聽的方式回答)。**Skills**:`eli5`(單次觸發版)、`humanizer-zh-tw`(去除文字的 AI 生成痕跡)、`html-artifacts`(該用版面/圖表說清楚的內容改產出單檔 HTML)。**Command**:`/agent-essentials:setup`(相依沒生效時排查用)。以 `plugin.json` 的 `dependencies` 宣告四個相依 plugin(下方四列),**安裝時自動一起裝**。 |
| ↳ **caveman** | agent-essentials 相依,來源 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)。穴居人講話模式,實測砍約 65% 輸出 token,技術準確度不變(靠 SessionStart hook,裝完要重開 session)。 |
| ↳ **mattpocock-skills** | agent-essentials 相依,來源 [mattpocock/skills](https://github.com/mattpocock/skills)。工程工作流 skills:grilling、TDD、code review、domain modeling、writing-for-agents 等。 |
| ↳ **taste-skill** | agent-essentials 相依,來源 [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)。前端設計美感:brutalist / minimalist / soft / redesign / stitch 與 image-to-code。 |
| ↳ **viz-tools** | agent-essentials 相依(本 marketplace)。圖解與圖表,見下方獨立列。 |
| ↳ **content-tools** | agent-essentials 相依(本 marketplace)。內容寫作產線,見下方獨立列。 |
| ↳ **open-kimi-ppt** | agent-essentials 相依,來源 [shooter2062424/open-kimi-ppt-skill](https://github.com/shooter2062424/open-kimi-ppt-skill)。以 PPTD 格式做簡報的建立/編輯/仿製/匯出,產出可編輯專案 + 內嵌字型的 .pptx。 |
| **knowledge-tools** | 知識與學習類工具。目前含 `rapid-learning` skill(NotebookLM 三提問快速學習法)。 |
| **investing-like-pro** | 投資類工具。**Agents**:`gooaye`(用股癌數百集 podcast 萃取的「投資思維框架」評斷一支股票好不好)、`google-nexus`(用 Google Nexus 五代理人框架做未來 N 日走勢預測+可解釋推理)、`valuation-bands`(用 EPS×本益比歷史分位把股價判成 特價/便宜/合理/昂貴/瘋狂 五檔)。**Skill**:`trading-math`(用期望值/系統設計/變異數/風險四大交易數學概念評斷一套交易系統會不會賺、能不能活久,反推部位大小、破產風險、復原數學,含 Python 計算腳本)。**教育用途,非投資建議。** |
| **finance** | 金融/交易類工具。含 `ctbc-securities-api`(用 Python+pywin32 操作中國信託證券交易 API:登入/下單/查詢/回報,含 headless client 與回傳解析腳本)。**涉及真實下單與真錢,務必先用測試環境;非投資建議。** |
| **web-design-tools** | 前端/網頁設計類工具。目前含 `modern-web-design` skill(Next.js+Tailwind+shadcn/ui 做現代網站:突破 AI 預設風格、捲動逐幀動畫管線、設計參考擷取、依受眾拆設計策略;含 ffmpeg 拆幀與 Playwright 擷取腳本)。 |
| **career-tools** | 職涯類工具。目前含 `interview-personality` skill(面試的個人特質 / cultural fit 題:用 Trait → Behaviour → Evidence 三層公式,把 hardworking / team player 這種跟所有人都一樣的形容詞,換成讓面試官看得見「跟你工作是什麼體驗」的具體畫面;從事件回推特質,並針對職位重排順序)。 |
| **viz-tools** | 資料視覺化與圖解。**Skills**:`archify`(架構圖/工作流程圖/時序圖/資料流圖/狀態機 → 可探索的單檔 HTML + inline SVG,深淺色主題、路徑動畫、可匯出 PNG/JPEG/WebP/SVG/WebM,也吃貼上的 Mermaid、也能讀 repo 照真實程式碼畫)、`lieflat-charts`(模板驅動的 HTML 圖表與 12 套中英文整頁報告,Mono 灰階保底並依資料語義自動選色)。**相依**:`diagram-design`。⚠️ `lieflat-charts` 為 **PolyForm Noncommercial** 授權,僅限非商業用途。 |
| ↳ **diagram-design** | viz-tools 相依,來源 [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)。品牌化圖表:架構、流程、時序、狀態機、ER/資料模型、時間軸、泳道、象限、雷達、漏斗、樹狀、組織圖、Sankey、魚骨、Wardley map、使用者旅程等數十種版型,輸出 HTML/SVG/PNG,可從網站擷取品牌 token、重畫 .drawio 與 Mermaid。 |
| **content-tools** | 內容創作寫作產線,四個 skill 各守一段:`viral-hooks`(開頭第一句 / 影片前兩秒 / 電子報標題 —— 同時要有主題清晰與精準好奇)、`storytelling`(口說與故事型內容,把「停下來」變成「看完」)、`dumbify`(降到約八年級閱讀水準,簡單的語言而非簡單的想法)、`anti-ai-writing`(最後一道濾網,目標是聽起來像一個具體的人而不是「不像 AI」)。以英文寫作為主;繁中請用 agent-essentials 的 `humanizer-zh-tw`。 |

## 收錄的別人精華

這個 repo 有一部分是**站在別人肩膀上**:社群裡寫得很好的 plugin / skill,收進來讓它們能跟自製的東西一起被一行指令裝好。
收錄方式分兩種 —— **外部參照**(對方本身就是 plugin,只在 `marketplace.json` 指向原 repo,程式碼永遠是上游最新版)、
**vendored 收錄**(對方只有一份 SKILL.md 沒有 plugin 形式,複製進來並在此標註來源)。

### 外部參照(自動跟上游最新版)

| 來源 | 原作者 | 收進來當什麼 | 精華在哪 |
|---|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | JuliusBrussee | `caveman` plugin,`agent-essentials` 相依 | 穴居人講話模式。砍掉冠詞、贅字、客套與鋪陳,只留技術內容,實測省約 65% 輸出 token 而準確度不變。分 lite / full / ultra 與文言文變體,靠 SessionStart hook 全程生效。 |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Matt Pocock | `mattpocock-skills` plugin,`agent-essentials` 相依 | 一整套工程工作流:`grilling`(逼問你的計畫直到站得住腳)、`tdd`(red-green-refactor)、`code-review`(標準面 + 規格面雙軸審查)、`domain-modeling`、`writing-for-agents`(怎麼寫 CLAUDE.md 跟 skill)、`diagnosing-bugs`。 |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | Leonxlnx | `taste-skill` plugin,`agent-essentials` 相依 | 前端美感的解毒劑。把「一看就是 AI 做的」那種預設風格擋掉,提供 brutalist / minimalist / high-end / redesign / stitch 等明確設計方向,外加 image-to-code 與圖像生成的設計參考流程。 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | Cathryn Lavery | `diagram-design` plugin,`viz-tools` 相依 | 品牌化的圖表工廠。數十種版型(架構、流程、時序、狀態機、ER、時間軸、泳道、象限、雷達、漏斗、樹狀、組織圖、Sankey、魚骨、Wardley map、使用者旅程…)配上可從網站擷取的品牌 token,輸出 HTML / SVG / PNG,還能把既有的 .drawio 與 Mermaid 重畫成同一套視覺。 |
| [shooter2062424/open-kimi-ppt-skill](https://github.com/shooter2062424/open-kimi-ppt-skill) | shooter2062424 | `open-kimi-ppt` plugin,`agent-essentials` 相依 | 用 PPTD 格式做簡報的建立 / 編輯 / 仿製 / 匯出,產出的是**可編輯的專案資料夾**加上內嵌字型的 `.pptx`,不是一次性的死檔。 |

外部參照的好處:上游更新,你這邊 `claude plugin update` 就跟上,不用等這個 repo 同步。

### Vendored 收錄(複製進來,已標註來源)

這些上游只提供 `SKILL.md`(安裝方式是 `npx skills add` 或 `git clone` 後手動複製),沒有 plugin manifest 可以被 marketplace 參照,所以複製進來。
一律在**該 plugin 的 README** 的「收錄來源」段落標註原作者、原 repo 與授權條款;上游有 LICENSE 的隨 skill 目錄一起附上,沒有的以上游 repo 為準。
vendored 時唯一的修改是在 `SKILL.md` frontmatter 的 `description` 後面**附加**繁中觸發詞,讓中文提問也叫得動;原文一字未動。

| Skill | 原作者 | 原 repo | 授權 | 放在 | 精華在哪 |
|---|---|---|---|---|---|
| `archify` | tt-a1i | [tt-a1i/archify](https://github.com/tt-a1i/archify) | MIT | `viz-tools` | 不是輸出一張死圖,而是**可探索的單檔 HTML + inline SVG**:深淺色主題、可選的路徑追蹤動畫、一鍵匯出 PNG/SVG/WebM。吃自然語言,也吃你貼上的 Mermaid,要畫真實系統時會去讀 repo 對照。 |
| `lieflat-charts` | 躺在廢墟裡([moxt.ai](https://moxt.ai)) | [larashero3-dotcom/lieflat-charts](https://github.com/larashero3-dotcom/lieflat-charts) | **PolyForm Noncommercial 1.0.0** | `viz-tools` | 圖表**品味**法典。模板全部來自真實實作的 gallery(Lupi / Basics / Glance / Maps / Interactive)加 12 套中英文整頁報告;Mono 灰階保底,依資料語義自動選色,同一份交付不准混色系 —— 它管的不只是畫得出來,是畫得好看。 |
| `viral-hooks` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT | `content-tools` | 鉤子只有一個任務:讓**對的人**決定繼續看。必須同時給主題清晰 + 精準好奇,缺一個就滑掉。 |
| `storytelling` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT | `content-tools` | 鉤子賺到前兩秒,敘事賺到後面每一秒。六個技巧撐住口說 / 故事型內容的中段。 |
| `dumbify` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT | `content-tools` | 人不是因為內容太淺而離開,是因為**跟上太費力**。降到約八年級閱讀水準,簡單的語言不是簡單的想法。 |
| `anti-ai-writing` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT | `content-tools` | 目標不是「不要像 AI」—— 追著否定跑只會得到一片米色。目標是聽起來像一個真的想過這件事、而且有話要說的**具體的人**。 |
| `humanizer-zh-tw` | kevintsai1202(上游 op7418/humanizer-zh、blader/humanizer) | [kevintsai1202/Humanizer-zh-TW](https://github.com/kevintsai1202/Humanizer-zh-TW) | 見上游 repo | `agent-essentials` | 繁中版的去 AI 味:誇大象徵、宣傳語言、破折號過度、三段式法則、否定式排比,一條條抓出來改掉。 |
| `html-artifacts` | dogum | [dogum/html-artifacts](https://github.com/dogum/html-artifacts) | 見上游 repo | `agent-essentials` | 判斷「這件事該用版面講」而不是硬塞 markdown,然後產出自帶樣式的單檔 HTML。 |

上游授權不明或明確禁止再散布的,不 vendored,只在文件放連結。

> ⚠️ **`lieflat-charts` 例外:PolyForm Noncommercial 只允許非商業用途。** 拿它產出的圖表或報告做客戶交付、對外銷售或營利產品前,請先向原作者取得授權;公開分發其產出時請署名。同 plugin 的 `archify` 是 MIT,沒有這個限制。

> 所有外部內容的著作權屬於各自作者,依其原授權條款使用。這裡只做整合與中文化說明。

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
claude plugin install career-tools@ai-grocery
claude plugin install viz-tools@ai-grocery
claude plugin install content-tools@ai-grocery

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

## 更新

分兩層:**marketplace 清單**(有哪些 plugin、指到哪個 repo)和**已安裝的 plugin 本身**。

```bash
# 1. 更新所有 marketplace 的清單(不指名就是全部)
claude plugin marketplace update

# 2. 更新單一 plugin
claude plugin update agent-essentials

# 3. 更新全部已安裝的 plugin(claude plugin update 一次只吃一個名字,所以用迴圈)
#    PowerShell:
claude plugin list --json | ConvertFrom-Json | ForEach-Object { $_.id.Split('@')[0] } | Select-Object -Unique | ForEach-Object { claude plugin update $_ }
#    bash:
claude plugin list --json | jq -r '.[].id | split("@")[0]' | sort -u | xargs -n1 claude plugin update
```

更新完要**重開 session** 才會套用。

> ⚠️ `claude plugin update agent-essentials` **不等於連相依一起更新**。
> 官方文件保證的是:更新 bundle 本身,以及 bundle 新版若「多宣告了一個相依」,`/reload-plugins` 後會把那個**新增的**相依裝進來。
> 至於既有相依(caveman 等)會不會順帶升到最新,文件沒有明說,所以別依賴它 —— 用上面第 3 點的迴圈逐一更新,
> 或直接開 auto-update(auto-update 會更新**所有**已安裝 plugin,自動安裝的相依也算在內)。

其他有用的:

```bash
claude plugin list --json     # 有問題的 plugin 會多一個 errors 欄位(乾淨的沒有)
claude plugin prune           # 清掉已經沒有任何 plugin 需要的自動安裝相依
claude plugin details <name>  # 看某個 plugin 帶進來哪些元件、吃多少 token
```

> 非 Anthropic 的 marketplace **預設不自動更新**。想讓 ai-grocery 自動跟上,
> 在 session 內開 `/plugin` 介面把該 marketplace 的 auto-update 打開,之後新版(含 bundle 新增的相依)會自己裝進來。

### agent-essentials 的相依

`agent-essentials` 是一個 **bundle plugin**:它在 `plugin.json` 的 `dependencies` 宣告四個相依,
安裝時 Claude Code 會自動把它們一起裝好、一起啟用。

```json
// plugins/agent-essentials/.claude-plugin/plugin.json
"dependencies": ["caveman", "mattpocock-skills", "taste-skill", "open-kimi-ppt"]
```

所以使用者只要一行:

```bash
claude plugin install agent-essentials@ai-grocery
```

兩個前提都已經滿足,不用額外設定:

- **同 marketplace**:`dependencies` 的名字預設在宣告者所屬的 marketplace 解析,而這四個都已列在本 marketplace 的
  `plugins` 陣列(各自 `source` 指向原 GitHub repo),所以不需要 `allowCrossMarketplaceDependenciesOn`。
- **不綁版本**:四個都用裸字串宣告(跟著上游最新版走),因此不需要上游打 `{name}--v{version}` git tag。
  哪天要把某個相依鎖在測過的版本,再改成 `{ "name": "caveman", "version": "~1.2.0" }`,那時上游才必須有對應 tag。

裝完 `caveman` 靠 SessionStart hook 生效,要**重開一個 session**。
若相依沒被拉進來(marketplace 沒加、被停用、解析失敗),在 session 內跑 `/agent-essentials:setup` 排查修復。
相關指令:`claude plugin list --json` 看 `errors` 欄位、`claude plugin prune` 清掉已無人需要的自動安裝相依。

不是 plugin 形式(只有一個 SKILL.md、或只能用 `npx skills add` / `git clone` 安裝)的來源,
則直接 vendored 進 `plugins/agent-essentials/skills/` 並在該 plugin 的 README 標註來源與授權。

## 慣例

- **新的「給 Claude 用」的 skill / hook / command / agent** 一律放進這個 repo(依類別歸到對應 plugin,沒有對應類別就新增一個 plugin 並更新 `marketplace.json`)。
- 知識整理類的 **report** 則放到 Knowledge(knowledgedb)倉庫,不放這裡。

## 給 Claude 的維護指南

要新增 / 整合 plugin 或 skill 的完整流程(判斷外部參照還是 vendored、類別怎麼歸、每次要一起更新哪些檔案、
驗證與 commit 慣例)寫在根目錄的 [`CLAUDE.md`](./CLAUDE.md)。

實務上使用者只要把別人的 repo 連結或安裝指令貼進 session,Claude Code 讀到 `CLAUDE.md` 就會照那份流程
把東西整合進來,並同步更新 `marketplace.json`、兩層 README 與這一頁的「收錄的別人精華」。
