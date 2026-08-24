import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "you-suck-at-prompting"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "you-suck-at-prompting"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
OPENAI_PATH = SKILL_ROOT / "agents" / "openai.yaml"
REPAIR_CONTRACT_PATH = SKILL_ROOT / "references" / "repair-contract.md"
MATERIALITY_CONTRACT_PATH = SKILL_ROOT / "references" / "materiality-and-authority.md"
AGENT_PLUGIN_PATH = PLUGIN_ROOT / "plugin.json"
CODEX_MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
HOOK_PATH = PLUGIN_ROOT / "hooks" / "hooks.json"
COPILOT_ADAPTER_PATH = (
    PLUGIN_ROOT / "copilot" / "you-suck-at-prompting.instructions.md"
)
KICKOFF = "Analyzing whether You Suck at Prompting… your prompt’s performance review is underway."
EXPECTED_DESCRIPTION = (
    "Use this skill to audit or repair prompts when the user explicitly asks to write, "
    "rewrite, critique, clarify, or quality-check a prompt, directly invokes You Suck at "
    "Prompting, or when a task request has a material problem such as ambiguity, conflicting "
    "constraints, missing authority, unclear scope or destination, missing success criteria, "
    "or an execution design that could change the outcome. Do not use it for clear, actionable, "
    "exploratory, conversational, or safely discoverable requests, simple follow-ups or "
    "acknowledgements, minor wording issues, or optional improvements. If no material repair "
    "is needed, proceed silently unless prompt review is the requested deliverable."
)


