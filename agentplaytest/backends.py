"""Model backends for AgentPlaytest.

The playtester is a local open-weight model. AgentPlaytest talks to it over
plain HTTP, so any local runtime works:

  - backend "llamacpp": llama.cpp's llama-server (OpenAI-compatible API).
    This is what the captured demo runs in this repo used, because the build
    machine had no Ollama and ~1 GB of free RAM — llama.cpp plus a 4-bit
    Gemma 3 1B GGUF was the smallest practical local route. See README.
  - backend "ollama": Ollama's /api/chat. Same checker, same prompts —
    on a normal laptop this is the one-command option (`ollama run gemma3`).

A third backend, "scripted", is a tiny rule-based player. It exists ONLY to
smoke-test the checker harness itself without a model. Its output files are
stamped SELF-TEST and must never be presented as model evidence.
"""
import json
import urllib.request


def _post(url, payload, timeout=600):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


class LlamaCppBackend:
    kind = "llamacpp"

    def __init__(self, base_url="http://localhost:8080", model="gemma-3-1b-it"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, system, user):
        out = _post(
            f"{self.base_url}/v1/chat/completions",
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
                "max_tokens": 80,
            },
        )
        return out["choices"][0]["message"]["content"]


class OllamaBackend:
    kind = "ollama"

    def __init__(self, base_url="http://localhost:11434", model="gemma3:1b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, system, user):
        out = _post(
            f"{self.base_url}/api/chat",
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 80, "num_ctx": 4096},
            },
        )
        return out["message"]["content"]


class ScriptedBackend:
    """Rule-based stand-in player for harness smoke tests ONLY."""

    kind = "scripted"

    def __init__(self, model="scripted-rules"):
        self.model = model

    def chat(self, system, user):
        # Deliberately naive rules over the friendly target's field names.
        # On the hostile target it cannot read the state and flails, which is
        # fine — this backend is never used as evidence either way.
        import re

        def grab(pat, default=0):
            m = re.search(pat, user)
            return int(m.group(1)) if m else default

        stock = grab(r'"snacks_in_stock":\s*(\d+)')
        opened = '"already_opened_today": true' in user
        if stock == 0:
            action = "buy_10_snacks"
        elif not opened:
            action = "open_the_stand"
        else:
            action = "end_the_day"
        return json.dumps({"action": action, "why": "scripted rule"})


BACKENDS = {
    "llamacpp": LlamaCppBackend,
    "ollama": OllamaBackend,
    "scripted": ScriptedBackend,
}
