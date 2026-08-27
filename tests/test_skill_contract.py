import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "you-suck-at-prompting"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
OPENAI_PATH = SKILL_ROOT / "agents" / "openai.yaml"
REPAIR_CONTRACT_PATH = SKILL_ROOT / "references" / "repair-contract.md"
MATERIALITY_CONTRACT_PATH = SKILL_ROOT / "references" / "materiality-and-authority.md"
PROGRAMMING_GIT_CONTRACT_PATH = SKILL_ROOT / "references" / "programming-and-git-isolation.md"
VERSION_PATH = ROOT / "VERSION"
VALIDATION_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-skill.yml"
KICKOFF = (
    "Analyzing whether You Suck at Prompting… your prompt’s performance "
    "review is underway."
)
EXPECTED_DESCRIPTION = (
    "Use this skill to audit or repair prompts when the user explicitly asks to write, "
    "rewrite, critique, clarify, or quality-check a prompt, directly invokes You Suck at "
    "Prompting, or when a task request has a material problem such as ambiguity, conflicting "
    "constraints, missing authority, unclear scope or destination, missing success criteria, "
    "or an execution design that could change the outcome, or a programming mutation that lacks "
    "safe Git isolation. Also inspect programming requests that may create or change "
    "repository-tracked files to decide whether a dedicated branch in the current checkout or "
    "a branch-backed linked worktree is appropriate. Do not use it for clear non-programming "
    "requests, exploratory or conversational work, read-only programming, non-Git directories, "
    "simple follow-ups or acknowledgements, minor wording issues, or optional improvements. If "
    "no material repair or Git isolation change is needed, proceed silently unless prompt review "
    "is the requested deliverable."
)