class PluginContractTests(unittest.TestCase):
    def config(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def skill_frontmatter(self) -> dict[str, str]:
        text = SKILL_PATH.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter, _ = text[4:].split("\n---\n", 1)
        metadata = {}
        for line in frontmatter.splitlines():
            key, value = line.split(":", 1)
            metadata[key] = value.strip()
        return metadata

    def release_markdown(self) -> list[Path]:
        return [
            ROOT / "README.md",
            *sorted((ROOT / "docs").glob("*.md")),
            *sorted(SKILL_ROOT.rglob("*.md")),
        ]

    def test_package_has_no_hook_or_always_on_adapter(self) -> None:
        self.assertFalse(HOOK_PATH.exists())
        self.assertFalse(COPILOT_ADAPTER_PATH.exists())

        agent_plugin = self.config(AGENT_PLUGIN_PATH)
        codex = self.config(CODEX_MANIFEST_PATH)
        claude = self.config(CLAUDE_MANIFEST_PATH)
        self.assertNotIn("hooks", agent_plugin)
        self.assertNotIn("extensions", agent_plugin)
        self.assertNotIn("hooks", codex)
        self.assertNotIn("mcpServers", codex)
        self.assertNotIn("hooks", claude)
        self.assertNotIn("skills", claude)
        self.assertEqual(codex["skills"], "./skills/")

    def test_manifests_are_aligned_at_v080(self) -> None:
        agent_plugin = self.config(AGENT_PLUGIN_PATH)
        codex = self.config(CODEX_MANIFEST_PATH)
        claude = self.config(CLAUDE_MANIFEST_PATH)

        self.assertEqual(
            {agent_plugin["name"], codex["name"], claude["name"]},
            {"you-suck-at-prompting"},
        )
        self.assertEqual(
            {agent_plugin["version"], codex["version"], claude["version"]},
            {"0.8.0"},
        )
        for manifest in (agent_plugin, codex, claude):
            self.assertIn("select", manifest["description"].casefold())
            self.assertIn("material", manifest["description"].casefold())

        self.assertNotIn(
            "version",
            self.config(ROOT / ".agents" / "plugins" / "marketplace.json"),
        )
        self.assertNotIn(
            "version",
            self.config(ROOT / ".claude-plugin" / "marketplace.json"),
        )

    def test_skill_uses_the_exact_public_description(self) -> None:
        metadata = self.skill_frontmatter()
        self.assertEqual(set(metadata), {"name", "description"})
        self.assertEqual(metadata["name"], "you-suck-at-prompting")
        self.assertEqual(metadata["description"], EXPECTED_DESCRIPTION)

    def test_openai_metadata_keeps_native_implicit_selection(self) -> None:
        text = OPENAI_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        default = re.search(r'(?m)^\s*default_prompt:\s*"([^"]+)"\s*$', text)
        short = re.search(r'(?m)^\s*short_description:\s*"([^"]+)"\s*$', text)
        self.assertIsNotNone(default)
        self.assertIsNotNone(short)
        self.assertIn("$you-suck-at-prompting", default.group(1))
        self.assertLessEqual(len(default.group(1)), 128)
        self.assertGreaterEqual(len(short.group(1)), 25)
        self.assertLessEqual(len(short.group(1)), 64)

    def test_clear_and_false_positive_loads_pass_silently(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        behavior = (ROOT / "docs" / "behavior-and-safety.md").read_text(
            encoding="utf-8"
        )

        for text in (skill, repair, behavior):
            self.assertIn("pass", text.casefold())
            self.assertIn("silently", text.casefold())
            self.assertIn("false-positive", text.casefold())
        self.assertIn("A host may load this skill for a near miss", skill)
        self.assertIn("A normal **PASS** never does", skill)
        self.assertIn("safely discoverable", skill)

    def test_visible_five_out_of_five_is_explicit_only(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        behavior = (ROOT / "docs" / "behavior-and-safety.md").read_text(
            encoding="utf-8"
        )

        for text in (skill, repair, behavior):
            folded = text.casefold()
            self.assertIn("5/5", text)
            self.assertIn("explicit", folded)
            self.assertIn("direct invocation", folded)
        self.assertIn(
            "Only an explicit prompt audit or direct invocation may produce a visible 5/5 assessment",
            skill,
        )
        self.assertIn("Prompt unchanged:", skill)

    def test_material_repair_and_active_gate_contracts_remain(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        materiality = MATERIALITY_CONTRACT_PATH.read_text(encoding="utf-8")

        for text in (skill, repair):
            self.assertIn("You Suck At Prompting Rewritten prompt:", text)
            self.assertIn("Draft rewritten prompt:", text)
            self.assertIn("[NEEDED: ...]", text)
            self.assertIn("Prompt performance rating: N/5", text)
            self.assertIn("Reply with an acknowledgement to use this prompt.", text)
            self.assertIn("Expected prompt impact:", text)
            self.assertIn("Recommended default:", text)
            self.assertIn("executes the latest", text)
            self.assertIn("once", text)

        self.assertEqual(SKILL_PATH.read_text(encoding="utf-8").count(KICKOFF), 1)
        self.assertEqual(repair.count(KICKOFF), 1)
        self.assertEqual(
            (ROOT / "README.md").read_text(encoding="utf-8").count(KICKOFF), 1
        )
        self.assertIn("If any condition fails, do not ask", materiality)
        self.assertIn("Never treat a polished prompt as authorization", materiality)

    def test_docs_require_no_hook_trust_or_copilot_copy(self) -> None:
        install = (ROOT / "docs" / "installation.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("No hook review or trust step is required", install)
        self.assertIn("No instruction-file copy is required", install)
        self.assertIn("Upgrade note for v0.7.0 Copilot users", install)
        self.assertIn(
            ".copilot\\instructions\\you-suck-at-prompting.instructions.md",
            install,
        )
        self.assertIn(
            ".github/instructions/you-suck-at-prompting.instructions.md",
            install,
        )
        self.assertIn("There is no hook to trust", readme)
        self.assertIn("no Copilot instruction file to copy", readme)

    def test_no_stale_universal_interception_claims(self) -> None:
        stale = (
            "audit every task",
            "audit every new task",
            "intercepts every task",
            "rewrite every task",
            "applies the same 5/5 pass-through or repair gate to every",
            "mandatory performance review between",
            "for every new task request",
        )
        failures = []
        for path in self.release_markdown():
            text = path.read_text(encoding="utf-8").casefold()
            for phrase in stale:
                if phrase in text:
                    failures.append(f"{path.relative_to(ROOT)}: {phrase}")
        self.assertEqual(failures, [])

    def test_starter_prompts_are_explicit_and_bounded(self) -> None:
        prompts = self.config(CODEX_MANIFEST_PATH)["interface"]["defaultPrompt"]
        self.assertGreaterEqual(len(prompts), 1)
        self.assertLessEqual(len(prompts), 3)
        for prompt in prompts:
            self.assertIn("$you-suck-at-prompting", prompt)
            self.assertLessEqual(len(prompt), 128)

    def test_v070_clean_replacement_leaves_no_hook_or_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            root = Path(raw_tmp)
            installed = root / "installed"
            (installed / "hooks").mkdir(parents=True)
            (installed / "copilot").mkdir(parents=True)
            (installed / "hooks" / "hooks.json").write_text(
                "{}",
                encoding="utf-8",
            )
            (
                installed
                / "copilot"
                / "you-suck-at-prompting.instructions.md"
            ).write_text("v0.7.0 adapter", encoding="utf-8")

            shutil.rmtree(installed)
            shutil.copytree(PLUGIN_ROOT, installed)

            self.assertFalse((installed / "hooks" / "hooks.json").exists())
            self.assertFalse(
                (
                    installed
                    / "copilot"
                    / "you-suck-at-prompting.instructions.md"
                ).exists()
            )


if __name__ == "__main__":
    unittest.main()
