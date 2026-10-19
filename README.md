# AgentPlaytest

**Can an AI agent actually use your app? Now you can measure it.**

AgentPlaytest is a model-playability checker for games and small web apps.
It hands a local open-weight model exactly three things about your app —

1. a compact **state snapshot** (JSON),
2. a **text view** (your app's own words about itself), and
3. a small set of **action names** —

then watches the model try to make progress, unaided. It scores the run
and writes a plain-English report of *where the agent got stuck and why*:
repeat loops, invalid replies, long no-progress stalls, milestones missed.

Every agent framework demo shows a model succeeding on an interface that
was designed for it. AgentPlaytest tests the other 99% of software: the
apps whose buttons are called `op_a`, whose state is `{"d":3,"c":48,"s":4}`,
and whose feedback is the code `S2`. If an AI agent is going to be your
next user, this is the test that tells you whether it can be.

## The demo: same game, two interfaces

`targets/` contains a tiny business game, **Snack Stand** (buy snacks at
$2, sell them during a 7-day week, finish with $70+). It ships with two
interfaces over the *identical* simulation:

- `friendly` — plain state names, the goal stated up front, every action
  explained in the text view.
- `hostile` — the same game wearing a disguise real software wears by
  accident: coded keys, tier indexes instead of dollars, meaningless
  action names in scrambled order, decoy stats, one-letter result codes,
  and the goal never mentioned anywhere.

Same checker, same model, same rules — the game simulation, harness and
model are held constant while the interface contract changes *as a bundle*
(goal visibility, state naming, action naming, feedback style all change
together, the way real software degrades). Captured reports live in `runs/`.

**Read the results honestly:** there is one captured run per cell, the two
4B runs used different step budgets (60 configured for friendly, 20 for
hostile), and the friendly 4B run stopped early on a backend timeout. These
are illustrative results from an initial experiment — a proof of concept,
not a statistically validated benchmark. The score is a prototype heuristic
(60% milestones + 40% best progress, minus penalties), computed from
target-supplied progress and milestone functions, so scores are comparable
across runs of the *same* target, not yet across different apps.

**Which model?** Captured results (all fully local, llama.cpp):

| Playtester | Friendly interface | Hostile interface |
|---|---|---|
| Gemma 3 4B (Q3) | **35.0 (D)** — real play: bought, sold, 2/4 milestones, then fixated on re-setting its price and never ended a day | **0.0 (F)** — cycled `op_c`/`op_d` into the same `E04` error for 20 steps, zero milestones, never moved the progress metric at all |
| Gemma 3 1B (Q4) | **0.0 (F)** — repeated its first action for 60 straight steps | **0.0 (F)** — picked `op_a` (end day) 7 times and skipped the entire week without learning anything |

The 4B friendly run ended at step 14 when a client timeout hit a slow
generation on the shared 2-core build box — the transcript in `runs/`
shows exactly where and says so. The 4B hostile run was captured on
2026-10-18 with a 20-step budget (see `runs/report-hostile-4b.md`),
completing the grid.

Each row holds the model and harness constant while the interface bundle
differs. The 4B row is the headline: a more capable
playtester turns the friendly interface into real, scoreable play
(35.0), and the *same* model scores absolute zero the moment the
interface stops explaining itself. That became one of the project's
genuine findings: a playability score measures model × interface
together, and below a capability floor the model is the bottleneck no
matter how good the interface is. AgentPlaytest says so in its own
reports instead of hiding it — which is rather the point of a testing
tool.

### Review fixes (2026-10-18)

An external review tore the first version of this checker apart, and three
of its findings were real bugs. They are fixed in the current code:

- **Backend failures are no longer scored as model failures.** A timeout or
  HTTP error used to increment the same counter as a malformed model reply,
  and the report then claimed the model "produced a reply with no usable
  action" when it never got to reply at all. Backend errors now have their
  own counter, and a run that dies on one is marked **incomplete** with a
  provisional score. Honest bookkeeping note: the captured 4B friendly
  score of 35.0 was recorded under the old accounting, which charged that
  run a 2-point penalty for its step-14 timeout. The captured score stands
  as recorded; new runs account correctly.
- **The stuck detector now sees action cycles.** It used to catch only the
  *same* action repeated — it was blind to an agent alternating between two
  actions forever. It now detects repeated short cycles (2–4 actions) that
  return the state to where the cycle started with no progress inside it.
  The captured 4B hostile report predates this fix and shows
  `loop_events: 0`, even though its transcript is exactly an
  `op_c`/`op_d` cycle — the current checker flags that pattern (there is a
  regression test with a cycling fake model to prove it).
- **A clean clone reproduces again.** `setup-runtime.sh` used to `cd` into
  `.runtime/` before creating it (the directory is gitignored, so a fresh
  clone failed at step one), and `run-demo.sh` used output labels that
  collided with the captured artifacts. Both are fixed; reproduction runs
  get their own labels and can never overwrite captured evidence.

## Running it

You need a local model server. The checker speaks plain HTTP, so either
runtime works:

**llama.cpp (what the captured demo runs used)**

```bash
./setup-runtime.sh   # downloads llama.cpp + Gemma 3 1B (Q4) into .runtime/
.runtime/llama/llama-server -m .runtime/models/gemma-3-1b-it-Q4_K_M.gguf \
    --host 127.0.0.1 --port 8080 -c 4096 &
python3 playtest.py --target friendly --backend llamacpp
python3 playtest.py --target hostile  --backend llamacpp
```

The captured runs used two Gemma sizes on the same stack: Gemma 3 1B-it
Q4_K_M (ggml-org) and Gemma 3 4B-it Q3_K_M (`gemma-3-4b-it-Q3_K_M.gguf`,
unsloth's GGUF conversion of Google's weights), served with `-c 2048`.
Swap the `-m` path and pass `--model <name>` to reproduce them
(`run-demo.sh` runs a 20-step pair back to back).

**Ollama (one-command option on a normal laptop)**

```bash
ollama pull gemma3:1b
ollama serve &   # if not already running
python3 playtest.py --target friendly --backend ollama --model gemma3:1b
```

### Why llama.cpp for the captured runs (honest note)

The machine these demo runs were captured on had no Ollama installed and
roughly 1–2 GB of free RAM. llama.cpp plus quantized Gemma GGUFs was the
smallest practical way to run real open-weight Gemma models fully locally
on it: a 4-bit Gemma 3 1B (~670 MB) for the capability-floor runs, and a
Q3_K_M Gemma 3 4B (~2.1 GB) for the headline captures. The checker is
deliberately runtime-agnostic — prompts, scoring, and reports are
identical either way — and the Ollama path above is the recommended
setup for your own machine. The playtester is Gemma in both cases; only
the serving runtime differs.

## Scoring

Score = 100 × (0.6 × milestones hit + 0.4 × progress toward the goal)
− 2 per invalid reply − 5 per repeat-loop event, clamped to 0–100,
graded A–F, with one of three verdicts: *model-playable*,
*playable with friction*, or *not model-playable*.

## The target protocol

Any app can be playtested if it exposes, in-process:

```python
state()      -> dict   # compact snapshot, JSON-serializable
text_view()  -> str    # the app's own description of the situation
actions()    -> [str]  # the only actions the model may pick
act(action)  -> str    # apply one action, return the app's feedback
# harness-only (never shown to the model):
progress()   -> float 0..1
milestones() -> (hit, all)
is_done()    -> bool
```

## Layout

```
playtest.py            CLI entry point
setup-runtime.sh       fetches llama.cpp + Gemma GGUF (URLs resolved via APIs)
agentplaytest/         the checker: backends.py, checker.py, report.py
targets/               snackstand.py (the sim) + friendly.py + hostile.py
runs/                  captured reports (.md) and transcripts (.json)
demo/index.html        static side-by-side viewer for the captured reports
```

## Who would pay for this?

Indie game devs and agent-tool builders are shipping "AI-playable"
features with no way to test them except vibes. AgentPlaytest is the
regression test for that claim: run it in CI, watch the score, and get a
readable report when a UI change quietly breaks your agent users. A
hosted "send us your app, get a report" tier is the paid lane; the local
checker stays open.

## License

MIT. Original code, written for the DEV Hacktoberfest Open-Source AI
Challenge, Week 2: Side Hustle (October 2026).
