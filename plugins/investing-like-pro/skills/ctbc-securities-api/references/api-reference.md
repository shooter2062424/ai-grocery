# Reference:中國信託證券交易 API 完整參數(整理自官方功能說明文件)

> COM ProgID:`DJTRADEOBJLibCTS.TradeApp`(TypeLib `DJTRADEOBJLibCTS`,類別 `TradeAppClass`)。
> 所有 `out` 參數在 Python 以 **tuple 依序回傳**(C# `int Init(s, out err, out msg)` → Python `(ret, err, msg)=Init(s)`)。
> 字串型別 BSTR ↔ Python str。回傳字串以 **Big5** 編碼(含中文)。

## A. 設定 / 連線生命週期

| 函式 | 參數(Python 呼叫) | 回傳 | 說明 |
|---|---|---|---|
| `Init(sTradeDAS)` | 連線位置字串 | `(ret, errCode, errMsg)`,ret 1成功/0失敗 | 最先呼叫(除 SetLogPath 外都要在此之後) |
| `Login(sUID, sPassword)` | 身分證/統編、密碼 | `(ret, errCode, errMsg)`,1/0 | Init 後才可;取得交易設定、回報伺服器、帳號 |
| `Connect()` | — | int(1成功/0失敗) | Login 後才可;主動回報 + Socket 下單連線 |
| `Disconnect()` | — | 無 | 登出主動回報連線 |
| `Logout(sUID)` | 身分證/統編 | 無 | 結束交易連線 |
| `Fini()` | — | 無 | 釋放記憶體、完整結束 |
| `Init2(sTradeDAS, sUID, sPassword)` | 連線主機、身分證、密碼 | `(ret, errCode, errMsg)`,1/0 | 一次做完 Init+Login+Connect |
| `Fini2(sUID)` | 身分證/統編 | 無 | 一次做完 Disconnect+Logout+Fini |
| `SetLogPath(sLogPath)` | 絕對路徑 | str(空=成功) | **必須在 Init 之前**;工程師除錯用 |
| `SetExecOrderType(lType)` | 0 Auto/1 HTTP/2 Socket | 無 | 下單走 HTTP 或 Socket |
| `SetLotSizeData(s)` | `"0050=1000|0028=1000"` | 無 | 設定非千股商品的交易單位 |
| `SetEchoType(lCmdType, lEchoType)` | cmd 1 Order/2 QueryTrade/3 QueryData;echo 0 同步/1 非同步 | 無 | 設定各類 API 同步或非同步回傳 |

## B. 帳號

| 函式 | 回傳 |
|---|---|
| `GetAccountCount()` | int(帳號數,不分證券期權) |
| `GetAccount(idx)` | 單筆帳號字串 |
| `GetAccountList()` | 全部帳號字串(多筆相連) |

**帳號格式:** `<ID=...|Name=...|UID=...|Type=...|Credit=...|SFID=|CanHedge=...>`
- `ID` 證券帳號(如 `79Z-1234567`,**= 分公司代號-帳號**,下單就用這個)·`Name` 名稱 ·`UID` 身分證 ·`Type` 1=證券 ·`Credit` 0無資券/1有資券 ·`CanHedge` 0不可現沖/1可先買後賣/2可先買後賣與先賣後買。
- 範例:`<ID=79Z-1234567|Name=證-安和1234567-陳XX|UID=A123456789|Type=1|Credit=1|SFID=|CanHedge=2>`

## C. 證券交易

### 新單 `Stock_NewOrder(...)` → 回傳字串(證券新單回傳格式)
參數順序:`(sAccountID, lTradeDate, nTT, nOT, nBS, sStockID, lQty, nPT, sPrice, sBroker, nPayType, nCond)`
- `sAccountID` 證券帳號(79Z-1234567)·`lTradeDate` 西元 YYYYMMDD(int)·`sStockID` 股號(如 0050)
- `lQty` 普通/盤後=張數;零股/興櫃=股數 ·`sPrice` **字串**(可小數,如 "90.5");市價/漲跌停/平盤時給 "0"
- `sBroker`/`nPayType` 興櫃保留未用(給 ""、0)

| 代碼 | 值 |
|---|---|
| **nTT 交易類別** | 0 普通 / 1 零股 / 2 盤後 / 5 興櫃 / 7 盤中零股 |
| **nOT 委託類別** | 0 現股 / 1 融資 / 2 融券 / 16 現沖先賣 |
| **nBS 買賣別** | 1 買進 / 2 賣出 |
| **nPT 價格別** | 0 限價 / 1 漲停 / 2 跌停 / 3 平盤 / 4 市價 |
| **nCond 委託條件** | 0 ROD / 1 FOK / 2 IOC ←（官方文件;⚠️ 範例 GUI 為 ROD=0/IOC=1/FOK=2,以測試環境驗證為準) |

### 改單 / 改價 `Stock_ModifyOrder(...)` → 回傳字串
參數:`(sAccountID, nTradeDate, nTT, nOT, sOID, sOrderNo, sStockID, nBS, nQty, nQcurrent, nQmatch, nPreOrder, nType, sNewPrice, nNewPriceType, nCond)`
- `sOID` 委託單編號 ·`sOrderNo` 委託書號 ·`nQty` 取消後股數(0=刪單)·`nQcurrent` 有效張數 ·`nQmatch` 成交張數 ·`nPreOrder` 保留給 0
- `nType` **0=改單 / 2=改價** ·`sNewPrice` 新價(若 nNewPriceType=1/2/3/4 則給 "0")·`nNewPriceType` 0限價/1漲停/2跌停/3平盤/4市價 ·`nCond` 0 ROD/1 FOK/2 IOC(目前只支援非市價 ROD 改非市價 ROD)

