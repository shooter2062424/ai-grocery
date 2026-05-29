# claude_marketplace

shooter2062424 的 **Claude Code plugin marketplace** —— 收錄各類給 Claude 用的 skills / hooks / commands / agents,集中管理、方便安裝與分享。

## 架構

採 **multi-plugin marketplace**:一個 marketplace 底下可掛多個 plugin,各 plugin 依類別獨立,可分別安裝、各自演進。

```
claude_marketplace/
├─ .claude-plugin/
│  └─ marketplace.json          # marketplace 清單(列出所有 plugin)
└─ plugins/
   └─ knowledge-tools/          # 知識/學習類工具
      ├─ .claude-plugin/
      │  └─ plugin.json         # plugin manifest
      └─ skills/
         └─ rapid-learning/
            └─ SKILL.md         # NotebookLM 三提問快速學習法
```

## 目前收錄的 plugin

| Plugin | 內容 |
|---|---|
| **knowledge-tools** | 知識與學習類工具。目前含 `rapid-learning` skill(NotebookLM 三提問快速學習法:抽取核心心智模型 → 畫出領域爭議 → 用理解型問題自我檢驗)。 |

## 安裝方式

在 Claude Code 中:

```
# 1. 加入這個 marketplace(只需一次)
/plugin marketplace add shooter2062424/claude_marketplace

# 2. 安裝想要的 plugin
/plugin install knowledge-tools@claude_marketplace
```

之後若新增其他 plugin,使用者再各別 `/plugin install <plugin>@claude_marketplace` 即可。

## 慣例

- **新的「給 Claude 用」的 skill / hook / command / agent** 一律放進這個 repo(依類別歸到對應 plugin,沒有對應類別就新增一個 plugin 並更新 `marketplace.json`)。
- 知識整理類的 **report** 則放到 Knowledge(knowledgedb)倉庫,不放這裡。
