"""Offline checks for the live-eval runner. These do not call a model."""

import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".cursor" / "skills" / "ysap-live-eval" / "scripts" / "ysap_live_eval.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("ysap_live_eval", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner()


def grade_for(case: dict, *, visible: str = "pass", category=None, trace_status=None) -> dict:
    result = "fail" if visible == "fail" else "pass"
    grade = {
        "id": case["id"],
        "visible_status": visible,
        "failure_category": category,
        "disputed": False,
        "reason": "Checked against the rubric.",
        "turns": [
            {
                "expect": [{"result": result, "reason": "checked"} for _item in turn["expect"]],
                "reject": [{"result": "pass", "reason": "absent"} for _item in turn["reject"]],
            }
            for turn in case["turns"]
        ],
        "trace_status": trace_status or ("not_applicable" if "trace" not in case else "unverified"),
        "trace_note": "",
    }
    if visible == "fail" and not any(
        item["result"] == "fail"
        for turn in grade["turns"]
        for item in turn["expect"] + turn["reject"]
    ):
        grade["turns"][0]["expect"][0]["result"] = "fail"
    return grade


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = RUNNER.load_suite(ROOT)
        self.outcomes = RUNNER.load_outcomes(ROOT)

    def test_reference_change_keeps_a_control(self) -> None:
        selected = RUNNER.select_for_paths(
            ["skills/you-suck-at-prompting/references/controls/loop.md"],
            self.suite,
        )
        ids = {case["id"]: case for case in selected["cases"]}
        self.assertIn("disclosure-loop", ids)
        self.assertIn("disclosure-simple", ids)
        self.assertEqual(ids["clear-bypass"]["role"], "control")
        self.assertTrue(ids["clear-bypass"]["control"])
        self.assertNotIn("prompt-only", ids)

    def test_entrypoint_change_uses_the_boundary_sample(self) -> None:
        selected = RUNNER.select_for_paths(
            ["skills/you-suck-at-prompting/SKILL.md"],
            self.suite,
        )
        ids = [case["id"] for case in selected["cases"]]
        self.assertEqual(set(ids), set(RUNNER.REPRESENTATIVE_CASES))
        suite_order = [case["id"] for case in self.suite["cases"] if case["id"] in ids]
        self.assertEqual(ids, suite_order)
        by_id = {case["id"]: case for case in selected["cases"]}
        self.assertTrue(by_id["clear-bypass"]["control"])
        self.assertTrue(by_id["strict-json"]["control"])

    def test_docs_only_change_does_not_require_live_cases(self) -> None:
        selected = RUNNER.select_for_paths(["docs/testing.md"], self.suite)
        self.assertEqual(selected["cases"], [])
        self.assertFalse(selected["live_required"])

    def test_release_plan_covers_the_suite_and_requires_a_skip_reason(self) -> None:
        plan = RUNNER.build_plan(
            mode="release",
            paths=[],
            suite=self.suite,
            outcomes=self.outcomes,
            changed_case_ids=[],
            outcomes_changed=False,
            repetitions=None,
            skip_reason="",
            version="0.16.0",
            commit="abc",
        )
        self.assertEqual(len(plan["cases"]), 42)
        self.assertEqual(len(plan["outcome_ids"]), 5)
        self.assertEqual(plan["repetitions_planned"], 3)
        self.assertEqual(plan["repetitions_completed"], 3)
        with self.assertRaises(ValueError):
            RUNNER.build_plan(
                mode="release",
                paths=[],
                suite=self.suite,
                outcomes=self.outcomes,
                changed_case_ids=[],
                outcomes_changed=False,
                repetitions=1,
                skip_reason="",
                version="0.16.0",
                commit="abc",
            )

    def test_per_pr_mode_rejects_repeated_runs(self) -> None:
        with self.assertRaises(ValueError):
            RUNNER.build_plan(
                mode="per-pr",
                paths=["docs/testing.md"],
                suite=self.suite,
                outcomes=self.outcomes,
                changed_case_ids=[],
                outcomes_changed=False,
                repetitions=3,
                skip_reason="",
                version="0.16.0",
                commit="abc",
            )


