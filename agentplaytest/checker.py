"""The AgentPlaytest checker loop.

The model under test receives exactly three things about the target app —
nothing else:

  1. a compact state snapshot (JSON),
  2. a text view (the app's own words about itself),
  3. the list of action names it may pick from.

It replies with one action per step. The checker applies the action, tracks
ground-truth progress (milestones + a progress function the target exposes
to the harness only), and detects the ways agents actually get stuck:
repeating an action with no state change, invalid replies, and long
no-progress stretches. The result is a score and a plain-English report.
"""
import hashlib
import json
import re

SYSTEM_PROMPT = (
    "You are an AI agent playtesting an app. You are not told the rules beyond "
    "what the app itself shows you. Each turn you receive the app's text view, "
    "its state as JSON, the list of actions you may take, and a short history "
    "of your own recent actions and what they did. Choose exactly "
    "ONE action and reply with only a JSON object like "
    '{"action": "ACTION_NAME", "why": "one short reason"}. '
    "Do not invent actions that are not in the list. "
    "If the app reports that an action failed or changed nothing, choosing "
    "the same action again will not help — pick a different one."
)


def build_user_prompt(target, step, max_steps, history=()):
    state = json.dumps(target.state(), indent=None, sort_keys=True)
    actions = "\n".join(f"- {a}" for a in target.actions())
    hist = ""
    if history:
        lines = "\n".join(f"- {a} -> {r}" for a, r in history)
        hist = f"\nYOUR RECENT ACTIONS (most recent last):\n{lines}\n"
    return (
        f"Step {step} of {max_steps}.\n\n"
        f"TEXT VIEW:\n{target.text_view()}\n\n"
        f"STATE (JSON):\n{state}\n"
        f"{hist}\n"
        f"ACTIONS YOU MAY TAKE:\n{actions}\n\n"
        "Reply with only the JSON object for your chosen action."
    )


def parse_action(reply, valid_actions):
    """Robustly extract an action: strict JSON first, then substring fallback."""
    if not reply:
        return None, "empty reply"
    m = re.search(r"\{.*?\}", reply, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(0))
            act = obj.get("action")
            if isinstance(act, str) and act in valid_actions:
                return act, obj.get("why", "")
            if isinstance(act, str):
                return None, f"model named an action not in the list: {act!r}"
        except json.JSONDecodeError:
            pass
    for a in valid_actions:
        if a in reply:
            return a, "(recovered: action named in free text)"
    return None, "no valid action found in reply"


def _state_hash(target):
    blob = json.dumps(target.state(), sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def run_playtest(target, backend, max_steps=60, verbose=False):
    steps = []
    invalid = 0
    loop_events = 0
    steps_since_progress = 0
    longest_stall = 0
    first_stall_step = None
    prev_hash = _state_hash(target)
    prev_action = None
    same_action_run = 0
    best_progress = target.progress()
    hit, _all = target.milestones()
    history = []  # last few (action, result) pairs, shown back to the model

    for step in range(1, max_steps + 1):
        if target.is_done():
            break
        prompt = build_user_prompt(target, step, max_steps, history[-6:])
        reply = None
        retried = False
        try:
            reply = backend.chat(SYSTEM_PROMPT, prompt)
        except Exception:
            retried = True  # one retry: a single slow generation must not kill a run
            try:
                reply = backend.chat(SYSTEM_PROMPT, prompt)
            except Exception as exc:
                steps.append({"step": step, "error": f"backend error after retry: {exc}"})
                invalid += 1
                break
        action, note = parse_action(reply, target.actions())
        record = {
            "step": step,
            "model_reply": reply.strip()[:400],
            "action": action,
            "note": (note + " [backend retried once]" if retried else note),
        }
        if action is None:
            invalid += 1
            steps.append(record)
            steps_since_progress += 1
            continue
        result = target.act(action)
        record["result"] = str(result)[:200]
        history.append((action, str(result)[:90]))
        new_hash = _state_hash(target)
        new_progress = target.progress()
        new_hit, _ = target.milestones()
        progressed = new_progress > best_progress + 1e-9 or len(new_hit) > len(hit)
        if action == prev_action and new_hash == prev_hash:
            same_action_run += 1
            if same_action_run == 2:  # third identical no-op in a row
                loop_events += 1
                record["loop"] = True
        else:
            same_action_run = 0
        if progressed:
            best_progress = max(best_progress, new_progress)
            hit = new_hit
            steps_since_progress = 0
        else:
            steps_since_progress += 1
            if steps_since_progress > longest_stall:
                longest_stall = steps_since_progress
                first_stall_step = step - steps_since_progress + 1
        prev_hash = new_hash
        prev_action = action
        steps.append(record)
        if verbose:
            print(f"  step {step:2d}: {action} -> {record['result'][:70]}")

    hit, all_milestones = target.milestones()
    milestone_frac = len(hit) / len(all_milestones) if all_milestones else 0.0
    score = 100.0 * (0.6 * milestone_frac + 0.4 * best_progress)
    score -= 2.0 * invalid + 5.0 * loop_events
    score = max(0.0, min(100.0, score))
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F"
    goal_reached = "goal_reached" in hit
    if goal_reached:
        verdict = "Model-playable: the agent reached the goal unaided."
    elif score >= 50:
        verdict = "Playable with friction: the agent made real progress but did not finish."
    else:
        verdict = "Not model-playable: the agent could not make meaningful progress unaided."

    return {
        "target": target.name,
        "backend": backend.kind,
        "model": getattr(backend, "model", "unknown"),
        "self_test": backend.kind == "scripted",
        "steps_taken": len(steps),
        "max_steps": max_steps,
        "milestones_hit": hit,
        "milestones_all": all_milestones,
        "progress": round(best_progress, 3),
        "invalid_replies": invalid,
        "loop_events": loop_events,
        "longest_stall_steps": longest_stall,
        "first_stall_step": first_stall_step,
        "score": round(score, 1),
        "grade": grade,
        "goal_reached": goal_reached,
        "verdict": verdict,
        "steps": steps,
    }
