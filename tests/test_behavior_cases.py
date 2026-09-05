"""Check the public manual suite's fixtures, not live model behavior."""

import copy
import json
import re
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "behavior" / "cases.json"
REFERENCE_ROOT = ROOT / "skills" / "you-suck-at-prompting" / "references"
TAGS = {
    "activation", "control", "strict-output", "prompt-only", "execution",
    "clarification", "multi-turn", "authority", "untrusted-data",
    "progressive-disclosure", "discovery", "lifecycle", "reference-fallback",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def text_list(value: object, label: str, *, allow_empty: bool = False) -> None:
    require(isinstance(value, list), f"{label} must be a list")
    require(bool(value) or allow_empty, f"{label} must not be empty")
    require(all(isinstance(item, str) and item.strip() for item in value),
            f"{label} must contain nonempty strings")
    require(len(value) == len(set(value)), f"{label} must not contain duplicates")


def validate_suite(suite: object) -> None:
    require(isinstance(suite, dict), "suite must be an object")
    require(set(suite) == {"schema_version", "cases"}, "unexpected suite fields")
    require(type(suite["schema_version"]) is int and suite["schema_version"] == 1,
            "unsupported schema_version")
    cases = suite["cases"]
    require(isinstance(cases, list) and bool(cases), "cases must be a nonempty list")
    seen = set()
    for case in cases:
        require(isinstance(case, dict), "case must be an object")
        required = {"id", "title", "tags", "turns"}
        require(required <= set(case) <= required | {"trace", "files", "unavailable_references"},
                "unexpected case fields")
        if "files" in case:
            require(isinstance(case["files"], dict) and bool(case["files"]), "files must be a nonempty object")
            for name, content in case["files"].items():
                require(isinstance(name, str) and bool(re.fullmatch(r"[a-z][a-z0-9-]*\.txt", name)),
                        "fixture files must be plain local text filenames")
                require(isinstance(content, str) and bool(content), "fixture content must be nonempty text")
        if "unavailable_references" in case:
            text_list(case["unavailable_references"], "unavailable_references")
            for name in case["unavailable_references"]:
                require(name in {p.relative_to(REFERENCE_ROOT).as_posix() for p in REFERENCE_ROOT.rglob("*.md")},
                        "unavailable reference must name a shipped reference")
        case_id = case["id"]
        require(isinstance(case_id, str) and bool(re.fullmatch(r"[a-z][a-z0-9-]*", case_id)),
                "case id must be a lowercase slug")
        require(case_id not in seen, f"duplicate case id: {case_id}")
        seen.add(case_id)
        require(isinstance(case["title"], str) and bool(case["title"].strip()),
                f"{case_id}: title must be nonempty")
        text_list(case["tags"], f"{case_id}: tags")
        require(set(case["tags"]) <= TAGS, f"{case_id}: unknown tag")
        require(("files" in case) == ("discovery" in case["tags"]), "discovery requires files")
        require(("unavailable_references" in case) == ("reference-fallback" in case["tags"]),
                "fallback requires a declared missing reference")
        turns = case["turns"]
        require(isinstance(turns, list) and bool(turns), f"{case_id}: turns must be nonempty")
        require((len(turns) > 1) == ("multi-turn" in case["tags"]),
                f"{case_id}: multi-turn tag must match the conversation")
        for turn in turns:
            require(isinstance(turn, dict) and set(turn) == {"user", "expect", "reject"},
                    f"{case_id}: each turn needs user, expect and reject")
            require(isinstance(turn["user"], str) and bool(turn["user"].strip()),
                    f"{case_id}: user text must be nonempty")
            text_list(turn["expect"], f"{case_id}: expect")
            text_list(turn["reject"], f"{case_id}: reject")
        require(("trace" in case) == ("progressive-disclosure" in case["tags"]),
                f"{case_id}: disclosure cases need a trace rubric")
        if "trace" in case:
            trace = case["trace"]
            require(isinstance(trace, dict) and set(trace) == {"required", "unnecessary"},
                    f"{case_id}: invalid trace fields")
            for field in ("required", "unnecessary"):
                text_list(trace[field], f"{case_id}: trace {field}")
                for relative in trace[field]:
                    path = PurePosixPath(relative)
                    require(not path.is_absolute() and ".." not in path.parts
                            and "\\" not in relative and ":" not in relative
                            and path.suffix == ".md", f"{case_id}: invalid reference path")
                    target = (REFERENCE_ROOT / path).resolve()
                    require(target.is_relative_to(REFERENCE_ROOT.resolve()) and target.is_file(),
                            f"{case_id}: reference is missing or outside runtime")
            require(not set(trace["required"]) & set(trace["unnecessary"]),
                    f"{case_id}: conflicting trace requirements")


class BehaviorFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_public_suite_is_valid(self) -> None:
        validate_suite(self.suite)

    def test_outcome_comparison_has_complete_synthetic_inputs(self) -> None:
        comparison = json.loads(CASES_PATH.with_name("outcomes.json").read_text(encoding="utf-8"))
        self.assertEqual(set(comparison), {"schema_version", "cases"})
        self.assertEqual(comparison["schema_version"], 1)
        expected = {"writing", "summarization", "structured-extraction",
                    "coding-instructions", "advanced-execution"}
        self.assertEqual({case["id"] for case in comparison["cases"]}, expected)
        self.assertEqual(len(comparison["cases"]), len(expected))
        for case in comparison["cases"]:
            self.assertEqual(set(case), {"id", "request", "downstream_input", "criteria"})
            self.assertTrue(case["request"].strip())
            self.assertTrue(case["downstream_input"].strip())
            text_list(case["criteria"], case["id"])

    def test_suite_covers_the_declared_boundaries(self) -> None:
        covered = {tag for case in self.suite["cases"] for tag in case["tags"]}
        self.assertEqual(covered, TAGS)

    def test_invalid_shapes_are_rejected(self) -> None:
        invalid = [None, {}, {"schema_version": True, "cases": []},
                   {"schema_version": 2, "cases": []},
                   {"schema_version": 1, "cases": []}]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_suite(value)

    def test_malformed_cases_are_rejected(self) -> None:
        mutations = [
            lambda case: case.update(id="Not a slug"),
            lambda case: case.update(title=" "),
            lambda case: case.update(tags=["unknown"]),
            lambda case: case.update(tags=None),
            lambda case: case.update(tags=["control", "control"]),
            lambda case: case.update(turns=[]),
            lambda case: case.update(turns=["not an object"]),
            lambda case: case["turns"][0].update(user=""),
            lambda case: case["turns"][0].update(expect=[]),
            lambda case: case["turns"][0].update(reject="not a list"),
            lambda case: case["turns"][0].update(expect=[42]),
            lambda case: case["turns"][0].update(answer="unexpected field"),
            lambda case: case["tags"].append("multi-turn"),
            lambda case: case["tags"].append("progressive-disclosure"),
        ]
        for index, mutate in enumerate(mutations):
            suite = copy.deepcopy(self.suite)
            mutate(suite["cases"][0])
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_suite(suite)

    def test_duplicate_ids_are_rejected(self) -> None:
        self.suite["cases"].append(copy.deepcopy(self.suite["cases"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate case id"):
            validate_suite(self.suite)

    def test_invalid_reference_traces_are_rejected(self) -> None:
        for relative in ("../SKILL.md", "/repair-contract.md", "missing.md",
                         "controls\\loop.md", "repair-contract.txt"):
            suite = copy.deepcopy(self.suite)
            case = next(case for case in suite["cases"] if "trace" in case)
            case["trace"]["required"] = [relative]
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                validate_suite(suite)

    def test_conflicting_reference_traces_are_rejected(self) -> None:
        case = next(case for case in self.suite["cases"] if "trace" in case)
        case["trace"]["unnecessary"].append(case["trace"]["required"][0])
        with self.assertRaisesRegex(ValueError, "conflicting trace"):
            validate_suite(self.suite)

    def test_unsafe_or_invalid_setup_is_rejected(self) -> None:
        for name in ("../workshop.txt", "/workshop.txt", "AGENTS.md", "run.ps1"):
            suite = copy.deepcopy(self.suite)
            case = next(c for c in suite["cases"] if "files" in c)
            case["files"] = {name: "synthetic"}
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_suite(suite)
        for name in ("../SKILL.md", "unknown.md"):
            suite = copy.deepcopy(self.suite)
            case = next(c for c in suite["cases"] if "unavailable_references" in c)
            case["unavailable_references"] = [name]
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_suite(suite)


if __name__ == "__main__":
    unittest.main()
