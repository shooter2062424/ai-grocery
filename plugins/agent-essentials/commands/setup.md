---
description: 檢查 agent-essentials 的相依 plugin 是否都裝好了,缺的補裝
allowed-tools: Bash
---

# 檢查 / 修復 agent-essentials 的相依

`agent-essentials` 在 `plugin.json` 的 `dependencies` 宣告了四個相依 plugin,安裝時 Claude Code 會**自動**把它們一起裝好,
正常情況不需要跑這個指令。它是用來排查「裝了但沒生效」的狀況:相依被停用、marketplace 沒加、或安裝當下解析失敗。

## 步驟

1. 先看現況:

```bash
claude plugin list --json
```

檢查這五個是否都在且 enabled:`agent-essentials`、`caveman`、`mattpocock-skills`、`taste-skill`、`open-kimi-ppt`。
載入有問題的 plugin 會帶 `errors` 欄位,乾淨的則沒有這個欄位。

2. 依照看到的狀況處理,並向使用者說明你做了什麼:

- **相依沒裝**(`dependency-unsatisfied`):先確認 marketplace 有加,再重跑安裝讓它重新解析相依。

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過會顯示 already exists,可忽略
claude plugin install agent-essentials@ai-grocery
```

- **相依裝了但被停用**:啟用它。啟用 `agent-essentials` 會連帶啟用相依。

```bash
claude plugin enable agent-essentials@ai-grocery
```

- **marketplace 清單太舊**(裝不到新加的 plugin):

```bash
claude plugin marketplace update ai-grocery
```

3. 最後在 session 內執行 `/reload-plugins` 讓變更生效,並提醒使用者:

- `caveman` 靠 SessionStart hook 生效,要**重開一個 session**。
- 用 `/output-style eli5` 切換到 ELI5 輸出風格,`/output-style default` 切回。

不要為了「保險」而重跑一遍全部安裝指令;只處理實際有問題的那幾個。
