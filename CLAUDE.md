# CLAUDE.md — ai-grocery 維護指南

這個檔案給 Claude Code 看。裡面寫的是「使用者丟一個別人的 repo / skill / plugin 過來時，
要怎麼把它整合進 ai-grocery」的標準流程，以及這個 repo 的慣例。

## 這個 repo 是什麼

一個 **Claude Code multi-plugin marketplace**。使用者用兩行指令就能裝：

```bash
claude plugin marketplace add shooter2062424/ai-grocery
claude plugin install <plugin>@ai-grocery
```

目錄結構：

```
.claude-plugin/marketplace.json   # marketplace 清單：列出所有 plugin（本地的 + 外部 GitHub 來源的）
plugins/<plugin-name>/
  .claude-plugin/plugin.json      # 該 plugin 的 manifest
  README.md                       # 該 plugin 的說明（含來源標註）
  skills/<skill-name>/SKILL.md    # skills
  agents/<agent>.md               # subagents
  commands/<cmd>.md               # slash commands
  output-styles/<style>.md        # output styles
  hooks/                          # hooks
docs/research/                    # 研究/知識整理輸出（非 plugin 內容）
```

## 核心任務：使用者貼一個 repo 或安裝指令過來

使用者常常只丟一句「這個幫我整合進 ai-grocery」加上一段安裝指令或 GitHub 連結。
**預設就是要做整合，不用再問要不要做。** 照下面流程走。

### 第 0 步：先看清楚來源是什麼型態

去看它的 repo 根目錄，判斷屬於哪一類：

| 判斷依據 | 型態 | 整合方式 |
|---|---|---|
| 有 `.claude-plugin/plugin.json` | 單一 plugin | **外部參照**（不要複製檔案） |
| 有 `.claude-plugin/marketplace.json` | 別人的 marketplace | 外部參照；若對方一個 marketplace 掛多個 plugin，挑使用者要的那幾個逐一列 |
| 只有 `SKILL.md`（或 `skills/` 但沒 manifest） | 裸 skill | **vendored 收錄**（複製進來） |
| 安裝方式是 `npx skills add …` / `git clone …` / 手動複製到 `~/.claude/skills` | 裸 skill | **vendored 收錄** |
| 安裝方式是 `claude plugin marketplace add X` + `claude plugin install Y@X` | plugin | **外部參照** |

分不出來時，以「對方 repo 有沒有 plugin manifest」為準。有 manifest 就外部參照，沒有就 vendored。

### 路線 A：外部參照（對方是 plugin）

不要把對方的檔案複製進來。改成在 `marketplace.json` 的 `plugins` 陣列加一筆 github 來源：

```json
{
  "name": "<上游 plugin 的 name，要跟對方 plugin.json 的 name 一致>",
  "source": { "source": "github", "repo": "<owner>/<repo>" },
  "description": "<中文說明；若是某個 bundle 的相依就在開頭寫「<bundle> 相依。」>"
}
```

如果這個東西屬於某個 bundle plugin（目前只有 `agent-essentials`），
再到該 plugin 的 `plugin.json` 把名字加進 `dependencies` 陣列：

```json
"dependencies": ["caveman", "mattpocock-skills", "taste-skill", "open-kimi-ppt", "<新的>"]
```

規則：

- **用裸字串宣告**（跟上游最新版走）。要鎖版本才改成 `{ "name": "x", "version": "~1.2.0" }`，
  但那需要上游有 `{name}--v{version}` 的 git tag，沒有就別鎖。
- 相依名字預設在**本 marketplace** 解析，所以被宣告成 dependency 的 plugin **一定也要列在
  `marketplace.json` 的 `plugins` 裡**，否則解析不到。這也是為什麼不需要 `allowCrossMarketplaceDependenciesOn`。
- 上游 plugin 的 `name` 不能跟本 repo 已有的 plugin 撞名。撞名就改用 vendored 路線，或請使用者決定。

### 路線 B：vendored 收錄（對方只是 skill）

1. 選一個**類別 plugin** 放（見下方類別表）。沒有合適的類別就新建一個 plugin。
2. 複製到 `plugins/<類別>/skills/<skill-name>/`，保留 `SKILL.md`、`scripts/`、`references/`、`assets/`。
3. **不要改寫上游的 `SKILL.md` 內容。** 唯一允許的修改是在 frontmatter `description` 的**結尾附加**一段
   繁中觸發詞，格式：`（繁中觸發詞：…、…、…。）`。
   理由：`description` 是 Claude 決定要不要載入這個 skill 的唯一依據，上游的英文描述通常已經調校過，
   整段翻掉會讓英文提問叫不動；只附加中文線索則兩邊都吃得到。正文與術語一律保持原文。
4. skill 內部引用檔案一律用 `${CLAUDE_PLUGIN_ROOT}` 開頭的路徑，不要用相對路徑或絕對路徑。
5. **一定要標註來源與授權**：在該 plugin 的 `README.md` 的「收錄來源」表格加一列，寫上
   原作者、原 repo 連結、授權條款。上游有 LICENSE 就把它一併複製到 skill 目錄下。
