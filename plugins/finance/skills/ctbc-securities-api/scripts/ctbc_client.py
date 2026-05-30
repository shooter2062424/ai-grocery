#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ctbc_client.py — 中國信託證券交易 API 的「無 GUI、可重用」Python client。

從官方 PyQt 範例蒸餾而來,只保留交易/查詢核心,方便寫自動化或 headless 程式。

⚠️ 會送出真實證券委託、涉及真錢。請先用測試環境(apsit.ectest.ctbcsec.com/tradedas),
   每一筆下單/改單/刪單前務必再三確認。非投資建議,風險自負。

環境需求(關鍵):
  - 32-bit Python(COM 元件是 x86),建議 3.10 32-bit
  - pip install pywin32
  - 機器需裝過「中國信託致富王」並匯入憑證(否則 COM 未註冊/憑證簽章失敗)
  - 只能在 Windows 跑

快速使用:
    from ctbc_client import CTBCClient
    cli = CTBCClient(trade_das="apsit.ectest.ctbcsec.com/tradedas")
    cli.init2(uid="你的身分證", password="你的密碼")   # = Init+Login+Connect
    for acc in cli.get_accounts():
        print(acc)                                      # dict: ID/Name/UID/Type...
    acc_id = cli.first_stock_account()                  # 79Z-1234567
    print(cli.query_position(acc_id))                   # 查庫存(唯讀,安全)
    # 下單(限價買 0050 1 張 90.5)— 確認後再執行!
    # print(cli.stock_new_order(acc_id, "0050", qty=1, bs="buy", price="90.5"))
    cli.fini2(uid="你的身分證")
