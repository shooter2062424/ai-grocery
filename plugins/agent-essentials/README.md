# agent-essentials

> 用 AI Agent 就一定要裝的那一包。

Claude Code 預設會做事,但輸出往往是一整面的 markdown 流水帳。這個 plugin 把「怎麼講」跟「產出什麼」補起來:
一組可切換的**輸出風格**,加上一組把結果變成**可讀文件/簡報**的能力。

## 內含(本體)

| 類型 | 名稱 | 用途 |
|---|---|---|
| output-style | `eli5` | 全程用「解釋給指定對象聽」的方式回答:先白話結論與類比,再依對象深度補細節。`/output-style eli5` 啟用。 |
| skill | `eli5` | 同樣的解釋框架,但只在單次請求觸發(說「ELI5」「解釋給我媽聽」「dumb it down」時)。 |
| skill | `humanizer-zh-tw` | 去除文字裡的 AI 生成痕跡(誇大象徵、宣傳語言、破折號過度、三段式法則、否定式排比…),繁中版。 |
| skill | `html-artifacts` | 該用版面/顏色/圖表/互動說清楚的內容,產出自帶樣式的單檔 HTML,而不是 markdown。 |

output-style 與 skill 版的 `eli5` 差別:**風格是整個 session 都套用,skill 是單次觸發**。想全程講白話就切風格;偶爾一句「這段 ELI5 一下」就靠 skill。

## 相依 plugin(自動一起安裝)

以下四個是獨立維護的外部 plugin,已寫在本 plugin `plugin.json` 的 `dependencies` 裡,
安裝 agent-essentials 時 Claude Code 會自動把它們一起裝好、一起啟用:

| Plugin | 來源 | 用途 |
|---|---|---|
| `caveman` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 穴居人講話模式,實測砍約 65% 輸出 token,技術準確度不變。 |
| `mattpocock-skills` | [mattpocock/skills](https://github.com/mattpocock/skills) | 工程工作流:grilling、TDD、code review、domain modeling、writing-for-agents。 |
| `taste-skill` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 前端設計美感:brutalist / minimalist / soft / redesign / stitch 與 image-to-code。 |
| `open-kimi-ppt` | [shooter2062424/open-kimi-ppt-skill](https://github.com/shooter2062424/open-kimi-ppt-skill) | 以 PPTD 格式做簡報:建立/編輯/仿製/匯出,產出可編輯專案 + 內嵌字型的 .pptx。 |

四個都以裸字串宣告(跟著上游最新版走),且都在同一個 marketplace,所以不需要 git tag 或跨 marketplace 允許清單。

## 安裝

在終端機:

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過改用:claude plugin marketplace update ai-grocery
claude plugin install agent-essentials@ai-grocery         # 四個相依會一起裝進來
claude plugin list                                        # 確認五個都在
```

`caveman` 靠 SessionStart hook 生效,安裝後要重開一個 session。

相依若沒被拉進來(marketplace 沒加、被停用、解析失敗),在 session 內跑 `/agent-essentials:setup` 排查修復。

## 更新

```bash
claude plugin marketplace update            # 先更新 marketplace 清單(不指名 = 全部)
claude plugin update agent-essentials       # 再更新本 plugin

# 連相依一起更新(claude plugin update 一次只吃一個名字,所以用迴圈)
# PowerShell:
claude plugin list --json | ConvertFrom-Json | ForEach-Object { $_.id.Split('@')[0] } | Select-Object -Unique | ForEach-Object { claude plugin update $_ }
# bash:
claude plugin list --json | jq -r '.[].id | split("@")[0]' | sort -u | xargs -n1 claude plugin update
```

更新完要重開 session 才會套用。非 Anthropic 的 marketplace 預設不自動更新,
想讓它自己跟上就在 `/plugin` 介面把 ai-grocery 的 auto-update 打開。

注意:vendored 的 `eli5` / `humanizer-zh-tw` / `html-artifacts` 是隨本 plugin 一起更新的,
上游 repo 有新版時要手動重抓再 commit,`claude plugin update` 不會幫你同步上游。

## 用法速查

```
/output-style eli5          # 整個 session 講白話
/output-style default       # 切回預設
「把這段 humanize 一下」      # 觸發 humanizer-zh-tw
「幫我寫一份 X 的 writeup」   # 觸發 html-artifacts,產出單檔 HTML
「做一份 X 的簡報」           # 觸發 open-kimi-ppt,產出 .pptd + .pptx
```

## 來源與授權

`skills/eli5` 取自 [dreambigou/eli5](https://github.com/dreambigou/eli5);`output-styles/eli5.md` 由該 skill 改寫成 output-style 並中文化。
`skills/humanizer-zh-tw` 取自 [kevintsai1202/Humanizer-zh-TW](https://github.com/kevintsai1202/Humanizer-zh-TW)(其上游為 op7418/humanizer-zh、blader/humanizer)。
`skills/html-artifacts` 取自 [dogum/html-artifacts](https://github.com/dogum/html-artifacts)。
以上三者原專案皆為 MIT,內嵌於此僅為讓一次安裝就能用;上游更新需手動同步。
