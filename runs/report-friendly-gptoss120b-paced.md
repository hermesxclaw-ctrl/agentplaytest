# AgentPlaytest report — Snack Stand (model-friendly interface)

**Playtester:** Model: openai/gpt-oss-120b via llamacpp  
**Score:** 100.0/100 (grade A)  
**Verdict:** Model-playable: the agent reached the goal unaided.  
**Steps:** 9 of 20 max  
**Milestones:** 4/4 — first_sale, profit_10, profit_25, goal_reached

## Where it got stuck (plain English)

- Most-used actions: `open_the_stand` x3, `buy_5_snacks` x2.
- The agent reached the goal in 9 steps with 0 invalid replies.

## Transcript

| Step | Action | Result |
|---|---|---|
| 1 | `buy_5_snacks` | Bought 5 snacks for $10. Stock is now 5. |
| 2 | `open_the_stand` | 6 customers came but you only had stock for 5 of them. Sold 5 snacks for $25. |
| 3 | `end_the_day` | Day 2 begins. |
| 4 | `buy_10_snacks` | Bought 10 snacks for $20. Stock is now 10. |
| 5 | `advertise_today` | You put up flyers. More customers will come today. |
| 6 | `open_the_stand` | Sold 9 snacks for $45. |
| 7 | `end_the_day` | Day 3 begins. |
| 8 | `buy_5_snacks` | Bought 5 snacks for $10. Stock is now 6. |
| 9 | `open_the_stand` | Sold 6 snacks for $30. |
