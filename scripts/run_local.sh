#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "KoStreet local startup helper"
echo
echo "Frontend:"
echo "  cd ${ROOT_DIR}/frontend"
echo "  npm install"
echo "  npm run dev"
echo
echo "Backend:"
echo "  cd ${ROOT_DIR}/backend"
echo "  python -m venv .venv"
echo "  source .venv/bin/activate"
echo "  pip install -e '.[dev]'"
echo "  uvicorn app.main:app --reload --port 8001"
echo
echo "AI package:"
echo "  cd ${ROOT_DIR}/ai"
echo "  python -m venv .venv"
echo "  source .venv/bin/activate"
echo "  pip install -e '.[dev]'"

