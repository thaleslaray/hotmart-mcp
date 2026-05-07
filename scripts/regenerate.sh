#!/usr/bin/env bash
# Regenerate src/hotmart_mcp/tools/ from specs/hotmart-api.json.
# Idempotent — overwrites every generated module.
set -euo pipefail
cd "$(dirname "$0")/.."
python -m hotmart_mcp.generator
