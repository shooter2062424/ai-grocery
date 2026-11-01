# 格式參考

## specflow.json

```json
{
  "spec_dirs": ["specs"],
  "code_dirs": ["src"],
  "test_dirs": ["tests"],
  "protected": ["tests/golden/**", "vendor/oracle/**"],
  "contracts": "specs/contracts.json",
  "gates": ["python -m unittest discover -s tests -q"],
  "state_dir": ".specflow"
}
```

- `protected`:凍結基準的 glob(fnmatch,相對於專案根)。`guard` 規定它們不得與程式在同一變更修改。
- `gates`:全部 exit 0 才算過;`mutate` 用它判斷突變有沒有被抓到。

## 規格條目

```markdown
## R-MR-03 · 鄰區上限
- kind: external          # external | internal | decision | question(預設依前綴:R-外部、D-決策、Q-問題)
- owner: rrc-team
- status: active          # active | draft | deprecated | open/resolved(question)
- release: 21             # 選填,版本軸
- depends: R-MR-01, D-INT-02
- constants: NEIGH_MAX=16, NEIGH_BITS   # NAME=值:check 會比對程式中的定義;只寫名稱 = 僅受保護(決策項用)

系統 SHALL 最多處理 NEIGH_MAX 筆鄰區。
```

- ID 格式:`大寫英數-…`,例如 `R-AUTH-01`、`D-INT-02`、`Q-007`、`REQ-12`。
- 屬性必須緊接標題之後、連續的 `- key: value` 行;之後是自由文字。
- 條目的 hash = 標題+屬性+內文(去行尾空白)。改任何一個字,`check` 會對已 stamp 的條目回報 `STALE`,直到複查後重新 stamp。
- `constants` 比對支援 `NAME = 值`、`NAME: 值`、`#define NAME 值`、`const int NAME = 值;` 等常見寫法;複雜表達式不比對。

## 程式與測試標註

```python
# @spec R-MR-03                 ← 實作處(任何語言的註解)
def accept(count): ...

// @covers R-MR-03, D-INT-02    ← 測試(可多個,逗號分隔)

# @uses Report.delay, Report.power   ← 此處讀取契約 Report 的欄位
```

## 契約檔 specs/contracts.json

見 `contracts.md`。

## SPEC QUESTION

`specflow question` 會在 `specs/questions.md` 追加:

```markdown
## Q-003 · 空 beam 清單與缺欄位是否等價
- kind: question
- status: open
- owner: rrc-team
- refs: R-MR-04

假設(在人回答前暫用): 兩者等價,編碼端一律省略空清單。
```

回答後把 `status` 改為 `resolved` 並在內文寫決議,必要時回頭修改被引用的需求。
