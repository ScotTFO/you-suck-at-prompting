import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "you-suck-at-prompting"
HOOK_PATH = PLUGIN_ROOT / "hooks" / "hooks.json"
EXPECTED_CONTEXT = (
    "Before acting on this request, apply the installed you-suck-at-prompting skill as a private "
    "preflight. Keep PASS outcomes silent. Do not broaden granted authority or execute a rewritten "
    "prompt without approval."
)


class PromptHookTests(unittest.TestCase):
    def handler(self) -> dict:
        config = json.loads(HOOK_PATH.read_text(encoding="utf-8"))
        return config["hooks"]["UserPromptSubmit"][0]["hooks"][0]

    def test_hook_contract_is_bounded_and_automatic(self) -> None:
        config = json.loads(HOOK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(config["hooks"]), {"UserPromptSubmit"})
        group = config["hooks"]["UserPromptSubmit"][0]
        self.assertNotIn("matcher", group)

        handler = self.handler()
        self.assertEqual(handler["type"], "command")
        self.assertEqual(handler["timeout"], 5)
        self.assertEqual(handler["additionalContextLimit"], 256)
        self.assertNotIn("async", handler)

    def test_hook_emits_only_constant_context(self) -> None:
        sentinel = "PRIVATE_PROMPT_MUST_NOT_APPEAR"
        payload = json.dumps(
            {
                "hook_event_name": "UserPromptSubmit",
                "turn_id": "test-turn",
                "prompt": sentinel,
            }
        )
        handler = self.handler()
        command = handler["commandWindows"] if os.name == "nt" else handler["command"]
        result = subprocess.run(
            command,
            cwd=PLUGIN_ROOT,
            input=payload,
            text=True,
            capture_output=True,
            shell=True,
            timeout=handler["timeout"],
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.strip(), EXPECTED_CONTEXT)
        self.assertNotIn(sentinel, result.stdout)


if __name__ == "__main__":
    unittest.main()
