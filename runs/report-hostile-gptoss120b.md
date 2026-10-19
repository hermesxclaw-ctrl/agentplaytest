# AgentPlaytest report — Snack Stand (model-hostile interface)

**Playtester:** Model: openai/gpt-oss-120b via llamacpp  
**Score:** 0.0/100 (grade F)  
**Verdict:** Not model-playable: the agent could not make meaningful progress unaided.  
**Steps:** 3 of 20 max  
**Milestones:** 0/4 — none
**Status:** INCOMPLETE — backend error at step 3: HTTP Error 429: Too Many Requests. Score is provisional.

## Where it got stuck (plain English)

- Most-used actions: `op_a` x1, `op_b` x1.
- The run stopped early on a backend failure (1 failed request(s): backend error at step 3: HTTP Error 429: Too Many Requests). That is an infrastructure failure, not a model decision — the model never got to reply — so this score is provisional and the run should be repeated before it is compared with completed runs.
- It never moved the progress metric at all in 3 steps — no milestone was ever reached, so there was no point in the run where the agent's actions added up to progress.

## Transcript

| Step | Action | Result |
|---|---|---|
| 1 | `op_a` | D1 |
| 2 | `op_b` | P9 |
| 3 | — | ERROR: backend error after retry: HTTP Error 429: Too Many Requests |
