---
name: spec-code-flow
description: 規格與程式雙向同步的總入口(spec-to-code / code-to-spec)。當使用者要「依規格改程式」、「程式改了要回寫規格」、「規格變更會影響哪些程式與測試」、「查某條需求的實作與測試」、「建立/維護需求知識庫與追溯」、「多個模組或團隊靠介面(API、訊息、ILM、protobuf)溝通時怎麼一起改」時使用。會判斷情境並導向 init / change / sync / audit 子流程,並規定知識庫的讀取與更新方式。
---

# spec-code-flow:規格 ⇄ 程式 雙向工作流(總入口)

> 這套流程把「規格、程式、測試」用**追溯標註**綁成一個可查詢的知識庫。
> 規格或程式**任何一邊**變動,都能被偵測、算出影響、擋住危險捷徑,並在不確定時**升級給人決定**,而不是默默猜。
> 工具:`scripts/specflow.py`(Python 3.9+,只用標準函式庫,不綁任何資料庫產品)。
> 設計依據是實測(玩具規模,數字不可外推到真實系統),見 `references/evidence.md`。

## 一、先認清你在哪個情境

| 使用者說的 | 去哪 | 子 skill |
|---|---|---|
| 「這個專案要開始用規格管理」「幫我建需求清單與追溯」 | 建知識庫 | **spec-flow-init** |
| 「規格變了/新需求來了,改程式」「程式要改這個行為,規格要跟著改」「介面欄位要改」 | 變更流程 | **spec-flow-change** |
| 「程式被人改了,規格對得上嗎」「幫我檢查漂移」「從現有程式反推規格」 | 同步與回寫 | **spec-flow-sync** |
| 「我的測試夠不夠強」「關卡會漏掉什麼」 | 品質探測 | **spec-flow-audit** |
| 只是查「R-xx 在哪實作/誰負責/改它影響什麼」 | 直接用下面的查詢指令 | — |

專案裡還沒有 `specflow.json` ⇒ 先走 **spec-flow-init**。

## 二、知識庫長什麼樣(預設:repo 內檔案 + 產生的索引)

```text
specflow.json              設定:規格/程式/測試目錄、受保護路徑、關卡指令、契約檔
specs/*.md                 需求(R-*)、內部決策(D-*)、SPEC QUESTION(Q-*);每條有 ID、owner、狀態、依賴
specs/contracts.json       模組間介面契約(欄位的型別、單位、縮放、範圍、enum、預設值、順序、延遲)
src/**  程式                註解寫 `@spec R-001`;讀契約欄位處寫 `@uses Report.delay`
tests/** 測試               註解寫 `@covers R-001`
.specflow/index.json       【產生物】ID↔程式↔測試↔依賴↔契約使用者;每次指令自動重建,不手改
.specflow/stamps.json      【進版控】「程式已確認符合此版規格」的簽章(規格 hash)
```

**讀取(查詢)知識庫** — 不要自己 grep 全 repo 猜:

```bash
python <本 skill>/scripts/specflow.py query R-001            # 規格全文+程式位置+測試+依賴+被依賴+確認狀態
python <本 skill>/scripts/specflow.py query --text "retry 上限"  # 關鍵字找需求
python <本 skill>/scripts/specflow.py impact R-001 D-02       # 影響:傳遞依賴、程式檔、測試檔、該通知的 owner、牽涉的決策
python <本 skill>/scripts/specflow.py check                   # 漂移總檢
```

**更新知識庫的規則(誰、何時能寫)**

| 動作 | 誰 | 條件 |
|---|---|---|
| 改規格 `specs/*.md` | 依 owner 規定(外部公定規格視為唯讀,只在新版釋出時合併) | 改後必須跑 `impact`,規格 hash 一變,`check` 會標 STALE 直到程式複查 |
| 改程式標註 `@spec/@covers/@uses` | 改程式的人(agent 可以) | 標註指向的 ID 必須存在,`check` 會抓孤兒 |
| `stamp <ID>` | **只在驗證通過之後**(測試綠、`check` 無 ERROR、人已看過 HUMAN 項) | stamp 是「我確認過程式符合這版規格」的聲明,不是讓紅燈消失的按鈕 |
| 新增 `question` | agent 或人,遇到含糊/矛盾時**必須**用 | 見第四節 |
| `.specflow/index.json` | 工具自動 | 不手改、不 commit |