class IsolationTests(unittest.TestCase):
    def test_prepare_keeps_rubrics_and_faults_outside_the_product_session(self) -> None:
        suite = {case["id"]: case for case in RUNNER.load_suite(ROOT)["cases"]}
        source = ROOT / "skills" / "you-suck-at-prompting"
        before = RUNNER.fingerprint(source)
        plan = {
            "schema_version": 1,
            "mode": "per-pr",
            "role": "per-pr",
            "version": "0.16.0",
            "commit": "abc",
            "live_required": True,
            "repetitions_planned": 1,
            "repetitions_completed": 1,
            "skipped": [],
            "cases": [
                {"id": "clear-bypass", "role": "control", "control": True, "reasons": ["control"]},
                {"id": "missing-reference-fallback", "role": "target", "control": False, "reasons": ["fault"]},
                {"id": "discoverable-fact", "role": "target", "control": False, "reasons": ["file"]},
            ],
            "outcome_ids": ["writing"],
            "budget": {},
        }
        with tempfile.TemporaryDirectory(prefix="ysap-eval-") as raw:
            run_dir = Path(raw) / "run"
            RUNNER.prepare_run(ROOT, run_dir, plan)
            self.assertEqual(RUNNER.fingerprint(source), before)
            index = json.loads((run_dir / "private" / "session-index.json").read_text(encoding="utf-8"))
            fallback = next(row for row in index if row["id"] == "missing-reference-fallback")
            discovered = next(row for row in index if row["id"] == "discoverable-fact")
            self.assertNotIn("missing-reference-fallback", fallback["key"])
            session = run_dir / "sessions" / fallback["key"]
            project = session / "project"
            self.assertFalse((project / "references" / "conversation-state.md").exists())
            self.assertFalse((project / ".cursor" / "skills" / "you-suck-at-prompting" / "references" / "conversation-state.md").exists())
            self.assertTrue((source / "references" / "conversation-state.md").is_file())
            prompt = (session / "turn-1-prompt.txt").read_text(encoding="utf-8")
            rubric = json.loads((run_dir / "private" / "rubrics" / "missing-reference-fallback.json").read_text(encoding="utf-8"))
            self.assertIn(suite["missing-reference-fallback"]["turns"][0]["user"], prompt)
            self.assertNotIn(suite["missing-reference-fallback"]["id"], prompt)
            self.assertNotIn(rubric["turns"][0]["expect"][0], prompt)
            self.assertFalse(any(path.name == "cases.json" for path in project.rglob("*")))
            workshop = run_dir / "sessions" / discovered["key"] / "project" / "workshop.txt"
            self.assertEqual(workshop.read_text(encoding="utf-8"), suite["discoverable-fact"]["files"]["workshop.txt"])
            self.assertFalse((run_dir / "outcomes" / "writing" / "disabled" / "project" / ".cursor").exists())
            self.assertTrue((run_dir / "outcomes" / "writing" / "enabled" / "project" / ".cursor" / "skills" / "you-suck-at-prompting" / "SKILL.md").is_file())
            with self.assertRaises(FileExistsError):
                RUNNER.prepare_run(ROOT, run_dir, plan)

    def test_run_dir_inside_the_repository_is_rejected(self) -> None:
        plan = {
            "schema_version": 1,
            "mode": "per-pr",
            "role": "per-pr",
            "version": "0.16.0",
            "commit": "abc",
            "live_required": False,
            "repetitions_planned": 1,
            "repetitions_completed": 0,
            "skipped": [],
            "cases": [],
            "outcome_ids": [],
            "budget": {},
        }
        inside = ROOT / "eval-run-should-not-exist"
        with self.assertRaises(SystemExit):
            RUNNER.prepare_run(ROOT, inside, plan)
        self.assertFalse(inside.exists())


