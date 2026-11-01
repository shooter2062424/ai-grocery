---
name: spec-flow-change
description: 執行一次「規格 ⇄ 程式」變更:新需求或規格變更要落地到程式(spec-to-code),或需要改程式行為而規格必須同步(code-to-spec),含跨模組介面/訊息/API 的破壞性變更(新舊並存遷移)。用於使用者說「依這份規格改程式」「規格改了」「要改這個上限/欄位/行為」「改介面」時。
---

# spec-flow-change:一次變更怎麼做

先讀 `spec-code-flow` 的十條規則。工具:`../spec-code-flow/scripts/specflow.py`(下稱 `specflow`)。專案要有 `specflow.json`,沒有先走 spec-flow-init。

## A. 流程(規格 → 程式;反向見 B)

1. **查脈絡**:`specflow query <受影響的 ID>`、`specflow impact <ID…>`。把輸出當工作清單:要看的程式檔、要跑的測試、要通知的 owner、牽涉的 `D-*`。
2. **先判斷有沒有需要人決定的事**(在動手前):
   - `impact` 的「牽涉的決策項」不為空,且新規格會讓決策常數不夠用 ⇒ 先 `question` 並列出選項(例如提高預算 vs 降低單筆成本),**不要自己改決策常數**。
   - 規格含糊/矛盾 ⇒ `question`,寫明採用的假設。
   - 規格 vs 程式現況本來就不一致(遺留偏離,例如規格 200、程式 150)⇒ **獨立處理**,不要夾在這次功能變更裡悄悄修;在回報中列出,請人決定哪個為準。
3. **更新規格**(若是 code→spec 方向,先改規格文字再改程式,兩者同一變更)。新舊版本並存時,舊版內容保留(用 `release:` 屬性或獨立條目),新版只寫差異。
4. **先寫測試**(spec-first):依新規格寫測試並加 `@covers`;**邊界值必測**(上限、上限+1、編碼最大值、空/缺欄位)。在舊程式上跑一次,確認它是紅的(證明測試真的測到新行為)。
5. **改程式**,加/更新 `@spec` 標註。小步:一個變更一個邏輯單元。**不得修改 `protected` 路徑的檔案**(golden、舊版輸出)。
6. **跑關卡**:`gates`(測試)→ `specflow check` → `specflow guard`。
   - 退出碼 `1`:修。 退出碼 `3`:停,報告,不要硬繞。
   - 測試紅時先判斷是**程式錯**、**測試錯**還是**規格解讀有爭議**;後者開 `question`,不要改測試遷就程式。
7. **簽章**:全綠且 HUMAN 項已回報後,`specflow stamp <改動的 ID…> --by <名字>`。
8. **回報**(固定格式):改了什麼 / 影響範圍 / 跑了哪些關卡與結果 / 未解決的 SPEC QUESTION / 需要誰簽核。

## B. 反方向:程式要改行為,規格必須跟上

1. 先 `query` 該行為對應的 ID;沒有就新增一條 `R-`/`D-`(屬性齊全,外部/內部歸類不確定就問)。
2. 規格與程式在**同一個變更**一起改;改完 `check` 必須無 `CONST-DRIFT`/`STALE`。
3. 若這個行為被其他模組依賴(`dependents` 或 `@uses` 有人),照第 C 節。

## C. 跨模組介面變更(API、訊息、ILM、protobuf、事件…)

1. 改 `specs/contracts.json` 的新版草稿,對舊版跑 `specflow contract-diff old.json new.json`。
2. 依分類行動(完整說明見 `references/contracts.md`):
   - `semantic`(單位/縮放/極性/基底/預設值/enum 重編號):**不得就地改**。新增帶新名字的並存欄位,舊欄位照舊;consumer 逐一遷移。
   - `structural`:同上走共存期;移除欄位前要三方確認(manifest 無讀取者、契約測試綠、端到端綠)。
   - `boundary`(範圍放寬、enum 新增值):通知 consumer,附邊界案例;consumer 需容忍未知值。
   - `behavior`(順序、延遲):通知並補時序/順序測試。
3. `contract-diff` 列出的 consumer 來自 `@uses` 標註;**列為空不代表沒人用**(可能是動態讀取),移除前還要有執行期證據或契約測試。
4. 每個受影響 consumer 一個小變更,各自走 A 流程。

## 紅線

- 不重產 golden、不放寬測試、不調整 `D-*` 常數來讓關卡變綠。
- 不確定就 `question`,最終回報必須列出。
- 沒跑 `check` / 測試 / `guard` 就不說完成。
