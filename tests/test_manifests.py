"""Guards for the generated harness manifests.

Each test names the past mistake it fails on. Evidence lives in git history:
commit 7d933f6 fixed a marketplace entry that duplicated plugin.json components.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import manifests  # noqa: E402


def git_show(ref_path: str) -> str:
    return subprocess.check_output(["git", "show", ref_path], cwd=ROOT, text=True)


class GeneratedManifestsTest(unittest.TestCase):
    def test_committed_manifests_match_source(self) -> None:
        self.assertEqual(manifests.drifted(ROOT), [])

    def test_check_fails_and_names_the_fix_when_a_derived_file_is_hand_edited(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / manifests.SOURCE).write_text(
                (ROOT / manifests.SOURCE).read_text(encoding="utf-8"), encoding="utf-8"
            )
            manifests.generate(root)
            self.assertEqual(manifests.drifted(root), [])

            codex = root / ".codex-plugin/plugin.json"
            data = json.loads(codex.read_text(encoding="utf-8"))
            data["license"] = "MIT"  # the drift found on main before this change
            codex.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            self.assertEqual(manifests.drifted(root), [".codex-plugin/plugin.json"])

    def test_marketplace_entries_never_declare_components(self) -> None:
        # Commit 7d933f6: a marketplace entry carrying skills/mcpServers made
        # Claude Code refuse the plugin. The renderers cannot emit those keys.
        src = manifests.load_source(ROOT)
        for render in (manifests.render_claude_marketplace, manifests.render_cursor_marketplace):
            for entry in render(src)["plugins"]:
                with self.subTest(renderer=render.__name__):
                    self.assertFalse(manifests.MARKETPLACE_FORBIDDEN_KEYS & entry.keys())

    def test_check_rejects_the_exact_marketplace_shape_fixed_in_7d933f6(self) -> None:
        # Known limitation: `claude plugin validate .` passes on this shape
        # (verified locally on Claude Code 2.1.302), so this check is the only guard.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / manifests.SOURCE).write_text(
                (ROOT / manifests.SOURCE).read_text(encoding="utf-8"), encoding="utf-8"
            )
            manifests.generate(root)
            buggy = root / ".claude-plugin/marketplace.json"
            buggy.write_text(git_show("7d933f6~1:.claude-plugin/marketplace.json"), encoding="utf-8")
            self.assertIn(".claude-plugin/marketplace.json", manifests.drifted(root))

    def test_every_manifest_agrees_on_name_version_and_license(self) -> None:
        src = manifests.load_source(ROOT)
        for path, render in manifests.OUTPUTS.items():
            data = render(src)
            with self.subTest(path=path):
                if "plugins" in data:
                    self.assertEqual(data["plugins"][0]["name"], src["name"])
                elif "name" in data:
                    self.assertEqual(data["name"], src["name"])
                if "license" in data:
                    self.assertEqual(data["license"], src["license"])
                if "version" in data:
                    self.assertEqual(data["version"], src["version"])

    def test_mcp_server_is_declared_once(self) -> None:
        src = manifests.load_source(ROOT)
        self.assertEqual(manifests.render_mcp(src)["mcpServers"], src["mcp_servers"])
        self.assertEqual(manifests.render_gemini_extension(src)["mcpServers"], src["mcp_servers"])


if __name__ == "__main__":
    unittest.main()
