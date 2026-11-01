# spec-code-flow

Spec ⇄ Code 雙向工作流 plugin。把需求規格、程式、測試用**追溯標註**綁成一個可查詢的知識庫:規格或程式任何一邊變動,都能被偵測、算出影響、擋住危險捷徑,不確定時**誠實升級給人決定**。

## 內容

| skill | 用途 |
|---|---|
| `spec-code-flow` | 總入口:情境路由、知識庫的讀取與更新規則、十條規則、指令速查。內含 `scripts/specflow.py` |
| `spec-flow-init` | 為專案建立知識庫(specflow.json、specs/、標註、首次 stamp) |
| `spec-flow-change` | 一次變更怎麼做:spec→code、code→spec、跨模組介面(新舊並存遷移) |
| `spec-flow-sync` | 漂移檢查與修復、從既有程式反推規格 |
| `spec-flow-audit` | 變異探測:檢驗測試與關卡夠不夠強 |

## 安裝

```text
/plugin marketplace add shooter2062424/ai-grocery
/plugin install spec-code-flow@ai-grocery
```

## 零依賴工具 `specflow.py`

Python 3.9+,只用標準函式庫,不綁任何資料庫產品。也可以不裝 plugin,直接把 `skills/spec-code-flow/scripts/specflow.py` 複製進你的 repo 用。

```bash
python specflow.py init                 # 建立 specflow.json 與 specs/
python specflow.py check                # 漂移總檢  (0 通過 / 1 壞掉 / 3 需人決定)
python specflow.py query R-001          # 查一條需求的全部脈絡
python specflow.py impact R-001         # 影響分析
python specflow.py stamp --all          # 驗證後簽章
python specflow.py guard                # 護欄:凍結基準與決策常數
python specflow.py contract-diff a.json b.json   # 介面契約語意 diff
python specflow.py mutate -n 40         # 關卡品質探測
python test_specflow.py                 # 自我測試
```

## 它不是什麼

- 不是自動從規格生成整個系統的工具;它守的是**一致性與流程**。
- 不證明程式邏輯正確;邏輯正確性靠測試,測試夠不夠強靠 `mutate`。
- 實測只在玩具規模、Haiku、單輪下做過(見 `skills/spec-code-flow/references/evidence.md`),不要把數字外推到真實大型專案。

## 授權

MIT
