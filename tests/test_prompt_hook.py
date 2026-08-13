import ast
import json
import os
import hashlib
import re
import subprocess
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "you-suck-at-prompting"
HOOK_PATH = PLUGIN_ROOT / "hooks" / "hooks.json"
AGENT_PLUGIN_PATH = PLUGIN_ROOT / "plugin.json"
CODEX_MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
COPILOT_ADAPTER_PATH = (
    PLUGIN_ROOT / "copilot" / "you-suck-at-prompting.instructions.md"
)
VALIDATE_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-plugin.yml"
SKILL_PATH = PLUGIN_ROOT / "skills" / "you-suck-at-prompting" / "SKILL.md"
REPAIR_CONTRACT_PATH = (
    PLUGIN_ROOT / "skills" / "you-suck-at-prompting" / "references" / "repair-contract.md"
)
MATERIALITY_CONTRACT_PATH = (
    PLUGIN_ROOT / "skills" / "you-suck-at-prompting" / "references" / "materiality-and-authority.md"
)
KICKOFF = "Analyzing whether You Suck at Prompting… your prompt’s performance review is underway."
EXPECTED_CONTEXT = (
    f"MANDATORY: Use you-suck-at-prompting. Rewrite/draft starts once with exact {KICKOFF}, then exact "
    "heading+fence. Approval ends exact ack; prompt-only none. Missing: [NEEDED: ...]; ask once, no ack. "
    "Ack runs once, no kickoff. Preserve safety/authority. Goals/loops/plans/graphs/agents/recurrence/review: "
    "load execution-shapes. Excessive/unsupported orchestration: [NEEDED: preserve or simplify]; ask which; "
    "never replace silently."
)


