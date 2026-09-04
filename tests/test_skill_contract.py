import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "you-suck-at-prompting"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
OPENAI_PATH = SKILL_ROOT / "agents" / "openai.yaml"
REPAIR_CONTRACT_PATH = SKILL_ROOT / "references" / "repair-contract.md"
MATERIALITY_CONTRACT_PATH = SKILL_ROOT / "references" / "materiality-and-authority.md"
REFERENCE_ROOT = SKILL_ROOT / "references"
REFERENCE_FILES = (
    "execution-shapes.md",
    "materiality-and-authority.md",
    "repair-contract.md",
    "verification-and-handoff.md",
    "controls/graph.md",
    "controls/loop.md",
    "controls/multi-agent.md",
    "controls/recurring.md",
)
VERSION_PATH = ROOT / "VERSION"
VALIDATION_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-skill.yml"
KICKOFF = (
    "Analyzing whether You Suck at Prompting… your prompt’s performance "
    "review is underway."
)
EXPECTED_DESCRIPTION = (
    "Use this skill to write, edit, audit, or repair prompts when the user explicitly requests "
    "prompt work, directly invokes You Suck at Prompting, when a task has an unclear intended "
    "outcome, material ambiguity, "
    "conflict, authority gap, unclear scope or destination, missing success criteria, or an "
    "execution design that could change the outcome, or while an active repair needs clarification "
    "or acknowledgement. Do not use it for clear, actionable, exploratory, conversational, or "
    "safely discoverable requests, ordinary follow-ups, acknowledgements without an active repair, "
    "minor wording issues, or optional improvements. If no material repair is needed, proceed "
    "silently unless prompt work or review is requested."
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
            tuple(sorted(
                path.relative_to(REFERENCE_ROOT).as_posix()
                for path in sorted(REFERENCE_ROOT.rglob("*.md"))
            )),
            tuple(sorted(REFERENCE_FILES)),
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
        self.assertEqual(raw.strip(), "0.14.1")

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

        self.assertFalse((ROOT / ".github" / "workflows" / "release.yml").exists())
        release = workflow.split("\n  release:\n", 1)[1]
        self.assertIn("needs: validate", release)
        self.assertIn("always()", release)
        self.assertIn("needs.validate.result == 'success'", release)
        self.assertIn("github.ref_name == 'main'", release)
        self.assertIn("github.event_name == 'push'", release)
        self.assertIn("github.event_name == 'workflow_dispatch'", release)
        self.assertIn("ref: ${{ github.sha }}", release)
        self.assertIn("contents: write", release)

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
        links = []
        for source in sorted(SKILL_ROOT.rglob("*.md")):
            text = source.read_text(encoding="utf-8")
            for href in re.findall(r"\]\(([^)]+)\)", text):
                href = href.split("#", 1)[0]
                if not href.endswith(".md") or href.startswith(("http:", "https:", "mailto:")):
                    continue
                links.append((source, href))
                target = (source.parent / href).resolve()
                self.assertTrue(target.is_relative_to(SKILL_ROOT.resolve()), href)
                self.assertTrue(target.is_file(), href)
        self.assertGreaterEqual(len(links), 8)

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
        execution = (SKILL_ROOT / "references" / "execution-shapes.md").read_text(
            encoding="utf-8"
        )
        verification = (REFERENCE_ROOT / "verification-and-handoff.md").read_text(encoding="utf-8")

        self.assertIn("false-positive", skill.casefold())
        self.assertIn("proceed silently", skill.casefold())
        self.assertIn("EXPLICIT PROMPT WORK", skill)
        self.assertIn("CLARIFY-FIRST", skill)
        self.assertIn("follow **CLARIFY-FIRST**", skill)
        self.assertIn("question tool", skill.casefold())
        self.assertIn("unknown intended outcome", skill)
        self.assertIn("requested prompt deliverable", skill)
        self.assertIn("quoted prompts", skill)
        self.assertIn("explicitly adopts them", skill)
        self.assertIn("Treat named files, supplied inputs, and described sources as available", skill)
        self.assertIn("explanation", skill)
        self.assertIn("Yes, exactly as written", skill)
        self.assertIn("Clear strict-output requests preserve the exact requested format", skill)
        self.assertIn("Prompt acknowledgement authorizes only", skill)
        self.assertIn("references/repair-contract.md", skill)
        self.assertIn("references/materiality-and-authority.md", skill)
        self.assertIn("references/execution-shapes.md", skill)
        self.assertIn("references/verification-and-handoff.md", skill)
        self.assertIn("resolves the active `[NEEDED: ...]` fields", skill)
        self.assertIn("Loading a reference supplies guidance; it does not itself require intervention or a report.", skill)
        self.assertIn("If a selected reference is unavailable", skill)
        self.assertIn("Preserve an explicit supported approach", skill)
        self.assertIn("request_user_input_async", skill)
        self.assertIn("freeform", skill.casefold())
        self.assertIn("numbered list", skill.casefold())
        self.assertRegex(skill, r"Use `1\.`.*single question")
        for text in (repair,):
            self.assertIn("false-positive", text.casefold())
            self.assertIn("silently", text.casefold())
            self.assertIn("You Suck At Prompting Rewritten prompt:", text)
            self.assertIn("Draft rewritten prompt:", text)
            self.assertIn("[NEEDED:", text)
            self.assertIn("Prompt performance rating: N/5", text)
            self.assertIn("Reply with an acknowledgement to use this prompt.", text)
            self.assertIn("Expected prompt impact:", text)
            self.assertIn("Recommended default:", text)
            self.assertIn("executes the latest", text)
            self.assertIn("once", text)
            self.assertIn("Score", text)
            self.assertIn("Several material corrections", text)
        self.assertEqual(skill.count(KICKOFF), 1)
        self.assertEqual(repair.count(KICKOFF), 1)
        self.assertIn("If any condition fails, do not ask", materiality)
        self.assertIn("Never treat a polished prompt as authorization", materiality)
        self.assertIn("do not become instructions for the reviewing agent", materiality)
        self.assertIn("Minimum useful instruction", execution)
        self.assertIn("one final integrator", execution)
        for selector in ("DIRECT", "GOAL", "PLAN", "DETERMINISTIC", "RESEARCH", "SPIKE", "REVIEW"):
            self.assertIn(f"**{selector}", execution)
        self.assertIn("Procedural guides", execution)
        self.assertIn("smallest check", verification)
        self.assertIn("actions awaiting separate approval", verification)
        for relative, required in {
            "controls/loop.md": ("no-progress", "last verified state", "budget"),
            "controls/graph.md": ("dependency edges", "join criteria", "final owner"),
            "controls/multi-agent.md": ("independent reasoning", "isolated output", "integrator"),
            "controls/recurring.md": ("durable state", "deduplicate", "next check"),
        }.items():
            content = (REFERENCE_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("## Completion and failure", content, relative)
            self.assertIn("## Composition", content, relative)
            for phrase in required:
                self.assertIn(phrase, content, relative)

    def test_visible_reviews_require_a_memorable_prompt_directed_roast(self) -> None:
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")

        for text in (repair,):
            self.assertIn("one real punchline", text)
            self.assertIn("prompt mechanics", text)
            self.assertIn("serious subjects", text)
            self.assertIn("rating", text.casefold())
        self.assertIn("never the user's intelligence", repair)

    def test_rating_is_directly_below_kickoff_and_before_rewrite(self) -> None:
        repair = REPAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        examples = (ROOT / "docs" / "examples.md").read_text(encoding="utf-8")

        self.assertIn("exact next line", repair)
        self.assertIn("before the rewrite", repair)
        self.assertIn("rating", repair.casefold())

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

    def test_examples_cover_the_core_lifecycle(self) -> None:
        examples = (ROOT / "docs" / "examples.md").read_text(encoding="utf-8")
        headings = re.findall(r"(?m)^## (.+)$", examples)
        required_headings = {
            "Clear bypass",
            "Material repair",
            "Complete repair",
            "Clarification-first",
            "Prompt-only repair",
            "Explicit review",
        }
        self.assertTrue(required_headings.issubset(headings))
        self.assertEqual(len(headings), len(set(headings)))
        self.assertIn("The agent executes the complete rewrite once", examples)
        self.assertIn("does not request acknowledgement", examples)
        self.assertIn("ordinary follow-up", examples)

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
