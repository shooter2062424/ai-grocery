# ai-grocery

**Claude Code plugin marketplace** —— 收錄各類給 Claude 用的 skills / hooks / commands / agents,集中管理、方便安裝與分享。

## 架構

採 **multi-plugin marketplace**:一個 marketplace 底下可掛多個 plugin,各 plugin 依類別獨立,可分別安裝、各自演進。

```
ai-grocery/
├─ .claude-plugin/
│  └─ marketplace.json              # marketplace 清單(列出所有 plugin)
└─ plugins/
   ├─ knowledge-tools/              # 知識/學習類工具
   │  ├─ .claude-plugin/plugin.json
   │  └─ skills/rapid-learning/SKILL.md
   └─ investing-like-pro/           # 投資類工具
      ├─ .claude-plugin/plugin.json
      ├─ agents/                    # subagents(.md;委派時機寫在 frontmatter description)
      │  ├─ gooaye.md               # 用股癌投資思維框架評斷一支股票
      │  └─ google-nexus.md         # 用 Google Nexus 五代理人框架做時序預測
      ├─ gooaye/                    # gooaye agent 的資源(用 ${CLAUDE_PLUGIN_ROOT} 取用)
      │  ├─ scripts/                #   fetch_indicators.py / build_memory.py
      │  └─ references/             #   investment-framework.md / recent-stance / ranking…
      └─ google-nexus/             # google-nexus agent 的資源
         ├─ scripts/fetch_series.py
         └─ references/nexus-framework.md
```

## 目前收錄的 plugin

| Plugin | 內容 |
|---|---|
| **knowledge-tools** | 知識與學習類工具。目前含 `rapid-learning` skill(NotebookLM 三提問快速學習法)。 |
| **investing-like-pro** | 投資類工具(皆為 **agents**)。含 `gooaye`(用股癌數百集 podcast 萃取的「投資思維框架」評斷一支股票好不好:分型→估值→基本面→題材純度→護城河→預期差→循環紀律→風控,動態撈指標;近期推薦只當輕度輔助)與 `google-nexus`(用 Google Nexus 五代理人框架做未來 N 日走勢預測+可解釋推理)。**教育用途,非投資建議。** |
| **finance** | 金融/交易類工具。含 `ctbc-securities-api`(用 Python+pywin32 操作中國信託證券交易 API:登入/下單/查詢/回報,含 headless client 與回傳解析腳本)。**涉及真實下單與真錢,務必先用測試環境;非投資建議。** |
| **web-design-tools** | 前端/網頁設計類工具。目前含 `modern-web-design` skill(Next.js+Tailwind+shadcn/ui 做現代網站:突破 AI 預設風格、捲動逐幀動畫管線、設計參考擷取、依受眾拆設計策略;含 ffmpeg 拆幀與 Playwright 擷取腳本)。 |

## 安裝方式

在 Claude Code 中:

```
# 1. 加入這個 marketplace(只需一次;後面是 GitHub repo 路徑)
/plugin marketplace add shooter2062424/ai-grocery

# 2. 安裝想要的 plugin(@ 後面是 marketplace 名稱)
/plugin install knowledge-tools@ai-grocery
/plugin install investing-like-pro@ai-grocery
/plugin install finance@ai-grocery
/plugin install web-design-tools@ai-grocery
```

> 註:GitHub repo 名與 marketplace 名稱已統一為 `ai-grocery`(`marketplace add` 用 repo 路徑、
> `/plugin install <plugin>@` 用 marketplace 名稱,兩者現在同名)。
> ⚠️ marketplace 名稱 **不可含 "claude"**,否則會觸發 Claude Code「仿冒官方 marketplace」防衛而被擋。

之後若新增其他 plugin,使用者再各別 `/plugin install <plugin>@ai-grocery` 即可。

## 慣例

- **新的「給 Claude 用」的 skill / hook / command / agent** 一律放進這個 repo(依類別歸到對應 plugin,沒有對應類別就新增一個 plugin 並更新 `marketplace.json`)。
- 知識整理類的 **report** 則放到 Knowledge(knowledgedb)倉庫,不放這裡。
