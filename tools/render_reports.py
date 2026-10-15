#!/usr/bin/env python3
"""Render runs/report-*.md into simple standalone HTML for the demo viewer.

Deliberately tiny: headings, bold, inline code, tables and lists only —
just enough for the generated AgentPlaytest reports.
"""
import html
import os
import re
import sys

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")

CSS = """
body { font-family: system-ui, sans-serif; margin: 1rem; color: #1a1a2e; line-height: 1.45; }
table { border-collapse: collapse; font-size: .85rem; }
td, th { border: 1px solid #ccc; padding: 2px 6px; text-align: left; }
code { background: #eef; padding: 0 .2em; border-radius: 3px; }
"""


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def convert(md):
    out, in_table = [], False
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            tag = "</table>" if False else ""
            if not in_table:
                out.append("<table>")
                in_table = True
            out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            out.append(f"<p>&bull; {inline(line[2:])}</p>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    if in_table:
        out.append("</table>")
    return "\n".join(out)


def main():
    for name in sorted(os.listdir(RUNS)):
        if name.startswith("report-") and name.endswith(".md"):
            src = os.path.join(RUNS, name)
            dst = src[:-3] + ".html"
            with open(src) as f:
                body = convert(f.read())
            with open(dst, "w") as f:
                f.write(f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>")
            print("rendered", dst)


if __name__ == "__main__":
    sys.exit(main())