## 三、十條規則(每條都有實測依據,見 evidence.md)

1. **規格與程式在同一個變更裡一起改**,不要分兩次。漂移多半是「只改了一邊」。
2. **先算影響,再動手**:`impact` 的輸出是你的工作清單(要看的程式、要跑的測試、要通知的 owner)。
3. **先寫會失敗的測試**(spec-first):依新規格寫測試,先在舊程式上確認是紅的,再改程式。邊界值要寫(上限本身、上限+1、最大編碼值),這是實測最常漏的地方。
4. **凍結基準唯讀**:`protected` 路徑(golden vector、舊版輸出、外部 oracle)**不得與程式在同一個變更中修改**。「改程式再把 golden 改成一致」是最容易讓測試全綠的捷徑,`guard` 會擋。
5. **決策常數(`D-*` 的 `constants`)不得為了讓測試通過而調整**。改它要 owner 簽核,`guard` 會回傳「需人決定」。
6. **紅燈分兩類,別混**:退出碼 `1` = 壞掉了,你修;退出碼 `3` = 需要人決定,你停下來報告選項,不要自己選。
7. **規格含糊或矛盾 ⇒ 開 SPEC QUESTION**(`question` 指令):寫出假設、owner、關聯需求;在人回答前用假設繼續,並在最終回報標明。不要默默選一種。
8. **有舊版相容需求時,新舊並存**:新增欄位/新分支,舊的保留到確認沒人用才移除(見 references/contracts.md);不要就地改語意。
9. **跨模組介面的語意變更(單位、縮放、極性、基底、預設值)型別不變、schema diff 看不到**:一律用 `contract-diff` 分類,並用 `@uses` 標註找出 consumer。
10. **完成的定義**:`check` 無 ERROR ∧ 測試綠 ∧ `guard` 無違規 ∧ 沒有未回報的 HUMAN 項 ∧ 已 `stamp`。沒跑過就不能說完成。

## 四、誠實升級(最重要的行為)

遇到下列任一情況,**停止猜測**,執行 `question` 並在最終回報列出,不要靜默選擇:

- 兩條規格互相矛盾,或規格與既有測試矛盾。
- 規格沒定義的表示或邊界(空清單 vs 缺欄位、位元寬度、順序)。
- 要改動的數字屬於別的團隊(`D-*` 決策常數)。
- 程式與規格不一致,且看不出哪個才是意圖(例如規格 200、程式 150)。

回報格式:`SPEC QUESTION Q-xxx:問題 / 我採用的假設 / 影響範圍 / 建議 owner`。

## 五、指令速查

| 指令 | 用途 | 退出碼 |
|---|---|---|
| `init` | 建 specflow.json、specs/、範例 | 0 |
| `index` | 重建索引 | 0 |
| `check [--strict] [--verbose] [--untagged]` | 漂移總檢(孤兒標註、STALE、常數不符、依賴錯、未解決問題) | 0 / 1 / 3 |
| `query <ID…>` / `query --text <詞>` | 查知識庫 | 0 |
| `impact [ID…]` | 影響分析(不給 ID = 用「規格已變」的項目) | 0 |
| `stamp <ID…>` / `stamp --all` | 簽章確認 | 0 |
| `question "標題" --assume "假設" --owner x --refs R-1` | 開 SPEC QUESTION | 0 |
| `guard [--base REF]` | 護欄:凍結基準、決策常數 | 0 / 1 / 3 |
| `contract-diff old.json new.json` | 契約語意 diff + 受影響 consumer | 0 / 3 |
| `mutate -n 30` | 關卡品質探測(在暫存副本注入突變) | 0 / 3 |

詳細格式:`references/formats.md`;介面契約與多團隊:`references/contracts.md`;實測證據與限制:`references/evidence.md`;接向量庫/MCP 等外部知識庫:`references/adapters.md`。

## 六、做不到的事(誠實)

- 工具靠**標註與可解析的常數**運作;沒有標註的舊程式要先走 spec-flow-sync 的反推,且反推結果是「觀察到的行為」,**不等於意圖**。
- `check` 比對的是「宣告的常數」與「規格是否被改過」,**不驗證程式邏輯正確**;邏輯正確性靠測試,測試夠不夠強靠 `mutate`。
- 實測規模是玩具(數百行、Haiku、單輪),真實大型 C/C++、macro、條件編譯、硬即時都沒測。