### 刪單 `Stock_CancelOrder(...)` → 回傳字串
參數:`(sAccountID, nTradeDate, nTT, nOT, sOID, sOrderNo, sStockID, nBS, nQty, nQcurrent, nQmatch, nPreOrder, sPrice, nPriceType, nCond)`
- `nQty` 0=刪單 ·其餘同上;`sPrice`/`nPriceType` 同改單規則。

### 查詢(可同步直接拿回傳字串)
| 函式 | 參數 |
|---|---|
| `Stock_QueryOrder(sAccountID, nForceQuery)` | 委託查詢 |
| `Stock_QueryMatch(sAccountID, nForceQuery)` | 成交查詢 |
| `Stock_QueryPosition(sAccountID, nTradeDate, nForceQuery)` | 庫存查詢 |

`nForceQuery`:0 用元件快取 / 1 強制向伺服器查。

### 憑證 `CASignCheck(sAccountID)` → 回傳錯誤訊息(**空字串=簽章成功**),帳號放證券帳號。

## D. 非同步事件(OnDataResponse 回呼)

`OnDataResponse(nEventID, sResponseData)`:

| EventID | 名稱 | 內容 |
|---|---|---|
| 1 | 主動回報連線狀態 | `AccType,Status`(AccType 1=證券;Status 0斷線/1連線) |
| 100 | 主動回報(委託/成交即時回報) | 見「主動回報回傳格式」 |
| 101 | 下單回傳(非同步) | 一般回傳格式 |
| 102 | 交易查詢回傳(非同步) | 一般回傳格式 |
| 103 | 帳務查詢回傳(非同步) | 一般回傳格式 |
| 202 | 資料改變通知 | — |

## E. 回傳格式

**一般回傳:** `<rc=#code|cookie=#cookie|err=#errcode|msg=#message|count=#count><F0=..|F1=..|...><...>`
- `rc` 1成功/0失敗 ·`cookie` Request 編號 ·`err` 錯誤碼 ·`msg` 訊息 ·`count` 筆數;每筆 record = `<F0=..|F1=..|...>`。
- **Big5 編碼**;特殊字元跳脫:`&`→`&amp;`、`<`→`&lt;`、`>`→`&gt;`、`|`→`&bar;`、`=`→`&equ;`(解析時要還原)。

**證券新單回傳:** F0 1預約/0盤中 ·F1 交易日期 ·F2 委託書號 ·F3 委託編號 ·F4 Mode ·F5 OrderStatus ·F6 Code ·F7 CodeMsg。

**委託查詢回傳(F0~F32):** F0 帳號 ·F1 交易日期 ·F2 nTT ·F3 nOT ·F4 買賣別 ·F5 股號 ·F6 價格別 ·F7 價位 ·F8 原委託張/股數 ·F9 委託書號 ·F10 已成交 ·F11 已取消 ·F12 委託日期 ·F13 委託時間 ·F14 狀態描述(FALSE=失敗)·F15 編號(OID)·F16 預約單 ·F17 均價 ·F18 有效張數 ·F19/F20 異動日期/時間 ·F21 交割別 ·F26 1錯誤單 ·F27 Code ·F28 CodeMsg(錯誤訊息)·F30 委託條件 0ROD/1FOK/2IOC/99NULL …

**成交查詢回傳(F0~F20):** F0 TradeID ·F1 交易日期 ·F2 nTT ·F3 股號 ·F4 買賣別 ·F5 nOT ·F6 價位 ·F7 數量 ·F8 價金 ·F9 委託書號 ·F10/F11 成交日期/時間 ·F12 手續費 ·F13 交易稅 ·F14 編號 ·F16 股票名稱 …

**庫存查詢回傳(F0~F29):** F0 nTT ·F1 股號 ·F2 集保昨庫 ·F3 集保今庫 ·F4~F7 今買委/買成/賣委/賣成 ·F9~F15 融資相關 ·F16~F22 融券相關 ·F23 成本 ·F24 股票名稱 ·F25 昨收 …

**主動回報(eventID=100)欄位(F0~F29):** F0 帳號 ·F1 回報類別(03證券)·F2 OP ·F5 委託書號 ·F6 普通0/零股2/盤後3/興櫃4/盤中零股7 ·F7 現股0/融資3/融券4 ·F8 股票代號 ·F9 價位 ·F10 價格別 ·F11 B/S ·F12 數量 ·F14/F15 日期/時間 ·F28 委託條件 FOK'F'/IOC'I'/ROD'R' …

## F. 錯誤代碼

| 代碼 | 意義 |
|---|---|
| 0 | 無錯誤 |
| 1 | 執行逾時 |
| 9000 | 未定義的錯誤 |
| 9001 | 系統內部錯誤 |
| 9002 | 不合法的參數 |
| 9003 | 未支援的功能 |
| 9100 | 網路錯誤 |
| 9200 | 結果錯誤 |

## G. 連線位址

- 測試:`apsit.ectest.ctbcsec.com/tradedas`(放 `appsetting.json` 的 `TradeDas`)。
- 正式:依致富王/券商提供。
