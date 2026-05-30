---
name: ctbc-securities-api
description: 教 AI 如何用 Python 操作「中國信託證券」的交易 API(CTS / 嘉實 DJTRADEOBJLibCTS COM 元件)——登入、下單(新單/改單/改價/刪單)、查詢(委託/成交/庫存/帳號)、處理非同步回報。適用於:使用者要用 Python 串接中信證券下單/查詢、寫自動交易程式、解讀 API 回傳格式、或除錯 pywin32/COM 連線。⚠️ 這會送出真實證券委託、涉及真錢,務必先用測試環境並再三確認。
---

# ctbc-securities-api — 用 Python 操作中國信託證券交易 API

## 這是什麼

中國信託證券提供的 **交易 API** 是一個 **Windows COM 元件**(ProgID:`DJTRADEOBJLibCTS.TradeApp`,由嘉實資訊開發),隨「**中國信託致富王**」安裝時註冊(`apiCTS.dll`)。**使用時不需開啟致富王**,但機器上必須裝過它且已匯入憑證。Python 透過 **pywin32** 呼叫此 COM 元件即可下單與查詢。

> ⚠️ **重大安全聲明:** 本 skill 操作的是 **真實證券下單**(會花真錢)。協助使用者時務必:① **先用測試環境**(`TradeDas = apsit.ectest.ctbcsec.com/tradedas`)② 下任何真實單前 **明確複述參數並要求使用者確認** ③ 不擅自下單/改單/刪單;這 **不是投資建議**,所有交易風險由使用者自負。

## 環境前置(關鍵,常見卡點)

- **必須 32-bit Python**(COM 元件是 x86)。建議 Python 3.10 (32-bit)。
- `pip install pywin32`(GUI 範例另需 `PyQt5==5.15.7`,但 **headless 程式不需要 PyQt5**)。
- 機器需 **裝過中國信託致富王 + 匯入憑證**(否則 COM 未註冊、或下單憑證簽章失敗)。
- 只能在 **Windows** 上跑(COM 限定)。
- 連線位址放 `appsetting.json`:`{"TradeDas": "apsit.ectest.ctbcsec.com/tradedas"}`(此為 **測試**;正式環境位址依致富王/券商提供)。

## 核心用法(讀 `references/api-reference.md` 拿完整參數表)

### 1. 建立帶事件的 COM 物件(pywin32)
COM 元件有 **非同步事件回呼**,必須用 `DispatchWithEvents` + 一個含同名 method 的類別接收:
```python
import win32com.client

class _CTSEvents:
    def OnDataResponse(self, eventID, responseData):  # 事件入口,之後可重新指派
        pass

app = win32com.client.DispatchWithEvents("DJTRADEOBJLibCTS.TradeApp", _CTSEvents)
app.OnDataResponse = my_handler   # 重新指派成你的處理函式(eventID, responseData)
```

### 2. out 參數 → Python 以 tuple 依序回傳
C# 的 `out` 參數在 Python **不支援**,會 **以 tuple 依序回傳**。例:
```python
# C#: int nRet = app.Init(strTradeDAS, out nErrCode, out sErrMsg);
(ret, err_code, err_msg) = app.Init(trade_das)          # ret: 1成功/0失敗
(result, err_code, err_msg) = app.Login(uid, password)  # result: 1成功/0失敗
```

### 3. 生命週期(順序很重要)
```
Init(TradeDas) → Login(UID, Password) → Connect() → 取得帳號 → 交易/查詢 → Disconnect → Logout → Fini
```
- 也可用捷徑:**`Init2(TradeDas, UID, Password)`** 一次做完 Init+Login+Connect;**`Fini2(UID)`** 一次做完 Disconnect+Logout+Fini。
- `SetLogPath` 若要設,**必須在 Init 之前**。
- 帳號:`GetAccountCount()` + `GetAccount(idx)`,或 `GetAccountList()` 一次取全部;格式 `<ID=79Z-1234567|Name=...|UID=...|Type=1|...>`(Type=1 證券)。**下單用的 sAccountID 是「分公司代號-帳號」,如 `79Z-1234567`**。

