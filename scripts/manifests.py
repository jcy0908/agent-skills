#!/usr/bin/env python3
"""Generate every harness manifest from plugin.source.json, or check that none drifted.

    python3 scripts/manifests.py generate   # rewrite the derived manifests
    python3 scripts/manifests.py check      # exit 1 and name the fix if any drifted

The derived files are listed in OUTPUTS. Do not edit them by hand: CI runs `check`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "plugin.source.json"
MCP_PATH = "./.mcp.json"

# Keys a Claude marketplace entry must never carry. Claude Code refuses to load a
# plugin whose marketplace entry and plugin.json both declare components
# ("conflicting manifests", fixed in commit 7d933f6). The renderer below cannot
# emit them, and tests assert that.
MARKETPLACE_FORBIDDEN_KEYS = frozenset({"skills", "mcpServers", "agents", "commands", "hooks"})


def render_universal(src: dict) -> dict:
    return {
        "name": src["name"],
        "version": src["version"],
        "description": src["description"],
        "author": src["author"],
        "homepage": src["homepage"],
        "repository": src["repository"],
        "license": src["license"],
        "keywords": src["keywords"],
        "skills": src["skills_dir"],
        "mcpServers": MCP_PATH,
    }


def render_claude_plugin(src: dict) -> dict:
    return render_universal(src)


def render_codex_plugin(src: dict) -> dict:
    return {**render_universal(src), "interface": src["codex_interface"]}


def render_mcp(src: dict) -> dict:
    return {"mcpServers": src["mcp_servers"]}


def render_gemini_extension(src: dict) -> dict:
    return {
        "name": src["name"],
        "version": src["version"],
        "description": src["description"],
        "mcpServers": src["mcp_servers"],
    }


def render_claude_marketplace(src: dict) -> dict:
    market = src["marketplace"]
    entry = {
        "name": src["name"],
        "source": "./",
        "description": market["entry_description"],
        "version": src["version"],
        "homepage": src["homepage"],
        "repository": src["repository"],
        "license": src["license"],
        "strict": False,
        "category": market["category"],
        "tags": market["tags"],
    }
    assert not MARKETPLACE_FORBIDDEN_KEYS & entry.keys()
    return {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": market["name"],
        "owner": {"name": market["owner"]},
        "description": market["description"],
        "plugins": [entry],
    }


def render_cursor_marketplace(src: dict) -> dict:
    market = src["marketplace"]
    entry = {"name": src["name"], "description": market["entry_description"], "source": "./"}
    assert not MARKETPLACE_FORBIDDEN_KEYS & entry.keys()
    return {
        "name": market["name"],
        "owner": {"name": market["owner"]},
        "metadata": {"description": src["description"]},
        "plugins": [entry],
    }


OUTPUTS: dict[str, Callable[[dict], dict]] = {
    "plugin.json": render_universal,
    ".claude-plugin/plugin.json": render_claude_plugin,
    ".claude-plugin/marketplace.json": render_claude_marketplace,
    ".codex-plugin/plugin.json": render_codex_plugin,
    ".cursor-plugin/marketplace.json": render_cursor_marketplace,
    ".mcp.json": render_mcp,
    "gemini-extension.json": render_gemini_extension,
}


def load_source(root: Path = ROOT) -> dict:
    return json.loads((root / SOURCE).read_text(encoding="utf-8"))


def render_all(src: dict) -> dict[str, str]:
    return {
        path: json.dumps(render(src), ensure_ascii=False, indent=2) + "\n"
        for path, render in OUTPUTS.items()
    }


def generate(root: Path = ROOT) -> list[str]:
    changed = []
    for path, text in render_all(load_source(root)).items():
        target = root / path
        if not target.exists() or target.read_text(encoding="utf-8") != text:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            changed.append(path)
    return changed


def drifted(root: Path = ROOT) -> list[str]:
    out = []
    for path, text in render_all(load_source(root)).items():
        target = root / path
        if not target.exists() or target.read_text(encoding="utf-8") != text:
            out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["generate", "check"])
    args = parser.parse_args(argv)

    if args.command == "generate":
        for path in generate():
            print(f"wrote {path}")
        return 0

    bad = drifted()
    if bad:
        print("manifest drift detected in:", file=sys.stderr)
        for path in bad:
            print(f"  {path}", file=sys.stderr)
        print(
            f"\nThese files are generated from {SOURCE}. Edit {SOURCE} instead,"
            " then run: python3 scripts/manifests.py generate",
            file=sys.stderr,
        )
        return 1
    print("manifests in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