class SkillPackageContractTests(unittest.TestCase):
    def skill_frontmatter(self) -> dict[str, str]:
        text = SKILL_PATH.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter, _ = text[4:].split("\n---\n", 1)
        metadata: dict[str, str] = {}
        for line in frontmatter.splitlines():
            key, value = line.split(":", 1)
            metadata[key] = value.strip()
        return metadata

    def release_files(self) -> list[Path]:
        return sorted(
            path
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts
        )

    def release_markdown(self) -> list[Path]:
        return [
            ROOT / "README.md",
            *sorted((ROOT / "docs").glob("*.md")),
            *sorted(SKILL_ROOT.rglob("*.md")),
        ]

    def test_repository_contains_exactly_one_root_skill(self) -> None:
        discovered = sorted(
            path.parent.relative_to(ROOT).as_posix()
            for path in (ROOT / "skills").glob("*/SKILL.md")
        )
        self.assertEqual(discovered, ["skills/you-suck-at-prompting"])
        self.assertTrue(OPENAI_PATH.is_file())
        self.assertEqual(
            sorted(path.name for path in (SKILL_ROOT / "references").glob("*.md")),
            [
                "execution-shapes.md",
                "materiality-and-authority.md",
                "programming-and-git-isolation.md",
                "repair-contract.md",
            ],
        )

    def test_repository_has_no_native_package_or_private_artifacts(self) -> None:
        allowed_root = {
            ".github",
            "docs",
            "skills",
            "tests",
            "LICENSE",
            "README.md",
            "VERSION",
        }
        unexpected = sorted(
            path.name
            for path in ROOT.iterdir()
            if path.name != ".git" and path.name not in allowed_root
        )
        self.assertEqual(unexpected, [])

        for forbidden in (
            ROOT / ".agents",
            ROOT / ".claude-plugin",
            ROOT / "plugins",
            ROOT / "package.json",
            ROOT / "skills.sh.json",
        ):
            self.assertFalse(forbidden.exists(), str(forbidden.relative_to(ROOT)))

        private_parts = {
            "evals",
            "eval-workbench",
            "dashboard",
            "results",
            "candidates",
            "state",
            "source-cache",
            "__pycache__",
        }
        leaked = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if ".git" not in path.parts
            and any(part.casefold() in private_parts for part in path.parts)
        ]
        self.assertEqual(leaked, [])

    def test_version_is_one_strict_semver(self) -> None:
        raw = VERSION_PATH.read_text(encoding="utf-8")
        self.assertRegex(raw, r"^\d+\.\d+\.\d+\n?$")
        self.assertGreaterEqual(tuple(map(int, raw.strip().split("."))), (0, 9, 0))

    def test_validation_workflow_keeps_the_protected_validate_context(self) -> None:
        workflow = VALIDATION_WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertRegex(workflow, r"(?m)^  validate:\s*$")
        self.assertRegex(workflow, r"(?m)^    name: validate\s*$")
        for dependency in (
            "offline-contract",
            "version-policy",
            "pinned-installer",
            "latest-discovery",
        ):
            self.assertIn(f"      - {dependency}\n", workflow)
        self.assertIn('"references/programming-and-git-isolation.md"', workflow)

    def test_skill_uses_the_exact_selective_description(self) -> None:
        metadata = self.skill_frontmatter()
        self.assertEqual(
            metadata,
            {
                "name": "you-suck-at-prompting",
                "description": EXPECTED_DESCRIPTION,
            },
        )

    def test_all_skill_references_resolve_inside_the_skill(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")
        references = re.findall(r"\((references/[^)]+\.md)\)", text)
        self.assertGreaterEqual(len(references), 3)
        for reference in references:
            target = (SKILL_ROOT / reference).resolve()
            self.assertTrue(target.is_relative_to(SKILL_ROOT.resolve()))
            self.assertTrue(target.is_file(), reference)

    def test_openai_metadata_keeps_implicit_selection(self) -> None:
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

    def test_selective_behavior_contract_is_preserved(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        materiality = MATERIALITY_CONTRACT_PATH.read_text(encoding="utf-8")

        for text in (skill, repair):
            self.assertIn("false-positive", text.casefold())
            self.assertIn("silently", text.casefold())
            self.assertIn("You Suck At Prompting Rewritten prompt:", text)
            self.assertIn("Draft rewritten prompt:", text)
            self.assertIn("[NEEDED: ...]", text)
            self.assertIn("Prompt performance rating: N/5", text)
            self.assertIn("Reply with an acknowledgement to use this prompt.", text)
            self.assertIn("Expected prompt impact:", text)
            self.assertIn("Recommended default:", text)
            self.assertIn("executes the latest", text)
            self.assertIn("once", text)
        self.assertIn("A normal **PASS** never does", skill)
        self.assertIn("Only an explicit prompt audit or direct invocation", skill)
        self.assertIn("Prompt unchanged:", skill)
        self.assertEqual(skill.count(KICKOFF), 1)
        self.assertEqual(repair.count(KICKOFF), 1)
        self.assertIn("If any condition fails, do not ask", materiality)
        self.assertIn("Never treat a polished prompt as authorization", materiality)

    def test_programming_git_isolation_contract_is_conditional_and_safe(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        git_contract = PROGRAMMING_GIT_CONTRACT_PATH.read_text(encoding="utf-8")

        self.assertIn("Treat programming as a context, not a blanket trigger", skill)
        self.assertIn("A tracked mutation on an unisolated, unsafe, or unknown checkout", skill)
        self.assertIn(
            "Read [references/programming-and-git-isolation.md]",
            skill,
        )
        self.assertIn("branch or worktree creation is deferred until acknowledgement", skill)
        self.assertIn("programming request that may create or change Git-tracked files", repair)
        for phrase in (
            "dedicated task branch in the current checkout",
            "dedicated branch-backed linked worktree",
            "dirty-file ownership",
            "Do not initialize Git",
            "Never open `.env` files",
            "bare coordinator",
            "high risk",
        ):
            self.assertIn(phrase, git_contract)

    def test_visible_reviews_require_a_memorable_prompt_directed_roast(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")

        for text in (skill, repair):
            self.assertIn("one real punchline", text)
            self.assertIn("Make it sting for half a second", text)
            self.assertIn("Slightly brutal means candid plus funny, not cruel", text)
            self.assertIn("serious or sensitive", text)
            self.assertIn("rating comment carries the joke", text.casefold())
        self.assertIn("Prompting Performance Improvement Plan", skill)
        self.assertIn("lint messages wearing fake mustaches", skill)
        self.assertIn("never the user's intelligence", repair)

    def test_rating_is_directly_below_kickoff_and_before_rewrite(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        examples = (ROOT / "docs" / "examples.md").read_text(encoding="utf-8")

        for text in (skill, repair):
            self.assertIn("rating immediately below the kickoff", text)
            self.assertIn("before the rewrite or draft heading", text)
            self.assertIn("Never place it beneath the rewritten prompt", text)

        material_example = examples.split("## Material repair", 1)[1].split(
            "## Explicit review", 1
        )[0]
        kickoff_index = material_example.index(KICKOFF)
        rating_index = material_example.index("Prompt performance rating:")
        heading_index = material_example.index("Draft rewritten prompt:")
        self.assertLess(kickoff_index, rating_index)
        self.assertLess(rating_index, heading_index)
        self.assertIn(f"{KICKOFF}\nPrompt performance rating:", material_example)

    def test_readme_is_short_and_installation_is_above_the_example(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        words = re.findall(r"\b[\w’'-]+\b", readme)
        self.assertLessEqual(len(words), 850)
        self.assertLess(readme.index("## Install"), readme.index("## Exhibit A"))
        for command in (
            "npx skills@latest add ScotTFO/you-suck-at-prompting",
            "npx skills@latest add ScotTFO/you-suck-at-prompting --global",
        ):
            self.assertIn(command, readme)

    def test_installation_is_the_complete_lifecycle_contract(self) -> None:
        install = (ROOT / "docs" / "installation.md").read_text(encoding="utf-8")
        version = VERSION_PATH.read_text(encoding="utf-8").strip()
        required = (
            "Node.js 22.20",
            "--agent codex claude-code github-copilot hermes-agent",
            "--agent '*'",
            "--copy",
            f"tree/v{version}",
            "update you-suck-at-prompting --project",
            "update you-suck-at-prompting --global",
            "remove you-suck-at-prompting --yes",
            "remove you-suck-at-prompting --global",
            "codex plugin remove you-suck-at-prompting@scottfo",
            "claude plugin uninstall you-suck-at-prompting@scottfo",
            "@agentPlugins",
            ".copilot/instructions/you-suck-at-prompting.instructions.md",
            "DISABLE_TELEMETRY",
            "DO_NOT_TRACK",
        )
        for claim in required:
            self.assertIn(claim, install)

    def test_examples_cover_the_isolation_behavior(self) -> None:
        examples = (ROOT / "docs" / "examples.md").read_text(encoding="utf-8")
        headings = re.findall(r"(?m)^## (.+)$", examples)
        self.assertEqual(headings, ["Clear bypass", "Material repair", "Programming isolation", "Explicit review"])

    def test_runtime_and_installer_telemetry_are_not_conflated(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        behavior = (ROOT / "docs" / "behavior-and-safety.md").read_text(
            encoding="utf-8"
        )
        for text in (readme, behavior):
            self.assertIn("runtime", text.casefold())
            self.assertIn("no telemetry", text.casefold())
            self.assertIn("external `skills` installer", text)

    def test_no_stale_native_install_commands_or_universal_claims(self) -> None:
        stale = (
            "codex plugin marketplace add",
            "codex plugin add you-suck-at-prompting",
            "claude plugin marketplace add",
            "claude plugin install you-suck-at-prompting",
            "plugins/you-suck-at-prompting/skills/you-suck-at-prompting",
            "audit every task",
            "audit every new task",
            "intercepts every task",
            "rewrite every task",
            "for every new task request",
            "mandatory performance review between",
        )
        failures = []
        for path in self.release_markdown():
            text = path.read_text(encoding="utf-8").casefold()
            for phrase in stale:
                if phrase in text:
                    failures.append(f"{path.relative_to(ROOT)}: {phrase}")
        self.assertEqual(failures, [])

    def test_release_files_have_no_secret_or_private_path_patterns(self) -> None:
        patterns = (
            r"gh[pousr]_[A-Za-z0-9_]{20,}",
            r"sk-[A-Za-z0-9_-]{20,}",
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
            r"[A-Za-z]:\\",
            r"C:/Users/",
            r"/Users/[^/]+/",
            r"/home/[^/]+/",
        )
        hits = []
        for path in self.release_files():
            if path.resolve() == Path(__file__).resolve():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if any(re.search(pattern, text) for pattern in patterns):
                hits.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
