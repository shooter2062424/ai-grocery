# knowledge-tools

> 知識與學習類工具集：學習方法、思維框架。

## 內含

| 類型 | 名稱 | 用途 |
|---|---|---|
| skill | `rapid-learning` | NotebookLM 三提問快速學習法。 |
| skill | `game-theory-skill` | 博弈論(賽局理論)的結構化思維工具。基於 12 個一手來源的深度調研，提煉 6 個核心原理與完整操作協議：判斷局勢是不是博弈、找出參賽者與各自的策略空間、算不算零和、要不要先出手、對方會怎麼反應。適用於談判、競價/標案策略、產品定價、團隊博弈、任何「我這樣做,對方會怎麼反應」的情境。 |

## 收錄來源與授權

| Skill | 原作者 | 原 repo | 授權 |
|---|---|---|---|
| `game-theory-skill` | peterfei | [peterfei/forge-skill-game-theory-skill](https://github.com/peterfei/forge-skill-game-theory-skill) | MIT(見上游 `package.json`,上游 repo 本身未附獨立 `LICENSE` 檔) |

vendored 的原因：上游只有 `SKILL.md`,沒有 plugin manifest,不是 Claude Code plugin 形式。

vendored 時唯一的修改是在 `SKILL.md` frontmatter 的 `description` 結尾**附加**一行繁中觸發詞；原文(簡中)一字未動。

## 安裝

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過改用:claude plugin marketplace update ai-grocery
claude plugin install knowledge-tools@ai-grocery
```
