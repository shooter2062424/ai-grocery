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

## 相依 plugin(marketplace 宣告,分開安裝)

以下四個是獨立維護的外部 plugin,已宣告在 `ai-grocery` marketplace 裡,所以 marketplace 加過一次就能直接裝:

| Plugin | 來源 | 用途 |
|---|---|---|
| `caveman` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 穴居人講話模式,實測砍約 65% 輸出 token,技術準確度不變。 |
| `mattpocock-skills` | [mattpocock/skills](https://github.com/mattpocock/skills) | 工程工作流:grilling、TDD、code review、domain modeling、writing-for-agents。 |
| `taste-skill` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 前端設計美感:brutalist / minimalist / soft / redesign / stitch 與 image-to-code。 |
| `open-kimi-ppt` | [shooter2062424/open-kimi-ppt-skill](https://github.com/shooter2062424/open-kimi-ppt-skill) | 以 PPTD 格式做簡報:建立/編輯/仿製/匯出,產出可編輯專案 + 內嵌字型的 .pptx。 |

裝完 agent-essentials 後,執行 `/agent-essentials:setup` 會一次把這四個裝齊並驗證。

## 安裝

在終端機:

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過改用:claude plugin marketplace update ai-grocery
claude plugin install agent-essentials@ai-grocery
claude plugin list                                        # 確認裝好了
```

再進 Claude Code session 執行一次 `/agent-essentials:setup` 補齊相依,它等同於:

```bash
claude plugin install caveman@ai-grocery
claude plugin install mattpocock-skills@ai-grocery
claude plugin install taste-skill@ai-grocery
claude plugin install open-kimi-ppt@ai-grocery
```

`caveman` 靠 SessionStart hook 生效,安裝後要重開一個 session。

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
