# 跨模組介面契約與多團隊變更

適用:模組之間用 API、訊息(例如公司內部的 ILM)、protobuf、事件、設定檔溝通,每個團隊守自己的模組。
**問題:只改自己這邊的 spec,別人不會知道,也不會自己同步。**

## 契約檔(機器可讀的單一真相)

```json
{
  "contracts": {
    "Report": {
      "owner": "team-1",
      "order": ["id", "delay", "power", "flag"],
      "latency_ms": 10,
      "fields": {
        "id":    {"type": "int", "range": [0, 255]},
        "delay": {"type": "int", "unit": "ms", "range": [0, 1000]},
        "power": {"type": "int", "scale": 0.5, "range": [0, 127]},
        "flag":  {"type": "int", "polarity": "1=on", "enum": {"OFF": 0, "ON": 1}, "default": 0}
      }
    }
  }
}
```

重點是把**語意屬性**寫成欄位:`unit`、`scale`、`polarity`、`base`(索引基底)、`default`、`range`、`enum`、`order`、`latency_ms`。寫在人腦或 Word 裡等於不存在。

consumer 在讀取處加 `@uses Report.delay`,工具就能回答「誰在用這個欄位」(consumer manifest)。

## 變更分類(`contract-diff`)

| 類別 | 例子 | schema diff 看得到嗎 | 處理 |
|---|---|---|---|
| structural | 移除/改名欄位、改型別、新增必填欄位 | 看得到 | 共存期 |
| **semantic** | 單位 ms→us、縮放、極性反轉、索引基底、預設值、enum 重編號 | **看不到(型別沒變)** | 共存期,禁止就地改 |
| boundary | 範圍放寬、新增 enum 值 | 看不到 | 通知 + 邊界案例 + tolerant reader |
| behavior | 順序、延遲上限 | 看不到 | 通知 + 時序/順序測試 |
| compatible | 新增選填欄位、範圍收窄 | — | 自動通過 |

## 破壞性變更:新舊並存(expand → migrate → contract)

1. **Expand**:producer 新增帶新名字的欄位(名字帶單位或版本,例如 `delay_us`),舊欄位照舊輸出。
2. **Migrate**:每個 consumer 各開一個小變更,改讀新欄位;manifest(`@uses`)標示已遷移。
3. **Contract**:確認沒人讀舊欄位才移除。「沒人讀」要三方證據:manifest 無讀取者 + 契約測試/端到端在移除後的狀態是綠的 + (可行時)執行期存取追蹤。**只靠靜態分析會漏動態讀取。**
4. consumer 一律採 **tolerant reader**:不認得的欄位忽略、不認得的 enum 走預設分支;否則連「新增欄位」都要等所有人先放寬。

## 分層關卡(沒有單一關卡夠用)

| 關卡 | 查什麼 | 盲點 |
|---|---|---|
| G0 團隊自己的測試 | 自己與自己的規格一致 | 看不到別人的假設 |
| G1 schema diff | 欄位增刪、型別 | 看不到語意/邊界/行為;對沒人用的欄位誤報 |
| G2 manifest 語意比對 | 契約新值 vs consumer 宣告的假設(`@uses` + 宣告) | 宣告過期、動態讀取 |
| G3 consumer 契約測試 | 用新契約產生含邊界的樣本跑 consumer | 缺測試的訊息;轉發給下游的效果 |
| G4 端到端 replay | 整個系統跑典型刺激 | 邊界、預設值、新 enum |

疊加才夠(模擬中 G2∪G3∪G4 約 99.7%,單獨最高約 95%)。**producer 的 PR 要能觸發 consumer repo 的契約測試**,否則只有 G0。

## 誰通知誰

`contract-diff` 的輸出(consumer 檔案清單 + 失敗案例)要**自動變成各 consumer repo 的 issue/PR 留言**,並附契約的 old→new diff。實測:agent 當 consumer 時,「有被叫起來並看到 diff」(76/80)與「只是規格放在旁邊」(17/80)差距巨大,能力不是瓶頸。
