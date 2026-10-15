"""Model-HOSTILE interface for the Snack Stand sim.

The underlying game is byte-for-byte the same simulation as friendly.py.
Only the surface changes — and it changes in the ways real apps are
accidentally hostile to agents:

  - state keys are opaque codes (d, c, s, p) with no units and no goal;
  - the price is a tier index (0/1/2), not a dollar amount;
  - the text view is an unlabeled dump plus decoy numbers that look
    important (a "Q" weather code, a "Z" index that is just day x 7);
  - action names are meaningless (op_a ... op_h) in scrambled order;
  - results come back as terse codes instead of sentences.

Nothing here lies exactly — it just never explains itself. That is the
point of the demo: the checker + model are identical, so any score gap
is caused by the interface alone.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from snackstand import SnackStand, MILESTONES  # noqa: E402

# Scrambled on purpose: op_a is "end day" (the tempting first choice that
# skips your selling day), buying is op_f / op_c, opening is op_g.
OP_MAP = {
    "op_a": "end_day",
    "op_b": "set_price_high",
    "op_c": "buy_10",
    "op_d": "advertise",
    "op_e": "set_price_low",
    "op_f": "buy_5",
    "op_g": "open_stand",
    "op_h": "set_price_medium",
}

PRICE_CODE = {3: 0, 5: 1, 8: 2}

RESULT_CODES = [
    ("Not enough cash", "E04"),
    ("already advertised", "R2"),
    ("already open", "R3"),
    ("Bought", "B1"),
    ("Price set", "P9"),
    ("flyers", "A7"),
    ("no snacks to sell", "S0"),
    ("Sold", "S1"),
    ("customers came", "S2"),
    ("begins", "D1"),
    ("week is over", "D9"),
]


def _code(result_text):
    for needle, code in RESULT_CODES:
        if needle in result_text:
            return code
    return "R0"


class HostileStand:
    name = "Snack Stand (model-hostile interface)"
    goal_text = ""  # never communicated to the model — that is the bug being demoed

    def __init__(self):
        self.sim = SnackStand()
        self.last_code = "R0"

    # --- the three channels the checker exposes to the model ---
    def state(self):
        s = self.sim
        return {
            "d": s.day,
            "c": s.cash,
            "s": s.stock,
            "p": PRICE_CODE[s.price],
            "o": 1 if s.opened_today else 0,
            "a": 1 if s.ad_today else 0,
            "t": s.total_sold,
            "r": self.last_code,
            "z": s.day * 7,          # decoy: looks like a score, means nothing
            "q": (s.day * 3) % 5,     # decoy: "weather", affects nothing
        }

    def text_view(self):
        s = self.sim
        return (
            f"D{s.day} C{s.cash} S{s.stock} P{PRICE_CODE[s.price]} "
            f"O{1 if s.opened_today else 0} A{1 if s.ad_today else 0} "
            f"T{s.total_sold} R{self.last_code} Z{s.day * 7} Q{(s.day * 3) % 5}"
        )

    def actions(self):
        return list(OP_MAP.keys())

    # --- harness-side surface (NOT shown to the model) ---
    def act(self, action):
        s = self.sim
        op = OP_MAP.get(action)
        if op is None:
            return "E99"
        if op == "buy_5":
            text = s.buy(5)
        elif op == "buy_10":
            text = s.buy(10)
        elif op == "set_price_low":
            text = s.set_price(3)
        elif op == "set_price_medium":
            text = s.set_price(5)
        elif op == "set_price_high":
            text = s.set_price(8)
        elif op == "advertise":
            text = s.advertise()
        elif op == "open_stand":
            text = s.open_stand()
        else:  # end_day
            text = s.end_day()
        self.last_code = _code(text)
        return self.last_code

    def progress(self):
        return self.sim.progress()

    def milestones(self):
        return list(self.sim.milestones_hit), list(MILESTONES)

    def is_done(self):
        return self.sim.done


def make_target():
    return HostileStand()
