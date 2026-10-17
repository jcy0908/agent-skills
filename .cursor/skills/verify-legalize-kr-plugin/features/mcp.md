# MCP server launch

Consumer: any MCP host reading `.mcp.json` or `gemini-extension.json`.
Drive: `verify.sh mcp`. It runs the exact `command` + `args` from `.mcp.json`, sends `initialize`, then `tools/list`.
Pass: a JSON-RPC result containing `"tools"`. Verified 2026-10-17: server `legalize-kr` answered with `laws_list` and the rest of the tool surface.
Needs: `uvx` and network on first run.
