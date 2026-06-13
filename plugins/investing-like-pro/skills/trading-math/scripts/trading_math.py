#!/usr/bin/env python3
"""
trading_math.py — 交易「贏家數學」計算器(教育用途,非投資建議)

實作四個核心:
  1) 期望值 Expectancy        expectancy()
  2) 損益兩平勝率 Breakeven    breakeven_winrate()
  3) 復原數學 Recovery         recovery_pct()
  4) 風險:部位大小 + 破產風險  position_size() / risk_of_ruin()(Monte Carlo)

純標準函式庫,無第三方相依。可當模組 import,或用 CLI 子命令跑。

CLI 範例:
  python trading_math.py expectancy --winrate 0.55 --avg-win 1200 --avg-loss 1000
  python trading_math.py expectancy --winrate 0.15 --r 8        # 用 R 倍數(avg_loss=1 單位)
  python trading_math.py breakeven --r 4
  python trading_math.py recovery --drawdown 0.5
  python trading_math.py position --balance 1000 --risk-pct 0.005 --stop 25 --pip-value 0.1
  python trading_math.py ruin --winrate 0.45 --r 2 --risk-pct 0.02 --threshold 0.5 --trades 200
  python trading_math.py report --winrate 0.45 --r 2 --risk-pct 0.02 --balance 10000
"""
from __future__ import annotations
import argparse
import random
import math


# ── 1) 期望值 ────────────────────────────────────────────────────────────────
def expectancy(winrate: float, avg_win: float, avg_loss: float,
               costs: float = 0.0) -> dict:
    """每筆交易平均期望值 = 勝率×平均獲利 − 敗率×平均虧損 − 每筆成本。
    avg_loss 傳「正數」(虧損的絕對值)。costs = 點差+手續費+滑價(每筆,絕對值)。
    回傳 paper(紙上)與 real(扣成本)兩個值。"""
    lossrate = 1.0 - winrate
    paper = winrate * avg_win - lossrate * avg_loss
    real = paper - costs
    return {
        "winrate": winrate,
        "lossrate": lossrate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "costs_per_trade": costs,
        "expectancy_paper": paper,
        "expectancy_real": real,
        "profitable": real > 0,
        # 以 R 表示(每筆風險 = avg_loss):每筆賺幾個 R
        "expectancy_in_R": (paper / avg_loss) if avg_loss else float("nan"),
    }


def expectancy_from_R(winrate: float, r: float) -> dict:
    """用 R 倍數算期望值:avg_win = r、avg_loss = 1(單位 = 1R)。"""
    return expectancy(winrate, avg_win=r, avg_loss=1.0)


# ── 2) 損益兩平勝率 ──────────────────────────────────────────────────────────
def breakeven_winrate(r: float) -> float:
    """目標賠率 R 下,不賺不賠所需的最低勝率 = 1 / (1 + R)。
    例:R=1 → 0.5;R=4 → 0.2(錯 80% 仍不虧)。"""
    return 1.0 / (1.0 + r)


# ── 3) 復原數學 ──────────────────────────────────────────────────────────────
def recovery_pct(drawdown: float) -> float:
    """虧損 drawdown(0~1)後,回到原點所需的報酬率 = d / (1 − d)。
    例:0.1→0.111;0.3→0.4286;0.5→1.0(要翻倍)。"""
    if drawdown >= 1.0:
        return float("inf")
    return drawdown / (1.0 - drawdown)


# ── 4a) 部位大小 ─────────────────────────────────────────────────────────────
def position_size(balance: float, risk_pct: float, stop_distance: float,
                  value_per_unit: float = 1.0) -> dict:
    """固定「每筆冒的錢」反推部位大小。
      risk_dollars = balance × risk_pct
      units = risk_dollars / (stop_distance × value_per_unit)
    stop_distance:停損距離(點數/pips/價格單位,自選);
    value_per_unit:每 1 單位部位、每 1 stop_distance 的金額(如外匯每 pip 每手價值)。
    回傳冒的金額與可下的「單位數」。"""
    risk_dollars = balance * risk_pct
    denom = stop_distance * value_per_unit
    units = risk_dollars / denom if denom else float("nan")
    return {
        "balance": balance,
        "risk_pct": risk_pct,
        "risk_dollars": risk_dollars,
        "stop_distance": stop_distance,
        "value_per_unit": value_per_unit,
        "position_units": units,
    }


# ── 4b) 破產風險 / 指定回撤機率(Monte Carlo)──────────────────────────────
def risk_of_ruin(winrate: float, r: float, risk_pct: float,
                 threshold: float = 0.5, trades: int = 200,
                 sims: int = 20000, seed: int = 12345) -> dict:
    """模擬 sims 條長度 trades 的權益曲線,估「期間內最大回撤 ≥ threshold」的機率。
    每筆:贏 → 帳戶 ×(1 + risk_pct×r);輸 → 帳戶 ×(1 − risk_pct)。
    (用『固定百分比風險』複利模型;每筆獨立,呼應賭徒謬誤。)"""
    rng = random.Random(seed)
    hit = 0
    final_mult = []
    for _ in range(sims):
        equity = 1.0
        peak = 1.0
        ruined = False
        for _ in range(trades):
            if rng.random() < winrate:
                equity *= (1.0 + risk_pct * r)
            else:
                equity *= (1.0 - risk_pct)
            peak = max(peak, equity)
            if (peak - equity) / peak >= threshold:
                ruined = True
                break
        if ruined:
            hit += 1
        else:
            final_mult.append(equity)
    avg_final = sum(final_mult) / len(final_mult) if final_mult else 0.0
    return {
        "winrate": winrate, "r": r, "risk_pct": risk_pct,
        "threshold_drawdown": threshold, "trades": trades, "sims": sims,
        "prob_hit_drawdown": hit / sims,
        "avg_final_multiple_if_survived": avg_final,
        "expectancy_in_R": expectancy_from_R(winrate, r)["expectancy_in_R"],
    }


