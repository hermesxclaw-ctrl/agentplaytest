# AgentPlaytest report — Snack Stand (model-hostile interface)

**Playtester:** Model: openai/gpt-oss-120b via llamacpp  
**Score:** 20.6/100 (grade F)  
**Verdict:** Not model-playable: the agent could not make meaningful progress unaided.  
**Steps:** 20 of 20 max  
**Milestones:** 1/4 — first_sale

## Where it got stuck (plain English)

- Most-used actions: `op_a` x3, `op_c` x3.
- Longest no-progress stretch: 7 steps, starting at step 8. During a stall the agent is spending tokens without moving any milestone — in a paid agent product this is literally burning money.
- It got 14% of the way to the goal (in cash terms) before the run ended.

## Transcript

| Step | Action | Result |
|---|---|---|
| 1 | `op_a` | D1 |
| 2 | `op_c` | B1 |
| 3 | `op_d` | E04 |
| 4 | `op_e` | P9 |
| 5 | `op_b` | P9 |
| 6 | `op_f` | E04 |
| 7 | `op_g` | S1 |
| 8 | `op_h` | P9 |
| 9 | `op_c` | B1 |
| 10 | `op_d` | A7 |
| 11 | `op_a` | D1 |
| 12 | `op_b` | P9 |
| 13 | `op_e` | P9 |
| 14 | `op_f` | E04 |
| 15 | `op_g` | S1 |
| 16 | `op_c` | B1 |
| 17 | `op_h` | P9 |
| 18 | `op_d` | A7 |
| 19 | `op_a` | D1 |
| 20 | `op_b` | P9 |
