---
name: spec-flow-init
description: 為一個專案建立 spec ⇄ code 知識庫與追溯(specflow.json、specs/、@spec/@covers 標註、首次 stamp)。用於專案尚未有 specflow.json、使用者要「開始用規格管理」「建需求清單」「幫既有專案補追溯」時。既有程式沒有規格時,先用 spec-flow-sync 的反推再回來。
---

# spec-flow-init:建立知識庫

先讀 `spec-code-flow` 的總則。工具路徑:`../spec-code-flow/scripts/specflow.py`(下稱 `specflow`)。

## 步驟

1. **偵測現況**:有沒有需求文件、測試、凍結的 golden/oracle 檔、介面定義(proto、OpenAPI、訊息定義)。把發現列給使用者,**不要憑空發明需求**。
2. `specflow --path <repo> init`,然後編輯 `specflow.json`:
   - `code_dirs` / `test_dirs` / `spec_dirs`:照實際目錄。
   - `protected`:凍結基準的 glob(golden、外部 oracle、舊版輸出)。**這些之後不得與程式同一變更修改。**
   - `gates`:一組指令,全部 exit 0 才算過(例如 `["python -m unittest -q", "python <skill>/scripts/specflow.py check"]`)。
   - `contracts`:介面契約檔路徑(有跨模組介面時才需要,格式見 `references/contracts.md`)。
3. **寫需求**(`specs/*.md`)。每條一個標題 `## R-AAA-01 · 標題` + 屬性清單 + 內文,格式見 `references/formats.md`。規則:
   - 外部公定要求用 `R-`,內部決定用 `D-`(**必須有 owner**,受保護數字寫進 `constants:`),待釐清用 `Q-`。
   - 一條需求只講一件可驗證的事;能用 `constants: NAME=值` 綁定程式常數的就綁(`check` 會自動比對)。
   - 有依賴就寫 `depends:`。
4. **補標註**:在實作處加 `@spec R-xxx`(任何語言的註解都行),在測試加 `@covers R-xxx`;讀契約欄位處加 `@uses Contract.field`。
5. `specflow check --untagged --verbose`:看孤兒標註、未實作、未測試、沒有任何 @spec 的檔案。逐項處理或明確記錄為已知缺口。
6. 所有測試綠、`check` 無 ERROR 後:`specflow stamp --all --by <你的名字>`,把 `.specflow/stamps.json` 與 `specs/` 一起 commit;`.specflow/index.json` 加進 `.gitignore`。
7. 把 `spec-code-flow` 的規則 4~7(凍結基準、決策常數、紅燈兩類、SPEC QUESTION)抄進專案的 `CLAUDE.md`/`AGENTS.md`,讓日後每個 session 都遵守。

## 注意

- 沒有規格只有程式 ⇒ 轉 **spec-flow-sync**(反推),產出的規格標「觀察到的行為」,需人確認意圖後才升級為需求。
- 不要為了讓 `check` 變綠而亂寫標註。標註必須對應真的實作與真的測試。
