#!/bin/bash
set -e

echo "🏗️  AI‑Trading demo bootstrap …"

# ------------------------------------------------------------------ venv
VENV=".venv-new"
PYTHON=$(command -v python3)           # always python3

# nuke the old broken venv, keep things clean
[ -d ".venv" ] && rm -rf .venv

if [ ! -d "$VENV" ]; then
  echo "📦 Creating virtual env ($VENV)…"
  "$PYTHON" -m venv "$VENV"
fi
source "$VENV/bin/activate"

# ------------------------------------------------------------------ pip fix
"$PYTHON" -m ensurepip --upgrade  >/dev/null 2>&1
"$PYTHON" -m pip install -q --upgrade pip setuptools wheel

# ------------------------------------------------------------------ deps
echo "📚 Installing demo requirements …"
"$PYTHON" -m pip install -q -r requirements-demo.txt

# ------------------------------------------------------------------ run
export PYTHONPATH=$PWD
echo "🚀 Launching demo …"
"$PYTHON" demo/DemoRunner.py
echo "✅ Demo done – see demo/demo_plot.png"
echo "🌐 Dashboard  http://localhost:8000/dash   (if docker compose up -d)"