class PromptHookTests(unittest.TestCase):
    def config(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def handler(self, path: Path) -> dict:
        config = self.config(path)
        return config["hooks"]["UserPromptSubmit"][0]["hooks"][0]

    def file_snapshot(self) -> dict[str, str]:
        return {
            path.relative_to(PLUGIN_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file()
        }

    def run_handler(self, harness: str, handler: dict, payload: str) -> subprocess.CompletedProcess[str]:
        if harness == "codex":
            command = handler["commandWindows"] if os.name == "nt" else handler["command"]
            argv = command if os.name == "nt" else ["sh", "-c", command]
            shell = os.name == "nt"
        elif os.name == "nt":
            argv = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", handler["command"]]
            shell = False
        else:
            argv = ["sh", "-c", handler["command"]]
            shell = False
        return subprocess.run(
            argv,
            cwd=PLUGIN_ROOT,
            input=payload,
            text=True,
            encoding="utf-8",
            capture_output=True,
            shell=shell,
            timeout=handler["timeout"],
            check=False,
        )

    def test_hooks_are_bounded_automatic_and_harness_native(self) -> None:
        config = self.config(HOOK_PATH)
        self.assertEqual(set(config["hooks"]), {"UserPromptSubmit"})
        groups = config["hooks"]["UserPromptSubmit"]
        self.assertEqual(len(groups), 1)
        self.assertNotIn("matcher", groups[0])
        self.assertEqual(len(groups[0]["hooks"]), 1)

        handler = self.handler(HOOK_PATH)
        self.assertEqual(handler["type"], "command")
        self.assertEqual(handler["timeout"], 5)
        self.assertEqual(handler["additionalContextLimit"], 512)
        self.assertLessEqual(len(EXPECTED_CONTEXT), handler["additionalContextLimit"])
        self.assertIn("load execution-shapes", EXPECTED_CONTEXT)
        self.assertIn("[NEEDED: preserve or simplify]", EXPECTED_CONTEXT)
        self.assertIn("commandWindows", handler)
        self.assertNotIn("async", handler)

    def test_agent_plugin_is_portable_hook_free_and_version_aligned(self) -> None:
        agent_plugin = self.config(AGENT_PLUGIN_PATH)
        codex_manifest = self.config(CODEX_MANIFEST_PATH)
        claude_manifest = self.config(CLAUDE_MANIFEST_PATH)

        self.assertEqual(
            agent_plugin["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        )
        self.assertEqual(agent_plugin["name"], "you-suck-at-prompting")
        self.assertEqual(
            agent_plugin["name"], codex_manifest["name"], claude_manifest["name"]
        )
        self.assertEqual(
            agent_plugin["version"], codex_manifest["version"], claude_manifest["version"]
        )
        self.assertNotIn("hooks", agent_plugin)
        self.assertNotIn("extensions", agent_plugin)

    def test_copilot_adapter_preserves_the_visible_gate_and_boundaries(self) -> None:
        adapter = COPILOT_ADAPTER_PATH.read_text(encoding="utf-8")

        self.assertTrue(adapter.startswith("---\n"))
        self.assertIn('applyTo: "**"', adapter)
        self.assertEqual(adapter.count(KICKOFF), 1)
        self.assertIn("load and follow the installed `you-suck-at-prompting` agent skill", adapter)
        self.assertIn("Reply with an acknowledgement to use this prompt.", adapter)
        self.assertIn("Draft rewritten prompt:", adapter)
        self.assertIn("[NEEDED: ...]", adapter)
        self.assertIn("prompt rewriting or critique", adapter)
        self.assertIn("Execute it once without displaying the kickoff", adapter)
        self.assertIn("A clarification, edit, or qualification", adapter)
        self.assertIn("Never retain a real usage prompt automatically", adapter)
        self.assertIn("`SAVE CASE`", adapter)
        self.assertIn("separate approvals for publishing", adapter)

    def test_ci_validator_uses_the_same_hook_context(self) -> None:
        workflow = VALIDATE_WORKFLOW_PATH.read_text(encoding="utf-8")
        match = re.search(
            r"expected_context = \(\n(?P<body>.*?)\n\s+\)\n\s+if len\(expected_context\)",
            workflow,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "validate workflow has no expected_context block")
        expression = "(\n" + textwrap.dedent(match.group("body")) + "\n)"
        self.assertEqual(ast.literal_eval(expression), EXPECTED_CONTEXT)

    def test_hooks_emit_identical_constant_context_without_retaining_input(self) -> None:
        sentinel = "PRIVATE_PROMPT_MUST_NOT_APPEAR"
        payload = json.dumps(
            {
                "hook_event_name": "UserPromptSubmit",
                "turn_id": "test-turn",
                "prompt": sentinel,
            }
        )
        before = self.file_snapshot()
        outputs = []
        for harness in ("codex", "claude"):
            with self.subTest(harness=harness):
                result = self.run_handler(harness, self.handler(HOOK_PATH), payload)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertEqual(result.stdout.strip(), EXPECTED_CONTEXT)
                self.assertNotIn(sentinel, result.stdout + result.stderr)
                outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(self.file_snapshot(), before)

    def test_shared_kickoff_is_exact_once_and_skipped_for_acknowledgements(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair_contract = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(EXPECTED_CONTEXT.count(KICKOFF), 1)
        self.assertEqual(skill.count(KICKOFF), 1)
        self.assertEqual(repair_contract.count(KICKOFF), 1)
        self.assertEqual(readme.count(KICKOFF), 1)
        self.assertLess(skill.index(KICKOFF), skill.index("**APPROVAL-READY:**"))
        self.assertIn("Ack runs once, no kickoff", EXPECTED_CONTEXT)
        self.assertIn("Do not use it when a clear affirmative acknowledgement executes", skill)

    def test_task_contract_takeaways_remain_selective_and_evidence_based(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        materiality = MATERIALITY_CONTRACT_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for text in (skill, materiality, repair):
            self.assertIn("Expected prompt impact:", text)
            self.assertIn("Recommended default:", text)
            self.assertLess(text.index("Expected prompt impact:"), text.index("Recommended default:"))
        self.assertIn("If any condition fails, do not ask", materiality)
        self.assertIn("permissions, deployment, deletion, sending, migration, publishing, purchases", materiality)
        self.assertIn("Make vague quality terms observable", skill)
        self.assertIn("smallest observable criteria", materiality)
        self.assertIn("Confidence language alone is not verification", skill)
        self.assertIn("every page or view of a multi-part artifact", skill)
        self.assertIn("Confidence language alone does not count as evidence", repair)
        self.assertIn("Inspect every page or view of a multi-part artifact", repair)
        self.assertIn("Do not require explanatory meta-language", repair)
        self.assertIn("result or artifact location", repair)
        self.assertIn("actions awaiting separate approval", repair)
        self.assertIn("Multiple routine local steps alone do not trigger it", repair)
        self.assertIn("routine direct work stays compact", readme)
        self.assertIn("the direct approach is a safe reversible default", skill)

    def test_all_versioned_manifests_are_aligned_at_patch_version(self) -> None:
        versions = {
            self.config(CODEX_MANIFEST_PATH)["version"],
            self.config(CLAUDE_MANIFEST_PATH)["version"],
            self.config(AGENT_PLUGIN_PATH)["version"],
        }

        self.assertEqual(versions, {"0.5.1"})
        self.assertNotIn("version", self.config(ROOT / ".claude-plugin" / "marketplace.json"))
        self.assertNotIn("version", self.config(ROOT / ".agents" / "plugins" / "marketplace.json"))


if __name__ == "__main__":
    unittest.main()
