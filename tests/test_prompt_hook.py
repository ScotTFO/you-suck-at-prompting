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
VALIDATE_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-plugin.yml"
EXPECTED_CONTEXT = (
    "MANDATORY: Use you-suck-at-prompting. Prompt-only: exact `You Suck At Prompting Rewritten prompt:` + fence; "
    "no gate. Else same + exact `Reply with an acknowledgement to use this prompt.` Missing: exact `Draft "
    "rewritten prompt:` + `[NEEDED: ...]`; one question, no ack. Ack executes; edits reset. Preserve "
    "safety/authority. For goals/loops/plans/graphs/agents/recurrence/review load execution-shapes. Excessive/"
    "unsupported orchestration: draft `[NEEDED: preserve or simplify]`; ask which; never replace silently."
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


if __name__ == "__main__":
    unittest.main()
