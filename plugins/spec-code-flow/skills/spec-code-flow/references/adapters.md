# 接外部知識庫(選用)

預設知識庫 = repo 內 Markdown + `.specflow/index.json`,git 版控、零伺服器。要接向量庫、圖資料庫或 MCP 時,把 `index.json` 當**唯一的結構化來源**,外部系統只做檢索加速:

```json
{
  "version": 1,
  "reqs":   {"R-1": {"id":"R-1","title":"…","kind":"external","owner":"…","status":"active",
                     "depends":["R-0"],"constants":{"LIMIT":"8"},"file":"specs/a.md","line":3,"hash":"…","text":"…"}},
  "code":   {"R-1": ["src/a.py:7"]},
  "tests":  {"R-1": ["tests/test_a.py:16"]},
  "uses":   {"Report.delay": ["src/consumer.py:2"]},
  "dependents": {"R-0": ["R-1"]}
}
```

建議的整合方式:

- **向量/全文檢索**:對 `reqs[*].text` 建索引;檢索結果只當**候選**,取得 ID 後一律用 `specflow query <ID>` 取權威內容與確認狀態(避免把過期的向量快照當真相)。
- **MCP/資料庫**:寫入端只接受 `specflow index` 的輸出,不允許手改;讀取端回傳時附 `hash`,讓呼叫者能比對是否 STALE。
- **多 repo**:每個 repo 各自有 index;跨 repo 的契約放在 producer repo,consumer repo 用 `@uses` 並在 CI 以 producer 的契約檔跑 `contract-diff`。
- **更新規則不變**:stamp 只在驗證後;外部庫不得成為第二個真相來源。
