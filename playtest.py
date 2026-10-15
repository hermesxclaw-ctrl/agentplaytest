#!/usr/bin/env python3
"""AgentPlaytest CLI.

Usage:
  python3 playtest.py --target friendly --backend llamacpp --max-steps 60
  python3 playtest.py --target hostile  --backend ollama --model gemma3:1b

Writes a Markdown report + JSON transcript into runs/ (or --outdir).
Targets expose state() / text_view() / actions() to the model, and
act() / progress() / milestones() / is_done() to the harness only.
"""
import argparse
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentplaytest.backends import BACKENDS          # noqa: E402
from agentplaytest.checker import run_playtest       # noqa: E402
from agentplaytest.report import write_markdown      # noqa: E402

TARGETS = {"friendly": "targets.friendly", "hostile": "targets.hostile"}


def main():
    ap = argparse.ArgumentParser(description="Playtest a target app with a local model.")
    ap.add_argument("--target", choices=sorted(TARGETS), required=True)
    ap.add_argument("--backend", choices=sorted(BACKENDS), default="llamacpp")
    ap.add_argument("--model", default=None, help="model name passed to the backend")
    ap.add_argument("--base-url", default=None, help="override backend base URL")
    ap.add_argument("--max-steps", type=int, default=60)
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs"))
    ap.add_argument("--label", default=None, help="filename label (default: target name)")
    args = ap.parse_args()

    module = importlib.import_module(TARGETS[args.target])
    target = module.make_target()

    backend_cls = BACKENDS[args.backend]
    kwargs = {}
    if args.model:
        kwargs["model"] = args.model
    if args.base_url:
        kwargs["base_url"] = args.base_url
    backend = backend_cls(**kwargs)

    print(f"[agentplaytest] target={target.name} backend={backend.kind} model={backend.model}")
    run = run_playtest(target, backend, max_steps=args.max_steps, verbose=True)

    os.makedirs(args.outdir, exist_ok=True)
    label = args.label or args.target
    md_path = os.path.join(args.outdir, f"report-{label}.md")
    json_path = os.path.join(args.outdir, f"run-{label}.json")
    write_markdown(run, md_path)
    with open(json_path, "w") as f:
        json.dump(run, f, indent=2)
    print(f"[agentplaytest] score={run['score']} grade={run['grade']} — {run['verdict']}")
    print(f"[agentplaytest] report: {md_path}")
    print(f"[agentplaytest] transcript: {json_path}")


if __name__ == "__main__":
    main()