### 4. 同步 vs 非同步回傳(`SetEchoType`)
`SetEchoType(lCmdType, lEchoType)`:cmdType 1=Order/2=QueryTrade/3=QueryData;echoType **0=同步(直接回完整字串)**、**1=非同步(先回 cookie,結果走 OnDataResponse 回呼)**。
> 範例程式用 `SetEchoType(1,1)`(下單非同步)。**新手建議先用同步(0)** 比較好拿結果除錯;要即時/高頻再用非同步 + 處理回呼事件(下單回 eventID=101、交易查詢 102、帳務 103、主動回報 100、連線狀態 1)。

### 5. 下單與查詢(證券)
```python
# 新單:tradeDate 西元 YYYYMMDD;price 是「字串」;市價/漲跌停時 price 給 "0"
result = app.Stock_NewOrder(account_id, tradeDate, nTT, nOT, nBS, stockID, qty,
                            nPT, price, broker, payType, nCond)
# 查詢(同步時直接拿到回傳字串)
app.Stock_QueryOrder(account_id, nForceQuery)       # 委託查詢
app.Stock_QueryMatch(account_id, nForceQuery)       # 成交查詢
app.Stock_QueryPosition(account_id, tradeDate, nForceQuery)  # 庫存查詢
```
列舉值(完整見 reference):**nTT** 0普通/1零股/2盤後/5興櫃/7盤中零股;**nOT** 0現股/1融資/2融券/16現沖先賣;**nBS** 1買/2賣;**nPT** 0限價/1漲停/2跌停/3平盤/4市價;**nCond** 0 ROD/1 FOK/2 IOC(⚠️見下方注意);`nForceQuery` 0用快取/1強制向伺服器查。

> ⚠️ **資料中有一處不一致:** API 文件寫 `nCond` 為 **0:ROD / 1:FOK / 2:IOC**,但範例 GUI 的下拉是 **ROD=0 / IOC=1 / FOK=2**。**以官方文件為準(0 ROD,1 FOK,2 IOC)**,但實作時 **務必先用測試環境驗證** FOK/IOC 的實際對應,別在正式單上賭。

### 6. 解析回傳格式
一般回傳:`<rc=#|cookie=#|err=#|msg=#|count=#><F0=..|F1=..|...><...>`(rc 1成功/0失敗;Big5 編碼;特殊字元有跳脫 `&amp; &lt; &gt; &bar; &equ;`)。用 `scripts/parse_response.py` 解析成 dict;各查詢的 F0..Fn 欄位定義見 `references/api-reference.md`。

## 可直接用的工具

- **`scripts/ctbc_client.py`** — 從官方範例蒸餾出的 **無 GUI、可重用 client 類別**(Init2 登入、下單、三種查詢、Fini2、事件回呼路由)。把帳密/TradeDas 設好即可在 32-bit Python 跑。
- **`scripts/parse_response.py`** — 把 `<rc=..><F0=..|F1=..>` 回傳解析成 list[dict],並還原跳脫字元。

## 建議工作流程

1. **先確認環境**:32-bit Python？`pip show pywin32`？致富王與憑證裝了嗎?用測試 TradeDas。
2. 用 `ctbc_client.py` 先 **登入 + 查帳號 + 查庫存/委託**(唯讀,安全)驗證連線。
3. 下單前 **同步模式 + 複述參數請使用者確認**;成功後再考慮非同步/自動化。
4. 用 `parse_response.py` + reference 的欄位表解讀結果。
5. 收尾呼叫 `Fini2(UID)` 釋放資源。

## 注意 / 限制

- **期權(FutOpt_*)**:範例程式雖有 `FutOpt_NewOrder` 等,但官方文件 v1.0.6.0 已「把期權拿掉」,屬未文件化,**不建議依賴**;本 skill 聚焦 **證券**。
- COM 是 **單執行緒 Apartment**;事件回呼在 Windows 訊息迴圈中觸發,headless 跑非同步時需要 `pythoncom.PumpWaitingMessages()` 之類保持訊息泵(見 client 註解)。
- 憑證簽章可用 `CASignCheck(sAccountID)` 測試(回空字串=成功)。

---

## 免責聲明

本 skill 為 **技術整合教學**,協助以 Python 串接中國信託證券交易 API。**會送出真實委託、涉及真實資金與券商規範**,不構成任何投資建議。請先在測試環境驗證、自行確認每一筆操作,風險與責任由使用者自負。
