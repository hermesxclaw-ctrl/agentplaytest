"""Plain-English report writer for AgentPlaytest runs.

The report is the product: a developer should be able to read it in two
minutes and know (a) whether an AI agent can use their app unaided,
(b) exactly where the agent got stuck, and (c) what evidence says so.
"""
from collections import Counter


def _diagnosis(run):
    lines = []
    steps = [s for s in run["steps"] if "action" in s or "model_reply" in s]
    actions = [s["action"] for s in steps if s.get("action")]
    if actions:
        common = Counter(actions).most_common(2)
        top_action, top_n = common[0]
        lines.append(
            "Most-used actions: "
            + ", ".join(f"`{a}` x{n}" for a, n in common)
            + "."
        )
        if top_n >= max(5, int(0.8 * len(actions))):
            lines.append(
                f"Fixation: `{top_action}` accounts for {top_n} of {len(actions)} steps. "
                "The agent locked onto one action and stopped exploring — the run tests "
                "that fixation more than it tests the app's full surface."
            )
    if run["invalid_replies"]:
        bad = [s for s in steps if s.get("action") is None and s.get("model_reply")]
        example = bad[0]["model_reply"][:120] if bad else ""
        lines.append(
            f"The model produced {run['invalid_replies']} repl"
            f"{'y' if run['invalid_replies'] == 1 else 'ies'} with no usable action"
            + (f'. First example: "{example}"' if example else "")
            + " — nothing in the reply mapped to a listed action, so the step was wasted."
        )
    if run.get("backend_errors"):
        lines.append(
            f"The run stopped early on a backend failure ({run['backend_errors']} failed "
            f"request(s): {run.get('incomplete_reason', 'see transcript')}). That is an "
            "infrastructure failure, not a model decision — the model never got to reply — "
            "so this score is provisional and the run should be repeated before it is "
            "compared with completed runs."
        )
    if run["loop_events"]:
        cycles = run.get("cycles_detected") or []
        if cycles:
            lines.append(
                f"It fell into {run['loop_events']} repeat cycle(s) — short action patterns "
                f"repeated with the state returning to where the cycle started and no "
                f"progress inside it ({'; '.join(cycles)}). The agent kept issuing actions "
                "that changed nothing; whether the app's feedback was uninterpretable or "
                "the model failed to adapt to clear feedback, the transcript shows exactly "
                "which actions and results repeated."
            )
        else:
            lines.append(
                f"It fell into {run['loop_events']} repeat loop(s): the same action three times "
                "in a row with the state not changing at all. The agent kept issuing an action "
                "that changed nothing — the transcript shows what feedback it was getting."
            )
    if run["longest_stall_steps"] >= 4:
        lines.append(
            f"Longest no-progress stretch: {run['longest_stall_steps']} steps, starting at "
            f"step {run['first_stall_step']}. During a stall the agent is spending tokens "
            "without moving any milestone — in a paid agent product this is literally burning money."
        )
    if run["goal_reached"]:
        lines.append(
            f"The agent reached the goal in {run['steps_taken']} steps with "
            f"{run['invalid_replies']} invalid replies."
        )
    elif run["progress"] > 0:
        lines.append(
            f"It got {round(run['progress'] * 100)}% of the way to the goal (in cash terms) "
            "before the run ended."
        )
    else:
        lines.append(
            "It never moved the progress metric at all in "
            f"{run['steps_taken']} steps — no milestone was ever reached, so there "
            "was no point in the run where the agent's actions added up to progress."
        )
    return lines


def write_markdown(run, path):
    stamp = "SELF-TEST (scripted player — NOT model evidence)" if run["self_test"] else f"Model: {run['model']} via {run['backend']}"
    lines = [
        f"# AgentPlaytest report — {run['target']}",
        "",
        f"**Playtester:** {stamp}  ",
        f"**Score:** {run['score']}/100 (grade {run['grade']})  ",
        f"**Verdict:** {run['verdict']}  ",
        f"**Steps:** {run['steps_taken']} of {run['max_steps']} max  ",
        f"**Milestones:** {len(run['milestones_hit'])}/{len(run['milestones_all'])} — "
        + (", ".join(run["milestones_hit"]) or "none"),
    ]
    if run.get("incomplete"):
        lines.append(
            f"**Status:** INCOMPLETE — {run.get('incomplete_reason', 'backend error')}. "
            "Score is provisional."
        )
    lines += [
        "",
        "## Where it got stuck (plain English)",
        "",
    ]
    lines += [f"- {d}" for d in _diagnosis(run)]
    lines += ["", "## Transcript", "", "| Step | Action | Result |", "|---|---|---|"]
    for s in run["steps"]:
        if "error" in s:
            lines.append(f"| {s['step']} | — | ERROR: {s['error']} |")
        elif s.get("action") is None:
            lines.append(f"| {s['step']} | (invalid reply) | {s.get('note', '')} |")
        else:
            res = str(s.get("result", "")).replace("|", "/")
            marker = " [LOOP]" if s.get("loop") else ""
            lines.append(f"| {s['step']} | `{s['action']}`{marker} | {res} |")
    lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))