"""
import datetime
import sys

# 列舉對照(以官方文件為準)
TT = {"normal": 0, "odd": 1, "afterhours": 2, "emerging": 5, "intraday_odd": 7}     # 交易類別
OT = {"cash": 0, "margin": 1, "short": 2, "day_short_first": 16}                    # 委託類別
BS = {"buy": 1, "sell": 2}                                                          # 買賣別
PT = {"limit": 0, "up": 1, "down": 2, "flat": 3, "market": 4}                       # 價格別
COND = {"ROD": 0, "FOK": 1, "IOC": 2}   # ⚠️ 官方文件 0ROD/1FOK/2IOC;範例 GUI 不同,先測試環境驗證


def _today() -> int:
    return int(datetime.date.today().strftime("%Y%m%d"))


class _CTSEvents:
    """DispatchWithEvents 需要的事件類別;OnDataResponse 之後會被重新指派。"""
    def OnDataResponse(self, event_id, response_data):
        cb = getattr(self, "_user_cb", None)
        if cb:
            cb(event_id, response_data)
        else:
            print(f"[event {event_id}] {response_data}")


class CTBCClient:
    PROGID = "DJTRADEOBJLibCTS.TradeApp"

    def __init__(self, trade_das: str, on_event=None):
        try:
            import win32com.client
        except ImportError:
            sys.exit("ERROR: 未安裝 pywin32。請在 32-bit Python 執行:pip install pywin32")
        self.trade_das = trade_das
        self.app = win32com.client.DispatchWithEvents(self.PROGID, _CTSEvents)
        # 依官方範例:建立後可重新指派 OnDataResponse 成自訂處理函式
        self.app._user_cb = on_event
        if on_event:
            self.app.OnDataResponse = on_event

    # ---- 生命週期 ----
    def init(self):
        ret, err, msg = self.app.Init(self.trade_das)
        if ret != 1:
            raise RuntimeError(f"Init 失敗 err={err} msg={msg}")
        return ret

    def login(self, uid: str, password: str):
        ret, err, msg = self.app.Login(uid, password)
        if ret != 1:
            raise RuntimeError(f"Login 失敗 err={err} msg={msg}")
        return ret

    def connect(self):
        if self.app.Connect() == 0:
            raise RuntimeError("Connect 失敗(無法連線主動回報/Socket)")
        return 1

    def init2(self, uid: str, password: str):
        """一次完成 Init+Login+Connect。"""
        ret, err, msg = self.app.Init2(self.trade_das, uid, password)
        if ret != 1:
            raise RuntimeError(f"Init2 失敗 err={err} msg={msg}")
        return ret

    def fini(self):
        self.app.Fini()

    def fini2(self, uid: str):
        """一次完成 Disconnect+Logout+Fini。"""
        self.app.Fini2(uid)

    def set_echo_type(self, cmd_type: int, echo_type: int):
        # cmd 1=Order/2=QueryTrade/3=QueryData ; echo 0=同步/1=非同步
        self.app.SetEchoType(cmd_type, echo_type)

    def set_lot_size(self, data: str):
        # "0050=1000|0028=1000"
        self.app.SetLotSizeData(data)

    def ca_sign_check(self, account_id: str) -> str:
        """憑證簽章測試;回空字串=成功。"""
        return self.app.CASignCheck(account_id)

    # ---- 帳號 ----
    def get_accounts(self) -> list:
        """回傳 list[dict],每筆含 ID/Name/UID/Type/Credit/SFID/CanHedge。"""
        out = []
        n = self.app.GetAccountCount()
        for i in range(n):
            raw = self.app.GetAccount(i).strip("<>")
            d = {}
            for field in raw.split("|"):
                if "=" in field:
                    k, v = field.split("=", 1)
                    d[k] = v
            out.append(d)
        return out

    def first_stock_account(self) -> str:
        for a in self.get_accounts():
            if a.get("Type") == "1":
                return a.get("ID", "")
        return ""

    # ---- 交易(證券)----
    def stock_new_order(self, account_id, stock_id, qty, bs, price="0",
                        tt="normal", ot="cash", pt="limit", cond="ROD",
                        trade_date=None, broker="", pay_type=0):
        """送出證券新單。bs/tt/ot/pt/cond 可給字串(見上方對照)或直接給 int。
        price 是字串;市價/漲跌停/平盤(pt!=limit)會自動帶 '0'。回傳 API 字串。"""
        nTT = TT.get(tt, tt); nOT = OT.get(ot, ot); nBS = BS.get(bs, bs)
        nPT = PT.get(pt, pt); nCond = COND.get(cond, cond)
        if nPT != 0:
            price = "0"
        td = int(trade_date) if trade_date else _today()
        return self.app.Stock_NewOrder(account_id, td, nTT, nOT, nBS, str(stock_id),
                                       int(qty), nPT, str(price), broker, pay_type, nCond)

    def stock_modify_price(self, account_id, stock_id, oid, order_no, new_price,
                           q_current, q_match=0, pre_order=0, tt="normal", ot="cash",
                           new_pt="limit", trade_date=None):
        """改價(nType=2)。"""
        td = int(trade_date) if trade_date else _today()
        nPT = PT.get(new_pt, new_pt)
        price = str(new_price) if nPT == 0 else "0"
        return self.app.Stock_ModifyOrder(account_id, td, TT.get(tt, tt), OT.get(ot, ot),
                                          oid, order_no, str(stock_id), 1, 0,
                                          int(q_current), int(q_match), int(pre_order),
                                          2, price, nPT, 0)

    def stock_cancel_order(self, account_id, stock_id, oid, order_no, q_current,
                           q_match=0, pre_order=0, tt="normal", ot="cash", trade_date=None):
        """刪單(nQty=0)。"""
        td = int(trade_date) if trade_date else _today()
        return self.app.Stock_CancelOrder(account_id, td, TT.get(tt, tt), OT.get(ot, ot),
                                          oid, order_no, str(stock_id), 1, 0,
                                          int(q_current), int(q_match), int(pre_order),
                                          "0", 0, 0)

    # ---- 查詢(同步模式可直接拿回傳字串)----
    def query_order(self, account_id, force=False):
        return self.app.Stock_QueryOrder(account_id, 1 if force else 0)

    def query_match(self, account_id, force=False):
        return self.app.Stock_QueryMatch(account_id, 1 if force else 0)

    def query_position(self, account_id, trade_date=None, force=False):
        td = int(trade_date) if trade_date else _today()
        return self.app.Stock_QueryPosition(account_id, td, 1 if force else 0)

    # ---- 非同步:保持訊息泵讓 OnDataResponse 能觸發 ----
    @staticmethod
    def pump(seconds=2.0):
        """非同步模式下,呼叫此方法在指定秒數內處理 COM 事件回呼。"""
        import pythoncom, time
        end = time.time() + seconds
        while time.time() < end:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.05)


if __name__ == "__main__":
    # 範例:登入測試環境、查帳號與庫存(唯讀,不下單)
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--uid", required=True)
    ap.add_argument("--pwd", required=True)
    ap.add_argument("--trade-das", default="apsit.ectest.ctbcsec.com/tradedas")
    args = ap.parse_args()

    cli = CTBCClient(args.trade_das, on_event=lambda eid, data: print(f"[event {eid}] {data}"))
    cli.set_echo_type(2, 0); cli.set_echo_type(3, 0)   # 查詢用同步,好拿結果
    cli.init2(args.uid, args.pwd)
    print("帳號:")
    for a in cli.get_accounts():
        print(" ", a)
    acc = cli.first_stock_account()
    if acc:
        print("庫存:", cli.query_position(acc))
        print("委託:", cli.query_order(acc))
    cli.fini2(args.uid)
