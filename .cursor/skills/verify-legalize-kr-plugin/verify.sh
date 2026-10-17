#!/usr/bin/env bash
# Drives the real artifacts this repo ships and leaves evidence in $EVIDENCE_DIR.
# Usage: .cursor/skills/verify-legalize-kr-plugin/verify.sh [feature]
#   feature: all (default) | manifests | zip | claude | mcp
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
EVIDENCE_DIR="${EVIDENCE_DIR:-$ROOT/dist/verify-evidence}"
mkdir -p "$EVIDENCE_DIR"
feature="${1:-all}"
cd "$ROOT"

run() { # name, command...
  local name="$1"; shift
  echo "== $name"
  if "$@" >"$EVIDENCE_DIR/$name.log" 2>&1; then echo "   ok  ($EVIDENCE_DIR/$name.log)"; else echo "   FAIL ($EVIDENCE_DIR/$name.log)"; tail -20 "$EVIDENCE_DIR/$name.log"; return 1; fi
}

want() { [ "$feature" = all ] || [ "$feature" = "$1" ]; }

want manifests && run manifests-check python3 scripts/manifests.py check
want manifests && run unit-tests python3 -m unittest discover -s tests -v
want zip && run zip-package python3 scripts/package_claude_plugin.py
want zip && run zip-validate python3 scripts/validate_claude_plugin_package.py dist/legalize-kr-plugin.zip
if want claude; then
  if command -v claude >/dev/null; then run claude-plugin-validate claude plugin validate .
  else run claude-plugin-validate npx -y @anthropic-ai/claude-code@latest plugin validate .; fi
fi
if want mcp; then
  # Real MCP handshake through the exact command .mcp.json declares.
  cmd=$(python3 -c 'import json;s=json.load(open(".mcp.json"))["mcpServers"]["legalize-kr"];print(" ".join([s["command"],*s["args"]]))')
  run mcp-handshake bash -c "(printf '%s\n' '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"verify\",\"version\":\"0\"}}}' '{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}' '{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}'; sleep 5) | timeout 170 $cmd | grep -q '\"tools\"'"
fi
echo "evidence: $EVIDENCE_DIR"
