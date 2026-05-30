# claude_marketplace

**Claude Code plugin marketplace** —— 收錄各類給 Claude 用的 skills / hooks / commands / agents,集中管理、方便安裝與分享。

## 架構

採 **multi-plugin marketplace**:一個 marketplace 底下可掛多個 plugin,各 plugin 依類別獨立,可分別安裝、各自演進。

```
claude_marketplace/
├─ .claude-plugin/
│  └─ marketplace.json              # marketplace 清單(列出所有 plugin)
└─ plugins/
   ├─ knowledge-tools/              # 知識/學習類工具
   │  ├─ .claude-plugin/plugin.json
   │  └─ skills/rapid-learning/SKILL.md
   └─ investing-like-pro/           # 投資類工具
      ├─ .claude-plugin/plugin.json
      └─ skills/gooaye/
         ├─ SKILL.md                  # 用股癌投資思維框架評斷一支股票好不好
         ├─ scripts/
         │  ├─ fetch_indicators.py    # 撈他看重的指標(台股 FinMind / 美股 yfinance)
         │  └─ build_memory.py        # 從逐字稿建立近期立場記憶(輔助層,可重跑)
         └─ references/
            ├─ investment-framework.md  # 【核心大腦】評斷準則:分型→七維度→紅旗→verdict
            ├─ recent-stance.md         # 近期立場(輔助層)
            ├─ recency-ranking.md       # 近期加權排名 + 升溫/退燒(輔助層)
            ├─ ranking.json / mention-timeline.json
            └─ methodology.md
```

## 目前收錄的 plugin

| Plugin | 內容 |
|---|---|
| **knowledge-tools** | 知識與學習類工具。目前含 `rapid-learning` skill(NotebookLM 三提問快速學習法)。 |
| **investing-like-pro** | 投資類工具。含 `gooaye`(用股癌數百集 podcast 萃取的「投資思維框架」評斷一支股票好不好:分型→估值→基本面→題材純度→護城河→預期差→循環紀律→風控,並動態撈他看重的指標;近期推薦只當輕度輔助)。**教育用途,非投資建議。** |
| **finance** | 金融/交易類工具。含 `ctbc-securities-api`(用 Python+pywin32 操作中國信託證券交易 API:登入/下單/查詢/回報,含 headless client 與回傳解析腳本)。**涉及真實下單與真錢,務必先用測試環境;非投資建議。** |
| **web-design-tools** | 前端/網頁設計類工具。目前含 `modern-web-design` skill(Next.js+Tailwind+shadcn/ui 做現代網站:突破 AI 預設風格、捲動逐幀動畫管線、設計參考擷取、依受眾拆設計策略;含 ffmpeg 拆幀與 Playwright 擷取腳本)。 |

## 安裝方式

在 Claude Code 中:

```
# 1. 加入這個 marketplace(只需一次;後面是 GitHub repo 路徑)
/plugin marketplace add shooter2062424/claude_marketplace

# 2. 安裝想要的 plugin(@ 後面是 marketplace 名稱 bigdaddy-marketplace)
/plugin install knowledge-tools@bigdaddy-marketplace
/plugin install investing-like-pro@bigdaddy-marketplace
/plugin install finance@bigdaddy-marketplace
/plugin install web-design-tools@bigdaddy-marketplace
```

> 註:`marketplace add` 後面用的是 **GitHub repo 路徑**(`shooter2062424/claude_marketplace`),
> 而 `/plugin install <plugin>@...` 的 `@` 後面用的是 **marketplace 名稱**(`bigdaddy-marketplace`,
> 定義在 `.claude-plugin/marketplace.json` 的 `name`)。兩者不同,別搞混。

之後若新增其他 plugin,使用者再各別 `/plugin install <plugin>@bigdaddy-marketplace` 即可。

## 慣例

- **新的「給 Claude 用」的 skill / hook / command / agent** 一律放進這個 repo(依類別歸到對應 plugin,沒有對應類別就新增一個 plugin 並更新 `marketplace.json`)。
- 知識整理類的 **report** 則放到 Knowledge(knowledgedb)倉庫,不放這裡。