6. **先看授權再決定要不要 vendored**：
   - MIT / Apache-2.0 / BSD 之類的寬鬆授權 → 直接 vendored，附上 LICENSE。
   - **非商業授權**（PolyForm Noncommercial 等）→ 可以 vendored，但必須在**該 plugin 的 README
     與根目錄 README 兩處**用 `⚠️` 明確標出「僅限非商業用途」，並附上原 LICENSE 全文。
   - 授權不明或明確禁止再散布 → **不要 vendored**，改成在 README 只放連結，並告訴使用者原因。
7. **控制體積**：跑測試用的 `test/`、`package-lock.json`、純截圖的 `docs/assets/` 這類執行時用不到的東西不要收，
   並在 plugin README 註明「哪些沒收、要看請去上游」。

### 第 2 步：類別歸屬

現有 plugin 的守備範圍：

| Plugin | 收什麼 |
|---|---|
| `agent-essentials` | 「用 AI Agent 一定要裝的那一包」：輸出風格、講話方式、文件/簡報產出、通用工作流。也是唯一的 bundle（用 `dependencies` 帶外部 plugin）。 |
| `knowledge-tools` | 知識、學習、研究方法類 |
| `investing-like-pro` | 投資分析、選股、估值、交易數學（教育用途） |
| `finance` | 券商 API、下單、金融系統串接 |
| `web-design-tools` | 前端、網頁設計、UI 實作 |
| `career-tools` | 職涯、面試、履歷、職場溝通 |

都不合就**新增一個 plugin**：建 `plugins/<name>/.claude-plugin/plugin.json`（照現有格式：
`name` / `description` / `version` / `author` / `keywords`）、寫 `README.md`、
並在 `marketplace.json` 的 `plugins` 加一筆 `"source": "./plugins/<name>"`。

### 第 3 步：每次整合都要一起更新的東西

**這步不可跳過。** 少更新任何一項就算沒做完：

1. `.claude-plugin/marketplace.json` — 新來源 / 新 plugin 的那一筆
2. `plugins/<plugin>/.claude-plugin/plugin.json` — `dependencies`、`keywords`、必要時升 `version`
3. `plugins/<plugin>/README.md` — 內容表格 + **收錄來源表格（原作者 / repo / 授權）**
4. 根目錄 `README.md` — 「目前收錄的 plugin」表格、「安裝方式」的指令清單，以及
   **「收錄的別人精華」章節**（統一列出所有外部來源與原作者，這是給人看的致謝與追溯）
5. 本檔案 `CLAUDE.md` — 只有在流程本身改變時才要動

### 第 4 步：驗證

```bash
# JSON 一定要能 parse
python3 -c "import json,glob;[json.load(open(f)) for f in ['.claude-plugin/marketplace.json']+glob.glob('plugins/*/.claude-plugin/plugin.json')];print('ok')"

# 每個 skill 都要有 frontmatter 的 name 與 description
grep -L '^description:' plugins/*/skills/*/SKILL.md
```

檢查清單：

- [ ] `marketplace.json` 每個 `source` 指到真的存在的路徑或 repo
- [ ] `dependencies` 裡的每個名字都出現在 `marketplace.json` 的 `plugins`
- [ ] 每個 vendored skill 都有來源與授權標註
- [ ] 兩層 README 都更新了
- [ ] 沒有把使用者的私人資料、API key、token 寫進任何檔案
- [ ] 沒有把上游的 `.git/` 目錄複製進來
- [ ] 非商業授權的內容已經在兩層 README 標出 `⚠️`

### 第 5 步：commit 與 push

- 一次整合 = 一個 commit。
- 訊息格式沿用現有慣例：`[feat] 新增 <plugin> plugin 與 <skill> skill`、
  `[feat] agent-essentials 新增相依 <name>`、`[docs] …`、`[chore] …`。
- Commit 訊息用**正常中文**寫，不要用壓縮風格。
- push 到使用者指定的分支，用 `git push -u origin <branch>`。
- **不要自己開 PR**，除非使用者明講要。

## 慣例

- **所有「給 Claude 用」的東西**（skill / hook / command / agent / output-style）一律進這個 repo。
- **知識整理型的報告**放 Knowledge(knowledgedb) 倉庫，不放這裡。
  例外：跟本 repo 直接相關的技術研究可放 `docs/research/`。
- marketplace 名稱**不可含 "claude"**，會觸發 Claude Code 的「仿冒官方 marketplace」防衛而被擋。
- 面向使用者的說明文字用**繁體中文**；指令、路徑、程式碼、API 名稱保持原文。
- 投資 / 金融類內容一律附上「教育用途，非投資建議」。
- 不要為了整合去改上游 plugin 的行為；要改就 fork 或做成自己的 skill，並在 README 說明差異。
