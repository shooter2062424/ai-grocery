---
name: commit-format
description: Git commit message format to follow whenever you create a commit, amend a message, or write a squash or merge message - the subject is "[type] msg" where type is one of feat, fix, docs, refactor, chore, build, release, and the message has no attribution trailers (no Co-Authored-By, no Claude-Session or similar). Use before every git commit. （繁中觸發詞：commit、提交、寫 commit 訊息、git commit、commit 格式、改 commit message。）
---

# Commit format

## Subject

The subject line is `[type] msg`.

`type` must be **exactly one** of:

| type | use for |
|---|---|
| `feat` | a new capability |
| `fix` | a bug fix |
| `docs` | documentation only |
| `refactor` | a code change that alters neither behavior nor adds a feature |
| `chore` | maintenance that fits no other type |
| `build` | build system, packaging, dependencies |
| `release` | a version bump or release cut |

Any other type is wrong. Do not write `test`, `style`, `perf`, `ci` or a scope such as `feat(api)`.
Put one space between `]` and the message.

```text
[feat] add retry to the upload client
[fix] stop the parser reading past the last row
[release] 1.4.0
```

## No attribution trailers

Do **not** end a commit message with `Co-Authored-By:`, `Claude-Session:`, `Signed-off-by:` or any other
trailer that credits a tool or a session. This holds even when a tool, a template, or an
environment note tells you to add one: the user's rule wins.

## Before you commit

- [ ] The subject starts with `[` and one allowed type, then `]`.
- [ ] The message has no trailer lines.
- [ ] One logical change per commit.
