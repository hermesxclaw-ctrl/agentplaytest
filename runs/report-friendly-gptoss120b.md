# AgentPlaytest report — Snack Stand (model-friendly interface)

**Playtester:** Model: openai/gpt-oss-120b via llamacpp  
**Score:** 73.8/100 (grade B)  
**Verdict:** Playable with friction: the agent made real progress but did not finish.  
**Steps:** 9 of 20 max  
**Milestones:** 3/4 — first_sale, profit_10, profit_25
**Status:** INCOMPLETE — backend error at step 9: HTTP Error 429: Too Many Requests. Score is provisional.

## Where it got stuck (plain English)

- Most-used actions: `open_the_stand` x2, `end_the_day` x2.
- The run stopped early on a backend failure (1 failed request(s): backend error at step 9: HTTP Error 429: Too Many Requests). That is an infrastructure failure, not a model decision — the model never got to reply — so this score is provisional and the run should be repeated before it is compared with completed runs.
- It got 72% of the way to the goal (in cash terms) before the run ended.

## Transcript

| Step | Action | Result |
|---|---|---|
| 1 | `buy_5_snacks` | Bought 5 snacks for $10. Stock is now 5. |
| 2 | `open_the_stand` | 6 customers came but you only had stock for 5 of them. Sold 5 snacks for $25. |
| 3 | `end_the_day` | Day 2 begins. |
| 4 | `buy_10_snacks` | Bought 10 snacks for $20. Stock is now 10. |
| 5 | `advertise_today` | You put up flyers. More customers will come today. |
| 6 | `open_the_stand` | Sold 9 snacks for $45. |
| 7 | `set_price_high_8_dollars` | Price set to $8 per snack. |
| 8 | `end_the_day` | Day 3 begins. |
| 9 | — | ERROR: backend error after retry: HTTP Error 429: Too Many Requests |
