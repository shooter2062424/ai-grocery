---
description: 安裝 agent-essentials 的所有相依 plugin(caveman / mattpocock-skills / taste-skill / open-kimi-ppt)
allowed-tools: Bash
---

# 安裝 agent-essentials 的相依 plugin

agent-essentials 本體已內含 `eli5` output-style、`eli5` / `humanizer-zh-tw` / `html-artifacts` 三個 skill。
其餘四個能力來自外部 repo,以獨立 plugin 形式安裝。它們全部都已宣告在 `ai-grocery` marketplace 裡,
所以只要 marketplace 加過一次,就能直接裝,不需要再逐一 `marketplace add`。

請依序執行下列指令,每一步都回報結果;若某一步失敗,說明失敗原因再繼續下一步,不要中斷整批安裝。

```bash
# 若尚未加入 marketplace(已加過會顯示 already exists,可忽略)
claude plugin marketplace add shooter2062424/ai-grocery

claude plugin install caveman@ai-grocery
claude plugin install mattpocock-skills@ai-grocery
claude plugin install taste-skill@ai-grocery
claude plugin install open-kimi-ppt@ai-grocery
```

裝完後執行 `claude plugin list` 確認這五個 plugin 都在:
`agent-essentials`、`caveman`、`mattpocock-skills`、`taste-skill`、`open-kimi-ppt`。

最後提醒使用者:
- 用 `/output-style eli5` 切換到 ELI5 輸出風格,`/output-style default` 切回。
- caveman 靠 SessionStart hook 生效,安裝後需要重開一個 session。
