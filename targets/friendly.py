"""Model-FRIENDLY interface for the Snack Stand sim.

Everything a player needs is communicated through the three channels the
checker allows: the state snapshot uses plain names and includes the goal,
the text view explains the situation and what every action does, and the
action names describe themselves.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from snackstand import SnackStand, MILESTONES, GOAL_CASH, DAYS  # noqa: E402

ACTIONS = [
    "buy_5_snacks",
    "buy_10_snacks",
    "set_price_low_3_dollars",
    "set_price_medium_5_dollars",
    "set_price_high_8_dollars",
    "advertise_today",
    "open_the_stand",
    "end_the_day",
]

ACTION_HELP = {
    "buy_5_snacks": "Buy 5 snacks for $10 (they cost $2 each). You need stock before you can sell.",
    "buy_10_snacks": "Buy 10 snacks for $20 (they cost $2 each).",
    "set_price_low_3_dollars": "Sell snacks at $3 each. More customers come (about 9 a day).",
    "set_price_medium_5_dollars": "Sell snacks at $5 each. About 6 customers a day.",
    "set_price_high_8_dollars": "Sell snacks at $8 each. Fewer customers (about 3 a day).",
    "advertise_today": "Costs $4. Brings 3 extra customers today.",
    "open_the_stand": "Open for business today and sell to today's customers. Once per day.",
    "end_the_day": "Sleep and move to the next day.",
}


class FriendlyStand:
    name = "Snack Stand (model-friendly interface)"
    goal_text = f"Finish the week with at least ${GOAL_CASH} cash."

    def __init__(self):
        self.sim = SnackStand()

    # --- the three channels the checker exposes to the model ---
    def state(self):
        s = self.sim
        return {
            "day": s.day,
            "days_in_week": DAYS,
            "cash_dollars": s.cash,
            "snacks_in_stock": s.stock,
            "current_price_dollars": s.price,
            "already_opened_today": s.opened_today,
            "advertised_today": s.ad_today,
            "total_snacks_sold": s.total_sold,
            "goal": self.goal_text,
            "what_happened_last": s.last_result,
            "game_over": s.done,
        }

    def text_view(self):
        s = self.sim
        lines = [
            "SNACK STAND — a tiny business game.",
            f"GOAL: {self.goal_text} You start with $20, so that means making $50 profit.",
            "",
            f"Day {s.day} of {DAYS}. You have ${s.cash} and {s.stock} snacks in stock.",
            f"Your price is ${s.price} per snack. Snacks cost you $2 each to buy.",
            f"So far you have sold {s.total_sold} snacks.",
            "",
            "What each action does:",
        ]
        for a in ACTIONS:
            lines.append(f"  - {a}: {ACTION_HELP[a]}")
        lines += [
            "",
            f"What happened last: {s.last_result}",
            "A good day usually looks like: buy snacks, pick a price, open the stand, then end the day.",
        ]
        return "\n".join(lines)

    def actions(self):
        return list(ACTIONS)

    # --- harness-side surface (NOT shown to the model) ---
    def act(self, action):
        s = self.sim
        table = {
            "buy_5_snacks": lambda: s.buy(5),
            "buy_10_snacks": lambda: s.buy(10),
            "set_price_low_3_dollars": lambda: s.set_price(3),
            "set_price_medium_5_dollars": lambda: s.set_price(5),
            "set_price_high_8_dollars": lambda: s.set_price(8),
            "advertise_today": s.advertise,
            "open_the_stand": s.open_stand,
            "end_the_day": s.end_day,
        }
        fn = table.get(action)
        return fn() if fn else f"Unknown action: {action}"

    def progress(self):
        return self.sim.progress()

    def milestones(self):
        return list(self.sim.milestones_hit), list(MILESTONES)

    def is_done(self):
        return self.sim.done


def make_target():
    return FriendlyStand()
