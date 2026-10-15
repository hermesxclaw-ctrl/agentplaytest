"""Snack Stand — a tiny business sim used as the AgentPlaytest demo target.

Written fresh for AgentPlaytest (Hacktoberfest 2026, Week 2). The simulation
core lives here once; two interface modules (friendly.py / hostile.py) expose
the SAME game through very different surfaces, so the playability checker can
show that interface quality — not task difficulty — decides whether a model
can use an app.

Rules (identical for both interfaces):
  - Start with $20 cash, 0 snacks, on day 1 of 7.
  - Buying stock costs $2 per snack.
  - Price tiers: $3 (low), $5 (medium), $8 (high).
  - Opening the stand sells to that day's customers:
      demand = 9 at $3, 6 at $5, 3 at $8; advertising adds +3 customers
      for the rest of the day and costs $4.
    Sales are limited by stock on hand.
  - Goal: finish with at least $70 cash (a $50 profit) by the end of day 7.
"""

WHOLESALE = 2
PRICE_TIERS = (3, 5, 8)
DEMAND = {3: 9, 5: 6, 8: 3}
AD_COST = 4
AD_BOOST = 3
START_CASH = 20
GOAL_CASH = 70
DAYS = 7

# Ground-truth milestones the checker scores against. The model never sees
# this list directly; a friendly interface *communicates* equivalent info.
MILESTONES = ("first_sale", "profit_10", "profit_25", "goal_reached")


class SnackStand:
    def __init__(self):
        self.day = 1
        self.cash = START_CASH
        self.stock = 0
        self.price = 5
        self.ad_today = False
        self.opened_today = False
        self.total_sold = 0
        self.done = False
        self.last_result = "The stand is set up. Nothing has happened yet."
        self.milestones_hit = []

    # -- underlying operations (interfaces map their action names to these) --
    def buy(self, n):
        cost = WHOLESALE * n
        if self.done:
            return "The week is over."
        if cost > self.cash:
            self.last_result = f"Not enough cash to buy {n} snacks (costs ${cost}, you have ${self.cash})."
        else:
            self.cash -= cost
            self.stock += n
            self.last_result = f"Bought {n} snacks for ${cost}. Stock is now {self.stock}."
        return self.last_result

    def set_price(self, p):
        if self.done:
            return "The week is over."
        self.price = p
        self.last_result = f"Price set to ${p} per snack."
        return self.last_result

    def advertise(self):
        if self.done:
            return "The week is over."
        if self.ad_today:
            self.last_result = "You already advertised today; it would not help twice."
        elif self.cash < AD_COST:
            self.last_result = f"Not enough cash to advertise (costs ${AD_COST}, you have ${self.cash})."
        else:
            self.cash -= AD_COST
            self.ad_today = True
            self.last_result = "You put up flyers. More customers will come today."
        return self.last_result

    def open_stand(self):
        if self.done:
            return "The week is over."
        if self.opened_today:
            self.last_result = "The stand was already open today; customers have gone home."
            return self.last_result
        self.opened_today = True
        customers = DEMAND[self.price] + (AD_BOOST if self.ad_today else 0)
        sold = min(self.stock, customers)
        self.stock -= sold
        revenue = sold * self.price
        self.cash += revenue
        self.total_sold += sold
        if sold == 0 and self.stock == 0:
            self.last_result = "You opened the stand but had no snacks to sell. Nobody bought anything."
        elif sold < customers:
            self.last_result = f"{customers} customers came but you only had stock for {sold} of them. Sold {sold} snacks for ${revenue}."
        else:
            self.last_result = f"Sold {sold} snacks for ${revenue}."
        self._check_milestones()
        return self.last_result

    def end_day(self):
        if self.done:
            return "The week is over."
        if self.day >= DAYS:
            self.done = True
            self.last_result = f"The week is over. Final cash: ${self.cash}."
        else:
            self.day += 1
            self.ad_today = False
            self.opened_today = False
            self.last_result = f"Day {self.day} begins."
        self._check_milestones()
        return self.last_result

    def _check_milestones(self):
        checks = {
            "first_sale": self.total_sold >= 1,
            "profit_10": self.cash >= START_CASH + 10,
            "profit_25": self.cash >= START_CASH + 25,
            "goal_reached": self.cash >= GOAL_CASH,
        }
        for name, ok in checks.items():
            if ok and name not in self.milestones_hit:
                self.milestones_hit.append(name)
        if self.cash >= GOAL_CASH:
            self.done = True

    def progress(self):
        """0..1 cash progress toward the goal, for checker scoring."""
        return max(0.0, min(1.0, (self.cash - START_CASH) / (GOAL_CASH - START_CASH)))
