---
name: verify-legalize-kr-plugin
description: Prove the legalize-kr plugin repo still installs and runs for every harness it ships to. Use before claiming a manifest, packaging, skill, or CI change works, or when asked to verify this repo.
---

# Verify the legalize-kr plugin

The surface a user touches is not an app. It is four artifacts: the generated harness manifests, the Cowork ZIP, the Claude Code plugin load, and the `legalize-mcp` server that `.mcp.json` launches. Verification drives each one as the harness would.

## Launch

Nothing long-running starts. Each check is a process that exits. Run from the repo root:

```bash
.cursor/skills/verify-legalize-kr-plugin/verify.sh            # everything
.cursor/skills/verify-legalize-kr-plugin/verify.sh manifests  # one feature, see features/
```

Ready means the script prints `evidence: <dir>` and no `FAIL` line.

## Doctor

Before trusting a failure, confirm the instance is worth driving:

```bash
python3 --version          # 3.10+ (scripts use PEP 604 unions)
claude --version           # optional; the script falls back to npx
uvx --version              # needed only for the mcp feature
git status --short         # generated manifests must be clean, else run generate first
```

## Drive

The script is the harness. Checks it runs, in order, with the exact command each harness runs:

| Feature | Command | Proves |
|---|---|---|
| manifests | `python3 scripts/manifests.py check`, `unittest` | derived manifests match `plugin.source.json`; PR 7d933f6's shape is rejected |
| zip | `package_claude_plugin.py` then `validate_claude_plugin_package.py` | the Cowork upload ZIP has the required files and nothing stray |
| claude | `claude plugin validate .` | Claude Code accepts marketplace and plugin manifests with no warnings |
| mcp | JSON-RPC `initialize` + `tools/list` piped into the command from `.mcp.json` | the server the manifests point at actually starts and lists tools |

## Evidence

Every check writes `dist/verify-evidence/<check>.log`. A proof is the log of the real command, not a paraphrase. Quote the `tools/list` line for MCP and the `Validation passed` line for Claude. `dist/` is gitignored, so evidence survives cleanup but never lands in a commit.

## Cleanup

The script starts no daemons. The MCP handshake is bounded by `timeout 170` and exits with the pipe. Delete `dist/` only if you want to clear old evidence.

## Known gaps

- `claude plugin validate .` passes on the PR 7d933f6 bug (checked on Claude Code 2.1.302). Only `manifests.py check` and the tests catch it.
- An interactive `claude --plugin-dir .` load is not scripted. It needs an authenticated session.
- The mcp feature downloads `legalize-cli[mcp]` through `uvx` on first run and needs network access.
