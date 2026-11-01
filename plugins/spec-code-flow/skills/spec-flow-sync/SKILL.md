---
name: spec-flow-sync
description: 檢查並修復規格與程式的漂移,或從既有程式反推規格(code-to-spec)。用於使用者說「程式被改了規格對得上嗎」「check 報 STALE/CONST-DRIFT」「幫既有程式補規格/追溯」「定期同步」時。
---

# spec-flow-sync:漂移檢查、修復與反推

先讀 `spec-code-flow` 總則。工具 `../spec-code-flow/scripts/specflow.py`(下稱 `specflow`)。

## 一、日常漂移檢查與修復

1. `specflow check --verbose`。逐類處理:

| 輸出 | 意思 | 處理 |
|---|---|---|
| `CONST-DRIFT` | 規格寫的常數值與程式不同 | **先問哪個才是意圖**(規格過期?程式改錯?),不要預設改程式。無法判斷 ⇒ `question`。 |
| `STALE` | 規格自上次 stamp 後被改過 | 讀規格 diff(`git diff -- specs/`),複查對應程式與測試;沒問題才 stamp |
| `ORPHAN-SPEC-TAG` / `ORPHAN-COVERS-TAG` | 標註指向不存在的 ID | 規格被刪/改名?補規格或修標註;殘留標註直接刪 |
| `DEPRECATED-IN-USE` | 已棄用的需求仍有程式引用 | 確認可移除(`query` 看被依賴)再清 |
| `UNIMPLEMENTED` / `UNTESTED` | 規格無實作/測試標註 | 補實作或測試;或確認是純決策項 |
| `DEPENDS-CYCLE` / `BAD-DEPENDS` | 依賴圖錯 | 修規格 |
| `OPEN-QUESTION`(HUMAN) | 未解決的 SPEC QUESTION | 彙整給使用者,不要自行關閉 |

2. 修完 `check` 無 ERROR、測試綠 ⇒ `stamp` 被複查過的 ID。
3. 建議把 `specflow check`(必要時加 `--strict`)放進 CI 的 PR 關卡,把 `guard` 放進 PR 檢查。

## 二、從既有程式反推規格(brownfield 第一步)

目標是**釘住現況**,不是宣稱意圖。

1. 盤點:列出模組、公開函式、常數、狀態/列舉、外部介面(檔頭與註解、現有測試名稱是線索)。大型程式依模組分批,每批一個變更。
2. 為每個可驗證的行為寫一條 `R-`/`D-` 草稿,屬性 `status: draft`,內文開頭註明 **「觀察到的行為(由程式反推),意圖未確認」**。常數用 `constants: NAME=值` 綁定。
3. 在程式加 `@spec`,在已有測試加 `@covers`;沒有測試的行為補 **characterization test**(用現在的輸出當期望,明確標註是 characterization)。
4. 工具能發現「規格值 vs 程式值」不一致,**但無法判斷哪個才是意圖**:列成清單請 owner 決定,不要自己選。
5. owner 確認後把 `status` 改 `active`,`stamp`。未確認者保持 `draft`,`check` 不會對 draft 報錯,但 `query` 仍看得到。
6. 對沒有任何 `@spec` 的檔案:`specflow check --untagged` 列出,排進後續批次。

## 三、定期維護(可交給 agent 常駐)

- 每週:`check --verbose --untagged`,彙整殘留標註、未標註檔案、過期功能旗標。
- 每次外部規格新版釋出:把差異寫成 delta(只記差異,舊版保留),走 spec-flow-change。
- 每季:跑 spec-flow-audit 看關卡有沒有變弱。
