---
name: video-transcript-verify
description: |
  把 YouTube 影片整理成知識筆記時的「逐字稿校正與延伸」流程:帶精確時間的逐字稿、
  影片畫面(投影片/燒錄字幕)截圖校正專有名詞、依影片提到的論文/技術 keyword 查一手資料延伸,
  並用單一頁面(Artifact)讓使用者點連結回到「對的時間點」逐題確認。
  觸發:整理 YouTube 影片/Whisper 逐字稿成筆記、字幕有同音字或專有名詞疑點、需要請使用者確認字幕、
  「校正字幕」「看影片畫面」「查論文延伸」「待確認清單」。
---

# 影片逐字稿校正與延伸(video-transcript-verify)

目標:字幕(尤其 Whisper)同音字多,專有名詞常錯。本流程用 **精確時間 + 畫面 + 一手資料** 取代猜測,
再把真正需要人判斷的題目集中成一頁讓使用者確認。

## 鐵則:時間不可錯
使用者會依你給的時間點回到影片聽。**時間錯 = 使用者無法校正**。
1. 給使用者的每個時間點,**只能**來自「帶時間的逐字稿」逐行查出的 `[m:ss]`;禁止寫「約 X:XX」或憑印象估。
2. 逐字稿必須帶時間:Whisper 輸出自帶(`[m:ss] 文字`);官方/自動字幕要保留 VTT 時間,**不可存成無時間純文字**。
3. 連結一律**提前 10 秒**(`&t=<秒-10>s`),並同時標示「從幾分幾秒開始、目標句在幾分幾秒」。
4. 找不到該詞就寫「逐字稿中未找到此詞」,不要編時間。
5. 交付前抽查:隨機 2–3 個時間點用截圖核對畫面/燒錄字幕是否吻合逐字稿。

工具(Knowledge 倉庫):`scripts/youtube/transcript_tools.py`
- `fetch <ID> --out DIR`:抓帶時間字幕,輸出 `[m:ss] 文字`;抓不到(HTTP 429/無字幕)改走 Whisper。
- `find <逐字稿> "<regex>" --video <ID>`:印精確時間、前後文與連結(含提前 10 秒)。
- `frames <ID> <秒>... --out DIR`:下載 480p 影片並截圖,再用 Read 看圖。

## 流程
1. **取帶時間逐字稿**:官方字幕優先(`fetch`,無官方字幕時自動改抓自動字幕);429 或無字幕時**一律呼叫 `python scripts/media/whisper_transcribe.py <影片ID或檔案> -o <輸出.txt> --prompt "<標題+說明欄+詞表>"`**(Knowledge 倉庫;固定 faster-whisper `large-v3-turbo` int8,輸出 `[m:ss]`,成敗看最後 `segments N`)。不要自己 inline 寫 `WhisperModel`,也不要換 `small`;SenseVoice-Small 只作純中文口播的備選實驗(未納入腳本)。
2. **整理初稿**(依 Knowledge 倉庫 CLAUDE.md 寫作規範)。
3. **看畫面,不只看字幕**:對專有名詞、數字、圖表、論文/repo 畫面出現處,用 `find` 取時間 → `frames` 截圖 → 讀圖。多數頻道(白白说大模型、Why QQ 等)有燒錄字幕與投影片,可直接讀到正確拼法(2026-11-07 實測:Chroma/Pinecone/Milvus、LangChain/Eino、FDE、vgpu 八項零件)。純口播頻道圖上無字,不算證據。
4. **依 keyword 查一手資料與延伸**:從字幕/畫面抽出論文、技術、工具、人名、數字,查 arXiv、官方文件、GitHub、官方部落格;有 repo 就 `git clone --depth 1` 讀原始碼再刪除。**要讀內文,不要只看搜尋摘要**。影片常把不同條件的數字放在一起比、講舊版架構、把論文結論講反,逐項核對並標出。
5. **寫入筆記**:修正錯誤;新增「延伸閱讀與深度補充」節(只寫真的讀到的內容,附完整 URL);核實以「已核實 / 需修正 / 未能核實」標示;無法確認的詞標「推定」,不可編造。
6. **仍需人判斷的題目 → 集中成一頁 Artifact**(不要在對話裡一題一題問):
   - 每題一張卡:頻道/影片、`▶ 開啟影片(從 X:XX 開始,目標句在 Y:YY)`連結、原字幕、問題、候選答案、自由輸入框。
   - 用 `db` capability 儲存選擇(集合 `answers`,doc id 為題號,欄位 `choice` / `note` / `video` / `t` / `at`);頁面頂端放進度條。
   - YouTube 無法嵌入 Artifact(CSP 禁止 iframe),只能用新分頁連結。
   - 使用者說填完後,用 `ArtifactData list` 讀 `answers`,把答案寫回筆記、刪除 `TRANSCRIPT-PENDING.md` 對應列,commit 並 push。
   - 使用者留白的「其他」視為「聽不出/無此詞」,筆記改為「推定」,不當成確認。
7. 使用者沒空(排程無人時):記到 `TRANSCRIPT-PENDING.md`(含**由 `find` 算出的精確時間**),筆記標「推定」。

## 備註
- SenseVoice 實測(i7-1260P CPU):一般中文詞最準最快,專有名詞全錯 → 專有名詞一律靠畫面與詞表;安裝需 `pip install --target np1 "numpy<2"` 並以 `PYTHONPATH=np1` 執行,避免動全域 numpy。
- 熱詞提示(`initial_prompt`)只能補一部分專有名詞,不能取代畫面核對。
- 批次審閱舊筆記時,每篇獨立處理、只改自己被指派的檔案,最後由主 session 統一 commit。
