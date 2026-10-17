# Generated harness manifests

Consumer: every harness (Claude Code, Cowork, Cursor, Codex, Gemini CLI, skills.sh).
Drive: `verify.sh manifests`.
Pass: `manifests in sync` and 8 unit tests OK.
Fail you will see most: `manifest drift detected in: <file>`. The fix is in the error text. Edit `plugin.source.json`, run `generate`.
