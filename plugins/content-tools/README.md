# content-tools

> 一條內容產線：**鉤子 → 內文 → 好懂 → 去 AI 味。**

四個 skill 分別守一個環節，來自同一套 content-skills，設計上就是要串著用。

## 內含

| 類型 | 名稱 | 守哪一段 | 用途 |
|---|---|---|---|
| skill | `viral-hooks` | 開頭 | 開場一句、短影片前兩秒、輪播第一張、電子報標題、推文首句。核心主張：鉤子只有一個任務 —— 讓**對的人**決定繼續看。要同時給出「主題清晰」與「精準好奇」兩件事，缺一個就滑掉。 |
| skill | `storytelling` | 內文 | 口說 / 敘事型內容：短影片腳本、影片講稿、故事型貼文。鉤子換到前兩秒，敘事負責換到**看完**。六個技巧，前四個做大部分的工。純教學示範或沒有主線的清單文不適用。 |
| skill | `dumbify` | 好懂 | 降低閱讀門檻與心智負擔。目標約八年級閱讀水準（鉤子約六年級）。前提是「**簡單的語言，不是簡單的想法**」—— 人不是因為內容太淺而離開，是因為跟上太費力。 |
| skill | `anti-ai-writing` | 最後一關 | 每一篇的最終濾網。目標不是「不要像 AI」（追著否定跑只會得到一片米色），而是「聽起來像一個真的想過這件事、而且有話要說的具體的人」。具體性與聲音就是護城河。 |

搭配用法：先 `viral-hooks` 定開頭 → `storytelling` 撐住內文 → `dumbify` 壓低閱讀成本 → `anti-ai-writing` 收尾。

跟 `agent-essentials` 裡 `humanizer-zh-tw` 的分工：**`anti-ai-writing` 主要針對英文寫作，`humanizer-zh-tw` 針對繁體中文。** 兩個可以並存，寫哪個語言就用哪個。

## 收錄來源與授權

| Skill | 原作者 | 原 repo | 授權 |
|---|---|---|---|
| `viral-hooks` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT |
| `storytelling` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT |
| `dumbify` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT |
| `anti-ai-writing` | Artem Novitckii | [artemnovitckii/content-skills](https://github.com/artemnovitckii/content-skills) | MIT |

授權條款隨每個 skill 目錄附上（`skills/<name>/LICENSE`）。

vendored 的原因：上游是一個 skills 集合，不是 Claude Code plugin（安裝方式是 `git clone` 後手動複製到 `~/.claude/skills`），
沒有 `plugin.json` 可以被 marketplace 參照，所以複製進來並在此標註來源。

vendored 時做的唯一修改：在 `SKILL.md` frontmatter 的 `description` 後面**附加**繁中觸發詞。原文一字未動。

上游同一個 repo 裡的 `voice-dna` 目前未收錄（只有 README，沒有 `SKILL.md`）。

## 安裝

```bash
claude plugin marketplace add shooter2062424/ai-grocery   # 已加過改用:claude plugin marketplace update ai-grocery
claude plugin install content-tools@ai-grocery
```

裝 `agent-essentials` 的話這個 plugin 會被當相依一起帶進來，不用重複安裝。
