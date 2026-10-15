#!/usr/bin/env bash
# Fetch a local inference runtime (llama.cpp) + a Gemma GGUF into .runtime/.
# All URLs are resolved from the official GitHub / HuggingFace APIs at run time.
set -euo pipefail
cd "$(dirname "$0")/.runtime"

if [ ! -x llama/llama-server ]; then
  echo "== resolving latest llama.cpp release with binaries =="
  url=$(curl -s "https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=10" \
    | python3 -c "
import json,sys
for r in json.load(sys.stdin):
    for a in r['assets']:
        n=a['name']
        if n.startswith('llama-') and n.endswith('-bin-ubuntu-x64.tar.gz'):
            print(a['browser_download_url']); sys.exit()
raise SystemExit('no ubuntu-x64 asset found')
")
  echo "downloading $url"
  curl -sL "$url" -o llama.tar.gz
  mkdir -p llama && tar --no-same-owner -xzf llama.tar.gz -C llama --strip-components=1
  rm llama.tar.gz
fi
ls -la llama/ | head

if [ ! -f models/gemma-3-1b-it-Q4_K_M.gguf ]; then
  echo "== resolving Gemma 3 1B GGUF file list =="
  file=$(curl -s https://huggingface.co/api/models/ggml-org/gemma-3-1b-it-GGUF \
    | python3 -c "import json,sys; d=json.load(sys.stdin); names=[s['rfilename'] for s in d['siblings']]; print(next(n for n in names if n.endswith('Q4_K_M.gguf')))")
  echo "downloading $file"
  curl -sL "https://huggingface.co/ggml-org/gemma-3-1b-it-GGUF/resolve/main/$file" -o models/gemma-3-1b-it-Q4_K_M.gguf
fi
ls -la models/
echo "SETUP DONE"