def _fmt(x):
    if isinstance(x, float):
        if math.isinf(x):
            return "∞"
        return f"{x:,.4f}"
    return str(x)


def _print(d: dict):
    for k, v in d.items():
        print(f"  {k:32s} : {_fmt(v)}")


def full_report(winrate, r, risk_pct, balance, stop_distance=None,
                value_per_unit=1.0, costs=0.0):
    """一次跑完四個概念,給綜合體檢。"""
    print("=== 1) 期望值 Expectancy ===")
    exp = expectancy_from_R(winrate, r)
    if costs:
        exp = expectancy(winrate, avg_win=r, avg_loss=1.0, costs=costs)
    _print(exp)
    print("=== 2) 損益兩平勝率 Breakeven ===")
    be = breakeven_winrate(r)
    print(f"  目標 {r}R 的損益兩平勝率   : {be:.4f}  (你的勝率 {winrate:.2%} "
          f"{'> 過關' if winrate > be else '< 不足'})")
    print("=== 3) 復原數學 Recovery(若發生 50% 回撤需多少報酬回本)===")
    for d in (0.1, 0.2, 0.3, 0.5):
        print(f"  虧損 {d:.0%} → 需報酬 {recovery_pct(d):.2%} 才回本")
    print("=== 4) 風險 Risk ===")
    if stop_distance:
        _print(position_size(balance, risk_pct, stop_distance, value_per_unit))
    print("  -- 破產風險(Monte Carlo,200 筆內出現 ≥50% 回撤的機率)--")
    ror = risk_of_ruin(winrate, r, risk_pct, threshold=0.5, trades=200)
    print(f"  每筆風險 {risk_pct:.2%} → P(≥50% 回撤) ≈ {ror['prob_hit_drawdown']:.2%}")
    print("  (把 risk-pct 調 0.5%/1%/2%/5% 比較,會看到破產風險爆炸式上升)")


def main():
    p = argparse.ArgumentParser(description="交易贏家數學計算器(教育用途,非投資建議)")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("expectancy", help="期望值")
    e.add_argument("--winrate", type=float, required=True)
    e.add_argument("--avg-win", type=float)
    e.add_argument("--avg-loss", type=float)
    e.add_argument("--r", type=float, help="用 R 倍數(avg_loss=1)")
    e.add_argument("--costs", type=float, default=0.0)

    b = sub.add_parser("breakeven", help="損益兩平勝率")
    b.add_argument("--r", type=float, required=True)

    rc = sub.add_parser("recovery", help="復原所需報酬")
    rc.add_argument("--drawdown", type=float, required=True)

    ps = sub.add_parser("position", help="部位大小")
    ps.add_argument("--balance", type=float, required=True)
    ps.add_argument("--risk-pct", type=float, required=True)
    ps.add_argument("--stop", type=float, required=True)
    ps.add_argument("--pip-value", type=float, default=1.0)

    ru = sub.add_parser("ruin", help="破產風險 Monte Carlo")
    ru.add_argument("--winrate", type=float, required=True)
    ru.add_argument("--r", type=float, required=True)
    ru.add_argument("--risk-pct", type=float, required=True)
    ru.add_argument("--threshold", type=float, default=0.5)
    ru.add_argument("--trades", type=int, default=200)
    ru.add_argument("--sims", type=int, default=20000)

    rp = sub.add_parser("report", help="綜合體檢")
    rp.add_argument("--winrate", type=float, required=True)
    rp.add_argument("--r", type=float, required=True)
    rp.add_argument("--risk-pct", type=float, required=True)
    rp.add_argument("--balance", type=float, default=10000)
    rp.add_argument("--stop", type=float)
    rp.add_argument("--pip-value", type=float, default=1.0)
    rp.add_argument("--costs", type=float, default=0.0)

    a = p.parse_args()
    if a.cmd == "expectancy":
        if a.r is not None:
            _print(expectancy_from_R(a.winrate, a.r) if not a.costs
                   else expectancy(a.winrate, a.r, 1.0, a.costs))
        else:
            _print(expectancy(a.winrate, a.avg_win, a.avg_loss, a.costs))
    elif a.cmd == "breakeven":
        print(f"breakeven_winrate({a.r}R) = {breakeven_winrate(a.r):.4f}")
    elif a.cmd == "recovery":
        print(f"recovery_pct({a.drawdown:.0%}) = {recovery_pct(a.drawdown):.4f}")
    elif a.cmd == "position":
        _print(position_size(a.balance, a.risk_pct, a.stop, a.pip_value))
    elif a.cmd == "ruin":
        _print(risk_of_ruin(a.winrate, a.r, a.risk_pct, a.threshold, a.trades, a.sims))
    elif a.cmd == "report":
        full_report(a.winrate, a.r, a.risk_pct, a.balance, a.stop, a.pip_value, a.costs)


if __name__ == "__main__":
    main()
