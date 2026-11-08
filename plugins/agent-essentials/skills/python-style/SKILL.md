---
name: python-style
description: Python coding rules to apply whenever you write, edit, review or refactor Python code - docstring format (English Google style, brief on the line after the opening quotes, on every function including private helpers), PEP 484 type hints on every signature, and column alignment of ':' and '=' in consecutive declarations (module constants, Enum members, dataclass fields). Use for any .py file, script, module, class or function you create or change. （繁中觸發詞：寫 Python、改 Python、Python 程式碼風格、docstring 格式、型別標註、對齊 = 與 :、dataclass 欄位對齊、重構 .py。）
---

# Python style

Apply these rules to every Python function and declaration block you write or change.
When you edit an existing file, bring the code you touch up to these rules. Do not reformat code you did not touch.

## 1. Docstrings and type hints

Every function gets an English Google-style docstring. **Private helpers too** (`_name`), no exceptions.

- Write the opening `"""` on its own line. Put the **brief on the line after it**.
  Never write a one-line `"""Text."""`.
- After the brief, add an optional detail paragraph, then `Args:`, `Returns:`, and `Raises:`.
- Add `Raises:` when the function raises on purpose. Leave it out otherwise.
- Write `None.` under `Args:` when the function has no arguments.
- Put PEP 484 type hints on every signature. Use built-in generics (`list[int]`, `dict[str, int]`) and `X | None`.
  Put `from __future__ import annotations` at the top of the module.
- Comments explain the **why**, and stay short. Do not narrate what the code does.

```python
from __future__ import annotations

from datetime import datetime, timezone


def clamp(value: float, low: float, high: float) -> float:
    """
    Limit a value to a closed range.

    Both bounds are inclusive. The caller must pass low <= high.

    Args:
        value: Number to limit.
        low: Smallest allowed result.
        high: Largest allowed result.

    Returns:
        The value, or the nearest bound when the value is outside the range.

    Raises:
        ValueError: If low is greater than high.
    """
    if low > high:
        raise ValueError("low must not exceed high")
    return max(low, min(value, high))


def _now_label() -> str:
    """
    Build the timestamp label used in report file names.

    Args:
        None.

    Returns:
        The current UTC time as YYYYMMDD-HHMMSS.
    """
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
```

## 2. Alignment in blocks of consecutive declarations

In a block of consecutive declarations - module constants, `Enum` members, `@dataclass` fields:

- Align the `:` of type hints into one column.
- Align the `=` into one column.
- Keep at least one space on each side of `=`.
- Align trailing `#` comments in the block too.

Keyword arguments and defaults **inside a call or a signature** stay PEP 8: `f(x=1)`, `def f(x: int = 1)`.
Do not align across a blank line or a different kind of statement: each block aligns on its own.

```python
SPAN_DAYS  = 156 * 7      # look back at most 156 weeks
BASE_TOL   = 0.05
MAX_RETRY  = 3            # the upstream drops about 1 in 20 requests


class Side(Enum):
    BUY  = "buy"
    SELL = "sell"


@dataclass
class Level:
    side:  str
    price: float
    prob:  int | None = None
```

## Checklist before you finish

- [ ] Every function has a docstring with the brief on the line after the opening `"""`.
- [ ] Private helpers have one too.
- [ ] `Args:` says `None.` when there are no arguments.
- [ ] Every signature has type hints, with built-in generics and `X | None`.
- [ ] `from __future__ import annotations` is at the top.
- [ ] `:` and `=` line up in each declaration block, and `#` comments line up too.
- [ ] Calls and signatures still use `f(x=1)`.