class GradeAndRecordTests(unittest.TestCase):
    def test_claimed_trace_cannot_pass_and_results_are_append_only(self) -> None:
        suite = {case["id"]: case for case in RUNNER.load_suite(ROOT)["cases"]}
        plan = {
            "schema_version": 1,
            "mode": "release",
            "role": "release-baseline",
            "version": "0.16.0",
            "commit": "abc",
            "live_required": True,
            "repetitions_planned": 3,
            "repetitions_completed": 1,
            "skipped": [{"item": "repetitions 2-3", "reason": "budget"}],
            "cases": [
                {"id": "clear-bypass", "role": "control", "control": True, "reasons": ["sample"]},
                {"id": "disclosure-simple", "role": "target", "control": False, "reasons": ["sample"]},
            ],
            "outcome_ids": [],
            "budget": {},
            "source_fingerprint": "abc",
        }
        with tempfile.TemporaryDirectory(prefix="ysap-eval-") as raw:
            run_dir = Path(raw) / "run"
            results = Path(raw) / "public"
            RUNNER.prepare_run(ROOT, run_dir, plan)
            for case_id in ("clear-bypass", "disclosure-simple"):
                turn = RUNNER.session_dir(run_dir, case_id, 1) / "transcript-turn-1.txt"
                turn.write_text("apricot, pear, plum\n", encoding="utf-8")
            disclosure = grade_for(suite["disclosure-simple"], trace_status="verified")
            disclosure["trace_evidence"] = "claimed"
            grades = {"cases": [grade_for(suite["clear-bypass"]), disclosure], "outcomes": []}
            payload = RUNNER.assemble_results(
                ROOT,
                run_dir,
                grades,
                {"live_seconds": 12, "wall_seconds": 9, "usage": {}},
                {"name": "test host", "model": "test", "os": "linux"},
                results_root=results,
            )
            by_id = {row["id"]: row for row in payload["cases"]}
            self.assertEqual(by_id["clear-bypass"]["status"], "pass")
            self.assertEqual(by_id["disclosure-simple"]["status"], "unverified")
            self.assertEqual(by_id["disclosure-simple"]["failure_category"], "infrastructure")
            self.assertEqual(payload["usage"]["note"], "not measured")
            self.assertIsNone(payload["usage"]["input_tokens"])
            self.assertEqual(payload["summary"]["cases"]["pass"], 1)
            self.assertEqual(payload["summary"]["cases"]["unverified"], 1)
            secret = "/ho" + "me/" + "example/" + "notes"
            payload["cases"][0]["reason"] = "see " + secret
            payload = RUNNER.sanitize(payload)
            now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
            first_json, first_md = RUNNER.write_results(results, payload, now)
            original = first_json.read_bytes()
            second_json, _second_md = RUNNER.write_results(results, payload, now)
            self.assertNotEqual(first_json, second_json)
            self.assertEqual(first_json.read_bytes(), original)
            self.assertNotIn(secret, first_json.read_text(encoding="utf-8"))
            self.assertIn("[path]", first_json.read_text(encoding="utf-8"))
            self.assertIn("clear-bypass", first_md.read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                RUNNER.write_results(results, payload, now)
            dirty = dict(payload)
            dirty["cases"][0]["reason"] = secret
            with self.assertRaises(ValueError):
                RUNNER.write_results(results / "rejected", dirty, now)

    def test_pass_to_fail_is_a_blocking_regression(self) -> None:
        findings = RUNNER.blocking_findings(
            [{"id": "clear-bypass", "status": "pass"}, {"id": "strict-json", "status": "pass"}],
            [
                {"id": "clear-bypass", "status": "fail"},
                {"id": "strict-json", "status": "unverified"},
            ],
        )
        self.assertEqual(
            [(item["id"], item["kind"]) for item in findings],
            [("clear-bypass", "regression"), ("strict-json", "evidence_gap")],
        )
        self.assertTrue(all(item["blocking"] for item in findings))

    def test_previous_release_is_the_latest_older_version(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ysap-eval-") as raw:
            root = Path(raw)
            older = root / "0.15.0"
            newer = root / "0.16.0"
            older.mkdir()
            newer.mkdir()
            (older / "2026-10-01.json").write_text(json.dumps({
                "schema_version": 1,
                "role": "release-baseline",
                "version": "0.15.0",
                "generated_at": "2026-10-01T00:00:00Z",
            }), encoding="utf-8")
            (newer / "2026-10-20.json").write_text(json.dumps({
                "schema_version": 1,
                "role": "per-pr",
                "version": "0.16.0",
                "generated_at": "2026-10-20T00:00:00Z",
            }), encoding="utf-8")
            payload, path = RUNNER.find_previous_baseline(root, "0.16.0", None)
            self.assertEqual(payload["version"], "0.15.0")
            self.assertEqual(path.parent.name, "0.15.0")

    def test_outcome_packet_stays_blinded_and_exact_checks_run(self) -> None:
        outcome = next(case for case in RUNNER.load_outcomes(ROOT)["cases"] if case["id"] == "structured-extraction")
        with tempfile.TemporaryDirectory(prefix="ysap-eval-") as raw:
            run_dir = Path(raw) / "run"
            plan = {
                "schema_version": 1,
                "mode": "release",
                "role": "release-baseline",
                "version": "0.16.0",
                "commit": "abc",
                "live_required": True,
                "repetitions_planned": 3,
                "repetitions_completed": 1,
                "skipped": [{"item": "repetitions 2-3", "reason": "budget"}],
                "cases": [],
                "outcome_ids": ["structured-extraction"],
                "budget": {},
            }
            RUNNER.prepare_run(ROOT, run_dir, plan)
            private = json.loads((run_dir / "private" / "outcomes" / "structured-extraction.json").read_text(encoding="utf-8"))
            self.assertEqual(set(private["labels"].values()), {"enabled", "disabled"})
            exact = '[{"name":"Mina","seats":2},{"name":"Joel","seats":null},{"name":"Mina","seats":1}]'
            for arm in ("enabled", "disabled"):
                downstream = run_dir / "outcomes" / "structured-extraction" / f"downstream-{arm}"
                downstream.mkdir(parents=True, exist_ok=True)
                (downstream / "transcript-turn-2.txt").write_text(exact + "\n", encoding="utf-8")
            packet = RUNNER.outcome_reviewer_packet(run_dir, "structured-extraction")
            self.assertNotIn("you-suck-at-prompting", packet)
            self.assertNotIn("enabled", packet)
            self.assertNotIn("disabled", packet)
            notes = RUNNER.deterministic_outcome_notes(outcome, exact, "not json")
            self.assertTrue(notes[0]["pass"])
            self.assertFalse(notes[1]["pass"])

    def test_contained_python_check_rejects_effects(self) -> None:
        good = "def stable_unique(items):\n    result = []\n    for item in items:\n        if item not in result:\n            result.append(item)\n    return result\n"
        bad = "def stable_unique(items):\n    open('x', 'w')\n    return []\n"
        self.assertTrue(RUNNER.check_python_function("enabled", good)["pass"])
        rejected = RUNNER.check_python_function("enabled", bad)
        self.assertFalse(rejected["pass"])
        self.assertIn("not contained", rejected["value"])

    def test_dirty_worktree_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ysap-eval-") as raw:
            repo = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "file.txt").write_text("x\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                RUNNER.assert_clean(repo)


if __name__ == "__main__":
    unittest.main()
