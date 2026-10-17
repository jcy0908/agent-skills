# Agent instructions

This repository publishes one skill (`skills/legalize-kr`) to several agent harnesses. Most mistakes here come from editing one of the harness manifests and not the others. The structure below makes that mistake fail in CI instead of in a user's install.

## Rules and what enforces them

| Rule | Enforced by |
|---|---|
| Edit `plugin.source.json`, never a generated manifest (`plugin.json`, `.claude-plugin/*.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/marketplace.json`, `.mcp.json`, `gemini-extension.json`). Then run `python3 scripts/manifests.py generate`. | `scripts/manifests.py check` in CI; `tests/test_manifests.py` |
| A marketplace entry never declares `skills`, `mcpServers`, `agents`, `commands`, or `hooks`. Those live in the plugin manifest only (commit 7d933f6). | Renderers in `scripts/manifests.py` cannot emit them; `test_marketplace_entries_never_declare_components` |
| The MCP server command is declared once (`mcp_servers` in the source). | Generator; `test_mcp_server_is_declared_once` |
| The Cowork ZIP's required-file list is derived from the packager's include list. | `scripts/validate_claude_plugin_package.py` imports `DEFAULT_INCLUDES` |
| Every manifest carries the same name, version, and license. | `test_every_manifest_agrees_on_name_version_and_license`; `claude plugin validate .` in CI |
| Before claiming a packaging change works, run the verification skill. | Judgment only. See `.cursor/skills/verify-legalize-kr-plugin/SKILL.md` |

When a human corrects you for a mistake not in this table, fix it and add a row. If the row exists but nothing enforces it, enforce it in the same change, at the highest level that works (structure, then types or checks, then tests, then prose).

## Local checks

```bash
python3 scripts/manifests.py check
python3 -m unittest discover -s tests
python3 scripts/package_claude_plugin.py && python3 scripts/validate_claude_plugin_package.py dist/legalize-kr-plugin.zip
claude plugin validate .
```
