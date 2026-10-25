#!/usr/bin/env python3
"""Prepare, grade, and record You Suck at Prompting live-model evals.

The product skill is not modified. This runner copies it into an isolated
session directory, writes append-only public results, and keeps transcripts
outside the repository.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = 1
FAILURE_CATEGORIES = (
    "product behavior",
    "evaluator defect",
    "infrastructure",
    "presentation",
)
CASE_STATUSES = ("pass", "fail", "unverified", "blocked", "not_run")
RELEASE_REPETITIONS = 3
LIVE_SECONDS_LIMIT = 60 * 60
REPAIR_CYCLE_LIMIT = 2
CONTROL_IDS = ("clear-bypass", "strict-json")
RUNTIME_PREFIX = "skills/you-suck-at-prompting/"

# One focused case per testing.md boundary. Per-PR entrypoint edits use this
# sample. Release mode runs every case instead.
REPRESENTATIVE_CASES = (
    "clear-bypass",
    "strict-json",
    "prompt-only",
    "ordinary-unknown-goal",
    "discoverable-fact",
    "quoted-instructions",
    "approval-lifecycle",
    "disclosure-simple",
    "missing-reference-fallback",
    "method-alternative-accept",
    "method-firm-constraint",
    "method-tentative-open",
    "method-unclear-outcome",
    "research-local-evidence",
)

BOUNDARIES = (
    ("Silent activation and exact output", ("clear-bypass", "strict-json")),
    ("Prompt deliverable and execution", ("prompt-only", "prompt-only-output-only", "prompt-and-execute")),
    ("Unknown goal and clarification", ("ordinary-unknown-goal", "unknown-goal-continuation", "execution-clarification")),
    ("Facts and conflicting requirements", ("discoverable-fact", "conflicting-requirements")),
    ("Source instructions and authority", ("quoted-instructions", "missing-authority")),
    ("Approval lifecycle", ("approval-lifecycle", "cancelled-approval", "replacement-late-answer", "stale-proposal-approval")),
    ("Selective reference loading", ("disclosure-simple", "disclosure-independent-review", "disclosure-loop", "disclosure-graph", "disclosure-recurring")),
    ("Entry-point fallback", ("missing-reference-fallback",)),
    ("Method agreement", ("method-alternative-accept", "method-alternative-reject", "method-alternative-revision")),
    ("Firm and unresolved methods", ("method-firm-constraint", "method-ambiguous-constraint")),
    ("Open, delegated, and technical methods", ("method-tentative-open", "method-delegated-choice", "method-technical-direct")),
    ("Outcome clarity and evidence", ("method-unclear-outcome", "prompt-rewrite-sufficient-evidence", "prompt-rewrite-current-evidence")),
    ("Research before action", (
        "research-local-evidence",
        "research-changing-facts",
        "research-settled-followup",
        "research-diagnosis-no-method",
        "research-mechanical-bypass",
        "research-unknown-goal",
        "research-strict-output",
        "research-firm-method",
        "research-source-conflict",
    )),
)

# Cases that depend on a reference even when they have no trace rubric.
REFERENCE_CASES = {
    "conversation-state.md": (
        "unknown-goal-continuation",
        "execution-clarification",
        "ordinary-unknown-goal",
        "approval-lifecycle",
        "cancelled-approval",
        "replacement-late-answer",
        "stale-proposal-approval",
        "method-alternative-accept",
        "method-alternative-reject",
        "method-alternative-revision",
        "method-ambiguous-constraint",
        "missing-reference-fallback",
        "conflicting-requirements",
        "research-settled-followup",
        "research-firm-method",
        "research-source-conflict",
        "research-unknown-goal",
    ),
    "repair-contract.md": (
        "prompt-only",
        "prompt-only-output-only",
        "quoted-instructions",
        "disclosure-simple",
        "disclosure-independent-review",
        "disclosure-loop",
        "disclosure-graph",
        "disclosure-recurring",
        "prompt-rewrite-sufficient-evidence",
        "prompt-rewrite-current-evidence",
    ),
    "materiality-and-authority.md": (
        "missing-authority",
        "conflicting-requirements",
        "method-firm-constraint",
        "method-ambiguous-constraint",
        "method-alternative-accept",
        "method-alternative-reject",
        "method-alternative-revision",
        "quoted-instructions",
    ),
    "research-before-action.md": (
        "research-local-evidence",
        "research-changing-facts",
        "research-settled-followup",
        "research-diagnosis-no-method",
        "research-mechanical-bypass",
        "research-unknown-goal",
        "research-strict-output",
        "research-firm-method",
        "research-source-conflict",
        "method-unclear-outcome",
        "prompt-rewrite-sufficient-evidence",
        "prompt-rewrite-current-evidence",
        "discoverable-fact",
    ),
    "execution-shapes.md": (
        "disclosure-simple",
        "disclosure-independent-review",
        "disclosure-loop",
        "disclosure-graph",
        "disclosure-recurring",
    ),
    "verification-and-handoff.md": (
        "disclosure-independent-review",
        "disclosure-simple",
    ),
    "controls/graph.md": ("disclosure-graph", "disclosure-simple"),
    "controls/loop.md": ("disclosure-loop", "disclosure-simple"),
    "controls/multi-agent.md": ("disclosure-independent-review", "disclosure-simple"),
    "controls/recurring.md": ("disclosure-recurring", "disclosure-simple"),
}

def _private_path_pattern() -> re.Pattern[str]:
    # Keep the pieces split so the package path scan does not flag this detector.
    home = "/ho" + "me/"
    users = "/Us" + "ers/"
    windows_users = "C:/" + "Users/"
    drive = "[A-Za-z]:" + "\\"
    tail = "[^\\s\"'\\\\]+"
    return re.compile(home + tail + "|" + windows_users + tail + "|" + users + tail + "|" + drive + tail)


PRIVATE_PATH = _private_path_pattern()
WORD = re.compile(r"\b[\w’'-]+\b")


def default_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def suite_paths(root: Path) -> tuple[Path, Path, Path]:
    behavior = root / "tests" / "behavior"
    return (
        behavior / "cases.json",
        behavior / "outcomes.json",
        root / "skills" / "you-suck-at-prompting",
    )


def load_suite(root: Path) -> dict:
    cases, _, _ = suite_paths(root)
    return load_json(cases)


def load_outcomes(root: Path) -> dict:
    _, outcomes, _ = suite_paths(root)
    return load_json(outcomes)


def read_version(root: Path) -> str:
    raw = (root / "VERSION").read_text(encoding="utf-8")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+\n?", raw):
        raise ValueError("VERSION must contain one strict stable semver")
    return raw.strip()


def skill_description(skill_root: Path) -> str:
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("skill frontmatter missing")
    front, _ = text[4:].split("\n---\n", 1)
    for line in front.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("skill description missing")


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def boundary_for(case_id: str) -> str:
    for name, ids in BOUNDARIES:
        if case_id in ids:
            return name
    return "Other"


def case_index(suite: dict) -> dict[str, dict]:
    return {case["id"]: case for case in suite["cases"]}


def cases_for_reference(suite: dict, reference: str) -> list[str]:
    found = set(REFERENCE_CASES.get(reference, ()))
    for case in suite["cases"]:
        trace = case.get("trace") or {}
        names = list(trace.get("required", [])) + list(trace.get("unnecessary", []))
        if reference in names or reference in case.get("unavailable_references", []):
            found.add(case["id"])
    order = [case["id"] for case in suite["cases"]]
    return [case_id for case_id in order if case_id in found]


def _add(selected: dict[str, dict], case_id: str, reason: str, *, role: str) -> None:
    entry = selected.get(case_id)
    if entry is None:
        selected[case_id] = {"id": case_id, "role": role, "control": False, "reasons": [reason]}
        return
    if reason not in entry["reasons"]:
        entry["reasons"].append(reason)
    if role == "target":
        entry["role"] = "target"


def select_for_paths(
    paths: list[str],
    suite: dict,
    *,
    changed_case_ids: list[str] | None = None,
    outcomes_changed: bool = False,
) -> dict:
    """Return per-PR targets. An empty case list means live behavior is not required."""
    known = case_index(suite)
    selected: dict[str, dict] = {}
    for path in paths:
        if path in {"tests/behavior/outcomes.json", "docs/outcome-comparison.md"}:
            outcomes_changed = True
        if path == "tests/behavior/cases.json":
            for case_id in changed_case_ids or []:
                if case_id not in known:
                    raise ValueError(f"changed case is not in the suite: {case_id}")
                _add(selected, case_id, "behavior fixture changed", role="target")
        if not path.startswith(RUNTIME_PREFIX):
            continue
        relative = path[len(RUNTIME_PREFIX):]
        if relative in {"SKILL.md", "agents/openai.yaml"}:
            for case_id in REPRESENTATIVE_CASES:
                _add(selected, case_id, f"entrypoint sample for {relative}", role="target")
        elif relative.startswith("references/"):
            reference = relative[len("references/"):]
            matched = cases_for_reference(suite, reference)
            if not matched:
                raise ValueError(f"no behavior case covers reference {reference}")
            for case_id in matched:
                _add(selected, case_id, f"covers {reference}", role="target")
    if selected:
        bypass = selected.get("clear-bypass")
        if bypass is None:
            _add(selected, "clear-bypass", "unchanged silent-activation control", role="control")
        elif bypass["role"] == "target":
            bypass["control"] = True
            if "strict-json" not in selected:
                _add(
                    selected,
                    "strict-json",
                    "unchanged exact-output control",
                    role="control",
                )
            selected["strict-json"]["control"] = True
        selected["clear-bypass"]["control"] = True
    order = [case["id"] for case in suite["cases"]]
    cases = [selected[case_id] for case_id in order if case_id in selected]
    return {
        "live_required": bool(cases),
        "cases": cases,
        "outcomes_changed": outcomes_changed,
    }


def ordered_cases(selection: dict, suite: dict) -> list[dict]:
    return selection["cases"]


def build_plan(
    *,
    mode: str,
    paths: list[str],
    suite: dict,
    outcomes: dict,
    changed_case_ids: list[str] | None,
    outcomes_changed: bool,
    repetitions: int | None,
    skip_reason: str,
    version: str,
    commit: str,
) -> dict:
    if mode not in {"per-pr", "release"}:
        raise ValueError("mode must be per-pr or release")
    skipped: list[dict] = []
    if mode == "release":
        planned = RELEASE_REPETITIONS
        reps = RELEASE_REPETITIONS if repetitions is None else repetitions
        if reps < 1 or reps > planned:
            raise ValueError("release repetitions must be from 1 through 3")
        if reps != planned and not skip_reason.strip():
            raise ValueError("skipping release repetitions requires a skip reason")
        if reps != planned:
            skipped.append({
                "item": f"repetitions {reps + 1}-{planned}",
                "reason": skip_reason.strip(),
            })
        cases = [
            {
                "id": case["id"],
                "role": "target",
                "control": case["id"] in CONTROL_IDS,
                "reasons": ["full release suite"],
            }
            for case in suite["cases"]
        ]
        outcome_ids = [case["id"] for case in outcomes["cases"]]
        live_required = True
    else:
        planned = 1
        reps = 1 if repetitions is None else repetitions
        if reps != 1:
            raise ValueError("per-PR mode uses one fresh run per selected case")
        chosen = select_for_paths(
            paths,
            suite,
            changed_case_ids=changed_case_ids,
            outcomes_changed=outcomes_changed,
        )
        cases = chosen["cases"]
        outcome_ids = [case["id"] for case in outcomes["cases"]] if chosen["outcomes_changed"] else []
        live_required = chosen["live_required"] or bool(outcome_ids)
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "role": "release-baseline" if mode == "release" else "per-pr",
        "version": version,
        "commit": commit,
        "live_required": live_required,
        "repetitions_planned": planned,
        "repetitions_completed": reps if live_required else 0,
        "skipped": skipped,
        "cases": cases,
        "outcome_ids": outcome_ids,
        "budget": {
            "repair_cycle_limit": REPAIR_CYCLE_LIMIT,
            "live_seconds_limit": LIVE_SECONDS_LIMIT,
        },
    }


def git_output(root: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=check,
    )


def assert_clean(root: Path) -> None:
    status = git_output(root, ["status", "--porcelain"])
    if status.stdout.strip():
        raise SystemExit("candidate worktree is dirty; commit before a live run")


def head_commit(root: Path) -> str:
    return git_output(root, ["rev-parse", "HEAD"]).stdout.strip()


def changed_paths(root: Path, base: str) -> list[str]:
    probe = git_output(root, ["rev-parse", "--verify", "--quiet", base], check=False)
    if probe.returncode != 0:
        raise SystemExit(f"base revision is not available: {base}")
    diff = git_output(root, ["diff", "--name-only", f"{base}...HEAD"])
    return [line for line in diff.stdout.splitlines() if line]


def changed_case_ids(root: Path, base: str) -> list[str]:
    shown = git_output(root, ["show", f"{base}:tests/behavior/cases.json"], check=False)
    current = load_suite(root)
    if shown.returncode != 0:
        return [case["id"] for case in current["cases"]]
    previous = json.loads(shown.stdout)
    old = {case["id"]: case for case in previous["cases"]}
    new = {case["id"]: case for case in current["cases"]}
    changed = [case_id for case_id, case in new.items() if old.get(case_id) != case]
    changed.extend(case_id for case_id in old if case_id not in new)
    return changed


def outcomes_file_changed(root: Path, base: str) -> bool:
    shown = git_output(root, ["show", f"{base}:tests/behavior/outcomes.json"], check=False)
    if shown.returncode != 0:
        return True
    return json.loads(shown.stdout) != load_outcomes(root)


def host_preamble(project: Path, description: str) -> str:
    skill_file = project / ".cursor" / "skills" / "you-suck-at-prompting" / "SKILL.md"
    return (
        "You are answering one user in an isolated project.\n"
        f"Project root: {project}\n\n"
        "The only installed skill is you-suck-at-prompting.\n"
        f"Description: {description}\n"
        f"Skill file: {skill_file}\n"
        "Read that file only if you decide the description applies. "
        "If you read it, follow it, including references it tells you to read inside this project. "
        "Do not announce whether you loaded it.\n\n"
        "Do not read, search, list, or write outside the project root. "
        "No question tool is available. If a skill you loaded requires one, use its fallback for when no question tool succeeds. "
        "Do not create files unless the user asked for a file change.\n\n"
        "Reply to the user message only.\n\n"
        "User:\n"
    )


def disabled_preamble(project: Path) -> str:
    return (
        "You are answering one user in an isolated project.\n"
        f"Project root: {project}\n\n"
        "No project skills are installed. Do not read, search, list, or write outside the project root. "
        "Do not create files unless the user asked for a file change.\n\n"
        "Reply to the user message only.\n\n"
        "User:\n"
    )


def assert_outside_repo(root: Path, run_dir: Path) -> None:
    resolved_root = root.resolve()
    resolved_run = run_dir.resolve()
    if resolved_run == resolved_root or resolved_root in resolved_run.parents:
        raise SystemExit("run-dir must stay outside the repository so transcripts stay private")


def copy_skill(source: Path, project: Path, unavailable: list[str]) -> dict:
    destination = project / ".cursor" / "skills" / "you-suck-at-prompting"
    destination.parent.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    omitted = []
    for relative in unavailable:
        target = destination / "references" / relative
        if not target.is_file():
            raise ValueError(f"declared missing reference is not in the candidate: {relative}")
        target.unlink()
        omitted.append(relative)
    return {
        "source_fingerprint": fingerprint(source),
        "session_fingerprint": fingerprint(destination),
        "omitted_references": omitted,
    }


def prepare_case_session(
    root: Path,
    run_dir: Path,
    case: dict,
    repetition: int,
    description: str,
    session_key: str,
) -> dict:
    source = suite_paths(root)[2]
    # The directory name is opaque so the product prompt does not reveal the case id.
    session = run_dir / "sessions" / session_key
    project = session / "project"
    if project.exists():
        raise FileExistsError(f"session already exists: {session}")
    identity = copy_skill(source, project, list(case.get("unavailable_references", [])))
    for name, content in case.get("files", {}).items():
        target = project / name
        target.write_text(content, encoding="utf-8")
    preamble = host_preamble(project, description)
    turns = []
    for index, turn in enumerate(case["turns"], start=1):
        user = turn["user"]
        if index == 1:
            prompt = preamble + user
            (session / "turn-1-prompt.txt").write_text(prompt, encoding="utf-8")
        else:
            (session / f"turn-{index}-user.txt").write_text(user, encoding="utf-8")
        turns.append({"index": index - 1, "user": user})
    private = run_dir / "private" / "rubrics"
    private.mkdir(parents=True, exist_ok=True)
    rubric_path = private / f"{case['id']}.json"
    if not rubric_path.exists():
        rubric_path.write_text(json.dumps({
            "id": case["id"],
            "title": case["title"],
            "tags": case["tags"],
            "turns": [
                {"expect": turn["expect"], "reject": turn["reject"]}
                for turn in case["turns"]
            ],
            "trace": case.get("trace"),
        }, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "key": session_key,
        "id": case["id"],
        "repetition": repetition,
        "turns": turns,
        "trace_required": list((case.get("trace") or {}).get("required", [])),
        **identity,
    }
    private_sessions = run_dir / "private" / "sessions"
    private_sessions.mkdir(parents=True, exist_ok=True)
    (private_sessions / f"{session_key}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def prepare_outcome_arms(root: Path, run_dir: Path, outcome: dict) -> dict:
    source = suite_paths(root)[2]
    description = skill_description(source)
    arms = {}
    for arm, enabled in (("enabled", True), ("disabled", False)):
        session = run_dir / "outcomes" / outcome["id"] / arm
        project = session / "project"
        project.mkdir(parents=True)
        if enabled:
            identity = copy_skill(source, project, [])
            prompt = host_preamble(project, description) + outcome["request"]
        else:
            identity = {"source_fingerprint": fingerprint(source), "session_fingerprint": None, "omitted_references": []}
            prompt = disabled_preamble(project) + outcome["request"]
        (session / "turn-1-prompt.txt").write_text(prompt, encoding="utf-8")
        arms[arm] = identity
    labels = assign_labels(outcome["id"], run_dir)
    private = run_dir / "private" / "outcomes"
    private.mkdir(parents=True, exist_ok=True)
    (private / f"{outcome['id']}.json").write_text(json.dumps({
        "id": outcome["id"],
        "request": outcome["request"],
        "downstream_input": outcome["downstream_input"],
        "criteria": outcome["criteria"],
        "labels": labels,
    }, indent=2) + "\n", encoding="utf-8")
    return {"id": outcome["id"], "labels": labels, "arms": arms}


def assign_labels(outcome_id: str, run_dir: Path) -> dict[str, str]:
    # Stable for a run directory and outcome, unpredictable across runs.
    seed = hashlib.sha256(f"{run_dir}:{outcome_id}:{os.urandom(16).hex()}".encode()).digest()
    enabled_is_a = seed[0] % 2 == 0
    if enabled_is_a:
        return {"A": "enabled", "B": "disabled"}
    return {"A": "disabled", "B": "enabled"}


def prepare_downstream(run_dir: Path, outcome_id: str, arm: str, produced_prompt: str) -> Path:
    private = json.loads((run_dir / "private" / "outcomes" / f"{outcome_id}.json").read_text(encoding="utf-8"))
    session = run_dir / "outcomes" / outcome_id / f"downstream-{arm}"
    project = session / "project"
    if project.exists():
        raise FileExistsError(session)
    project.mkdir(parents=True)
    prompt = disabled_preamble(project) + produced_prompt.strip() + "\n"
    (session / "turn-1-prompt.txt").write_text(prompt, encoding="utf-8")
    (session / "turn-2-user.txt").write_text(private["downstream_input"], encoding="utf-8")
    return session


def prepare_run(root: Path, run_dir: Path, plan: dict) -> dict:
    assert_outside_repo(root, run_dir)
    if run_dir.exists():
        raise FileExistsError(f"run-dir already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    suite = load_suite(root)
    outcomes = load_outcomes(root)
    by_id = case_index(suite)
    description = skill_description(suite_paths(root)[2])
    source_before = fingerprint(suite_paths(root)[2])
    repetitions = plan["repetitions_completed"] if plan["live_required"] else 0
    session_index = []
    sequence = 0
    for selected in plan["cases"]:
        case = by_id[selected["id"]]
        for repetition in range(1, repetitions + 1):
            sequence += 1
            session_key = f"s{sequence:03d}"
            manifest = prepare_case_session(root, run_dir, case, repetition, description, session_key)
            session_index.append({"key": session_key, "id": case["id"], "repetition": repetition})
            del manifest
    outcome_by_id = {case["id"]: case for case in outcomes["cases"]}
    prepared_outcomes = []
    if plan["live_required"]:
        for outcome_id in plan["outcome_ids"]:
            prepared_outcomes.append(prepare_outcome_arms(root, run_dir, outcome_by_id[outcome_id]))
    if fingerprint(suite_paths(root)[2]) != source_before:
        raise RuntimeError("prepare changed the candidate skill")
    plan = dict(plan)
    plan["source_fingerprint"] = source_before
    plan["prepared_outcomes"] = [{"id": item["id"]} for item in prepared_outcomes]
    plan["sessions"] = session_index
    (run_dir / "plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    private_dir = run_dir / "private"
    private_dir.mkdir(parents=True, exist_ok=True)
    (private_dir / "session-index.json").write_text(json.dumps(session_index, indent=2) + "\n", encoding="utf-8")
    return plan


def session_dir(run_dir: Path, case_id: str, repetition: int) -> Path:
    index = json.loads((run_dir / "private" / "session-index.json").read_text(encoding="utf-8"))
    for row in index:
        if row["id"] == case_id and row["repetition"] == repetition:
            return run_dir / "sessions" / row["key"]
    raise KeyError(f"no session for {case_id} repetition {repetition}")


def reviewer_packet(run_dir: Path, case_id: str, repetition: int) -> str:
    rubric = json.loads((run_dir / "private" / "rubrics" / f"{case_id}.json").read_text(encoding="utf-8"))
    session = session_dir(run_dir, case_id, repetition)
    manifest = json.loads((run_dir / "private" / "sessions" / f"{session.name}.json").read_text(encoding="utf-8"))
    blocks = []
    for turn in manifest["turns"]:
        index = turn["index"] + 1
        transcript_path = session / f"transcript-turn-{index}.txt"
        transcript = transcript_path.read_text(encoding="utf-8") if transcript_path.is_file() else ""
        expect = rubric["turns"][turn["index"]]["expect"]
        reject = rubric["turns"][turn["index"]]["reject"]
        blocks.append(
            f"Turn {index} user:\n{turn['user']}\n\n"
            f"Turn {index} assistant:\n{transcript or '[no transcript]'}\n\n"
            "Expect:\n" + "\n".join(f"- {item}" for item in expect) + "\n\n"
            "Reject:\n" + "\n".join(f"- {item}" for item in reject)
        )
    trace = rubric.get("trace")
    trace_text = "No trace rubric."
    if trace:
        trace_text = (
            "Required reference reads: " + ", ".join(trace["required"]) + "\n"
            "Unnecessary reference reads: " + ", ".join(trace["unnecessary"]) + "\n"
            "Tool events are unverified unless the packet includes a host tool log, which this packet does not."
        )
    return (
        "Grade this transcript against its rubric. Do not rewrite the rubric. "
        "Do not include filesystem paths in reasons. "
        "A rejection passes only when the assistant did not do that thing. "
        "Return JSON with visible_status, failure_category or null, disputed, reason, "
        "turns[{expect:[{result,reason}], reject:[{result,reason}]}], "
        "trace_status, and trace_note.\n"
        "visible_status is pass, fail, blocked, or not_run. "
        "failure_category is one of: product behavior, evaluator defect, infrastructure, presentation. "
        "Use product behavior for a wrong answer, missing clarification, unauthorized effect, or lost constraint. "
        "Use evaluator defect only when the rubric rejects a valid equivalent. "
        "Use infrastructure when evidence or the session is missing. "
        "Use presentation for incidental phrasing that no expectation makes substantive. "
        "Set disputed true when a human should settle the judgment.\n\n"
        f"Case: {case_id}\n{trace_text}\n\n" + "\n\n".join(blocks) + "\n"
    )


def outcome_reviewer_packet(run_dir: Path, outcome_id: str) -> str:
    private = json.loads((run_dir / "private" / "outcomes" / f"{outcome_id}.json").read_text(encoding="utf-8"))
    outputs = {}
    for label, arm in private["labels"].items():
        path = run_dir / "outcomes" / outcome_id / f"downstream-{arm}" / "transcript-turn-2.txt"
        if not path.is_file():
            path = run_dir / "outcomes" / outcome_id / f"downstream-{arm}" / "transcript-turn-1.txt"
        outputs[label] = path.read_text(encoding="utf-8") if path.is_file() else "[no transcript]"
    criteria = "\n".join(f"- {item}" for item in private["criteria"])
    return (
        "Review two anonymized outputs. You do not know which condition produced them. "
        "Judge every criterion for Output A and Output B before you state a preference. "
        "Preference is A, B, tie, or uncertain. Do not use a branded heading as a proxy for quality. "
        "Do not include filesystem paths. Return JSON only: "
        "{\"criteria\":[{\"label_a\":\"pass|fail|uncertain\",\"label_b\":\"pass|fail|uncertain\",\"note\":\"\"}],"
        "\"preference_label\":\"A|B|tie|uncertain\",\"disputed\":false,\"reason\":\"\"}.\n\n"
        f"Task:\n{private['request']}\n\n"
        f"Downstream input:\n{private['downstream_input']}\n\n"
        f"Criteria:\n{criteria}\n\n"
        "Output A:" + "\n" + outputs["A"] + "\n\n"
        "Output B:" + "\n" + outputs["B"] + "\n"
    )


def write_packets(run_dir: Path) -> list[Path]:
    plan = load_json(run_dir / "plan.json")
    written = []
    packet_root = run_dir / "private" / "packets"
    packet_root.mkdir(parents=True, exist_ok=True)
    repetitions = plan["repetitions_completed"]
    for selected in plan["cases"]:
        for repetition in range(1, repetitions + 1):
            text = reviewer_packet(run_dir, selected["id"], repetition)
            path = packet_root / f"{selected['id']}-r{repetition}.txt"
            path.write_text(text, encoding="utf-8")
            written.append(path)
    for outcome_id in plan["outcome_ids"]:
        text = outcome_reviewer_packet(run_dir, outcome_id)
        path = packet_root / f"outcome-{outcome_id}.txt"
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def normalize_case_grade(case: dict, grade: dict) -> dict:
    turns = case["turns"]
    visible = grade.get("visible_status")
    if visible not in CASE_STATUSES:
        raise ValueError(f"{case['id']}: invalid visible_status")
    graded_turns = grade.get("turns")
    if visible in {"not_run", "blocked"} and not graded_turns:
        graded_turns = []
    elif not isinstance(graded_turns, list) or len(graded_turns) != len(turns):
        raise ValueError(f"{case['id']}: turn count does not match the rubric")
    any_fail = False
    normalized_turns = []
    if not graded_turns and visible in {"not_run", "blocked"}:
        pass
    else:
        for index, (turn, graded) in enumerate(zip(turns, graded_turns)):
            if set(graded) != {"expect", "reject"}:
                raise ValueError(f"{case['id']}: turn {index} must contain expect and reject")
            for kind, expected in (("expect", turn["expect"]), ("reject", turn["reject"])):
                items = graded[kind]
                if not isinstance(items, list) or len(items) != len(expected):
                    raise ValueError(f"{case['id']}: {kind} count does not match the rubric")
                for item in items:
                    if item.get("result") not in {"pass", "fail"}:
                        raise ValueError(f"{case['id']}: item result must be pass or fail")
                    if not str(item.get("reason", "")).strip():
                        raise ValueError(f"{case['id']}: item reason is required")
                    if item["result"] == "fail":
                        any_fail = True
            normalized_turns.append(graded)
    if visible == "pass" and any_fail:
        raise ValueError(f"{case['id']}: visible pass contradicts a failed item")
    if visible == "fail" and not any_fail:
        raise ValueError(f"{case['id']}: visible fail needs a failed item")
    category = grade.get("failure_category")
    if visible == "fail" and category not in FAILURE_CATEGORIES:
        raise ValueError(f"{case['id']}: a failure needs one of the four categories")
    if visible == "pass" and category is not None:
        raise ValueError(f"{case['id']}: a pass cannot carry a failure category")
    disputed = bool(grade.get("disputed", False))
    trace = case.get("trace")
    trace_status = grade.get("trace_status", "not_applicable")
    trace_note = str(grade.get("trace_note", ""))
    if trace:
        if trace_status == "not_applicable" and visible in {"not_run", "blocked"}:
            trace_status = "blocked" if visible == "blocked" else "unverified"
        if trace_status == "verified" and grade.get("trace_evidence") != "host-tool-events":
            trace_status = "unverified"
            trace_note = (
                "Required reads stay unverified. The host did not supply tool events, "
                "and a claimed read is not verification."
            )
        if trace_status not in {"verified", "unverified", "blocked"}:
            raise ValueError(f"{case['id']}: trace status is invalid")
    elif trace_status != "not_applicable":
        raise ValueError(f"{case['id']}: unexpected trace status")
    status = visible
    if visible == "pass":
        if trace and trace_status != "verified":
            status = "unverified"
            category = "infrastructure"
        elif disputed:
            status = "unverified"
            category = "evaluator defect"
        else:
            category = None
    elif visible == "fail" and disputed and category is None:
        category = "evaluator defect"
    elif visible in {"blocked", "not_run"} and category is None:
        category = "infrastructure"
    return {
        "id": case["id"],
        "title": case["title"],
        "tags": case["tags"],
        "boundary": boundary_for(case["id"]),
        "repetition": grade.get("repetition", 1),
        "role": grade.get("role", "target"),
        "control": bool(grade.get("control", False)),
        "status": status,
        "visible_status": visible,
        "failure_category": category,
        "disputed": disputed,
        "reason": str(grade.get("reason", "")).strip(),
        "turns": normalized_turns,
        "trace_status": trace_status,
        "trace_note": trace_note,
    }


def unblind_preference(label: str, labels: dict[str, str]) -> str:
    if label == "tie":
        return "tie"
    if label == "uncertain":
        return "uncertain"
    if label not in labels:
        raise ValueError("preference must be A, B, tie, or uncertain")
    return labels[label]


def deterministic_outcome_notes(outcome: dict, enabled_text: str, disabled_text: str) -> list[dict]:
    notes = []
    for arm, text in (("enabled", enabled_text), ("disabled", disabled_text)):
        if outcome["id"] == "writing":
            count = len(WORD.findall(text))
            notes.append({
                "arm": arm,
                "check": "invitation word count",
                "value": count,
                "pass": 60 <= count <= 80,
            })
        elif outcome["id"] == "summarization":
            bullets = [
                line for line in text.splitlines()
                if re.match(r"\s*(?:[-*]|\d+[.)])\s+\S", line)
            ]
            notes.append({
                "arm": arm,
                "check": "bullet count",
                "value": len(bullets),
                "pass": len(bullets) == 3,
            })
        elif outcome["id"] == "structured-extraction":
            expected = extraction_target(outcome)
            parsed = parse_json_payload(text)
            notes.append({
                "arm": arm,
                "check": "exact JSON array",
                "value": parsed if isinstance(parsed, list) else None,
                "pass": parsed == expected,
            })
        elif outcome["id"] == "coding-instructions":
            notes.append(check_python_function(arm, text))
    return notes


def extraction_target(outcome: dict) -> list:
    for criterion in outcome["criteria"]:
        match = re.search(r"\[\{.*\}\]", criterion)
        if match:
            return json.loads(match.group(0))
    raise ValueError("structured extraction criterion has no JSON array")


def parse_json_payload(text: str):
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", stripped, re.DOTALL)
    if fence:
        stripped = fence.group(1).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def check_python_function(arm: str, text: str) -> dict:
    source = text
    fence = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        source = fence.group(1)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"arm": arm, "check": "stable_unique behavior", "pass": False, "value": f"syntax error: {exc.msg}"}
    if not python_source_is_contained(tree):
        return {
            "arm": arm,
            "check": "stable_unique behavior",
            "pass": False,
            "value": "source was not executed because it is not contained",
        }
    result = run_contained_function(source)
    return {"arm": arm, "check": "stable_unique behavior", "pass": result["pass"], "value": result["value"]}


def python_source_is_contained(tree: ast.AST) -> bool:
    allowed_modules = {"collections", "typing", "dataclasses"}
    banned_calls = {"open", "eval", "exec", "compile", "__import__", "input", "breakpoint"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] not in allowed_modules for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in allowed_modules:
                return False
        elif isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
            if name in banned_calls or name in {"system", "popen", "remove", "unlink"}:
                return False
    return True


def run_contained_function(source: str) -> dict:
    runner = r"""
import json, sys
source = sys.stdin.read()
namespace = {}
exec(compile(source, "<candidate>", "exec"), namespace)
fn = namespace["stable_unique"]
sample = [3, 1]
fn(sample)
report = {
    "duplicates": fn([3, 1, 3, 2, 1]),
    "unhashable": fn([[1], [1], [2]]),
    "empty": fn([]),
    "preserved": sample == [3, 1],
}
print(json.dumps(report))
"""
    completed = subprocess.run(
        [sys.executable, "-I", "-B", "-c", runner],
        input=source,
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )
    if completed.returncode != 0:
        return {"pass": False, "value": completed.stderr.strip()[-300:]}
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"pass": False, "value": "function did not return a report"}
    passed = (
        report.get("duplicates") == [3, 1, 2]
        and report.get("unhashable") == [[1], [2]]
        and report.get("empty") == []
        and report.get("preserved") is True
    )
    return {"pass": passed, "value": report}


def word_count(text: str) -> int:
    return len(WORD.findall(text))


def read_optional(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def assemble_results(
    root: Path,
    run_dir: Path,
    grades: dict,
    timing: dict,
    host: dict,
    results_root: Path | None = None,
) -> dict:
    plan = load_json(run_dir / "plan.json")
    suite = load_suite(root)
    outcomes = load_outcomes(root)
    by_id = case_index(suite)
    role_by_id = {item["id"]: item for item in plan["cases"]}
    grade_rows = {(item["id"], int(item.get("repetition", 1))): item for item in grades.get("cases", [])}
    normalized = []
    for selected in plan["cases"]:
        case = by_id[selected["id"]]
        for repetition in range(1, plan["repetitions_completed"] + 1):
            grade = grade_rows.get((selected["id"], repetition))
            if grade is None:
                raise ValueError(f"missing grade for {selected['id']} repetition {repetition}")
            grade = dict(grade)
            grade["repetition"] = repetition
            grade["role"] = selected["role"]
            grade["control"] = selected["control"]
            if grade.get("visible_status") == "pass":
                for index, _turn in enumerate(case["turns"]):
                    transcript = read_optional(
                        session_dir(run_dir, case["id"], repetition) / f"transcript-turn-{index + 1}.txt"
                    )
                    if not transcript.strip():
                        raise ValueError(f"{case['id']}: a pass requires a transcript for turn {index + 1}")
            normalized.append(normalize_case_grade(case, grade))
    outcome_grades = {item["id"]: item for item in grades.get("outcomes", [])}
    outcome_rows = []
    for outcome in outcomes["cases"]:
        if outcome["id"] not in plan["outcome_ids"]:
            continue
        grade = outcome_grades.get(outcome["id"])
        if grade is None:
            raise ValueError(f"missing outcome grade for {outcome['id']}")
        private = load_json(run_dir / "private" / "outcomes" / f"{outcome['id']}.json")
        if grade.get("status") == "not_run":
            outcome_rows.append({
                "id": outcome["id"],
                "status": "not_run",
                "failure_category": "infrastructure",
                "reason": grade.get("reason", "not run"),
                "preference": None,
                "criteria": [],
                "deterministic": [],
                "question_marks": {},
                "words": {},
                "incomplete": {"enabled": True, "disabled": True},
                "human_calibration": "pending",
            })
            continue
        preference = unblind_preference(grade["preference_label"], private["labels"])
        mapped = []
        for index, criterion in enumerate(outcome["criteria"]):
            scored = grade["criteria"][index]
            by_arm = {
                private["labels"]["A"]: scored["label_a"],
                private["labels"]["B"]: scored["label_b"],
            }
            mapped.append({
                "text": criterion,
                "enabled": by_arm["enabled"],
                "disabled": by_arm["disabled"],
                "note": scored.get("note", ""),
            })
        enabled_downstream = read_optional(run_dir / "outcomes" / outcome["id"] / "downstream-enabled" / "transcript-turn-2.txt")
        disabled_downstream = read_optional(run_dir / "outcomes" / outcome["id"] / "downstream-disabled" / "transcript-turn-2.txt")
        enabled_prompt = read_optional(run_dir / "outcomes" / outcome["id"] / "enabled" / "transcript-turn-1.txt")
        disabled_prompt = read_optional(run_dir / "outcomes" / outcome["id"] / "disabled" / "transcript-turn-1.txt")
        outcome_rows.append({
            "id": outcome["id"],
            "status": "recorded",
            "preference": preference,
            "disputed": bool(grade.get("disputed", False)),
            "reason": grade.get("reason", ""),
            "criteria": mapped,
            "deterministic": deterministic_outcome_notes(outcome, enabled_downstream, disabled_downstream),
            "question_marks": {
                "enabled": enabled_prompt.count("?"),
                "disabled": disabled_prompt.count("?"),
            },
            "words": {
                "enabled_prompt": word_count(enabled_prompt),
                "disabled_prompt": word_count(disabled_prompt),
                "enabled_answer": word_count(enabled_downstream),
                "disabled_answer": word_count(disabled_downstream),
            },
            "incomplete": grade.get("incomplete", {"enabled": False, "disabled": False}),
            "human_calibration": "pending",
        })
    summary = summarize_cases(normalized)
    if results_root is None:
        results_root = root / "tests" / "behavior" / "results"
    previous_payload, previous_path = find_previous_baseline(
        results_root,
        plan["version"],
        None,
    )
    blocking = []
    if previous_payload and plan["role"] == "release-baseline":
        blocking = blocking_findings(previous_payload.get("cases", []), normalized)
    usage = timing.get("usage", {})
    if "note" not in usage:
        usage = {"input_tokens": None, "output_tokens": None, "note": "not measured"}
    if usage.get("input_tokens") is None and usage.get("output_tokens") is None and not usage.get("note"):
        usage["note"] = "not measured"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "role": plan["role"],
        "mode": plan["mode"],
        "version": plan["version"],
        "commit": plan["commit"],
        "source_fingerprint": plan["source_fingerprint"],
        "generated_at": timing.get("generated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": host,
        "repetitions_planned": plan["repetitions_planned"],
        "repetitions_completed": plan["repetitions_completed"],
        "skipped": plan["skipped"],
        "timing": {
            "live_seconds": timing.get("live_seconds"),
            "wall_seconds": timing.get("wall_seconds"),
            "per_case_seconds": timing.get("per_case_seconds", {}),
        },
        "usage": {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "note": usage.get("note") or "not measured",
        },
        "budget": {
            "repair_cycles_used": timing.get("repair_cycles_used", 0),
            "repair_cycle_limit": REPAIR_CYCLE_LIMIT,
            "live_seconds_limit": LIVE_SECONDS_LIMIT,
            "live_seconds": timing.get("live_seconds"),
        },
        "summary": summary,
        "cases": normalized,
        "outcomes": outcome_rows,
        "baseline_comparison": {
            "previous": None if previous_path is None else previous_path.as_posix(),
            "previous_version": None if previous_payload is None else previous_payload.get("version"),
            "blocking": blocking,
        },
    }
    if payload["baseline_comparison"]["previous"]:
        payload["baseline_comparison"]["previous"] = Path(payload["baseline_comparison"]["previous"]).name
        if previous_path is not None:
            payload["baseline_comparison"]["previous_version_dir"] = previous_path.parent.name
    return sanitize(payload)


def summarize_cases(cases: list[dict]) -> dict:
    counts = {status: 0 for status in CASE_STATUSES}
    for case in cases:
        counts[case["status"]] = counts.get(case["status"], 0) + 1
    # One row per case id. A case passes only when every recorded repetition passed.
    by_id: dict[str, list[dict]] = {}
    for case in cases:
        by_id.setdefault(case["id"], []).append(case)
    case_counts = {status: 0 for status in CASE_STATUSES}
    boundaries: dict[str, dict] = {}
    failures = []
    for case_id, rows in by_id.items():
        status = aggregate_status(rows)
        case_counts[status] += 1
        boundary = rows[0]["boundary"]
        bucket = boundaries.setdefault(boundary, {status: 0 for status in CASE_STATUSES})
        bucket[status] += 1
        if status == "fail":
            failed = next(row for row in rows if row["status"] == "fail")
            failures.append({
                "id": case_id,
                "failure_category": failed["failure_category"],
                "reason": failed["reason"],
            })
    total = sum(case_counts.values())
    return {
        "repetition_rows": counts,
        "cases": case_counts,
        "case_total": total,
        "pass_rate": None if total == 0 else round(case_counts["pass"] / total, 4),
        "by_boundary": boundaries,
        "failing_cases": failures,
    }


def aggregate_status(rows: list[dict]) -> str:
    statuses = {row["status"] for row in rows}
    if "fail" in statuses:
        return "fail"
    if "blocked" in statuses:
        return "blocked"
    if "unverified" in statuses:
        return "unverified"
    if statuses == {"pass"}:
        return "pass"
    if "not_run" in statuses and statuses <= {"not_run", "pass"}:
        return "not_run" if "pass" not in statuses else "unverified"
    return "unverified"


def blocking_findings(previous_cases: list[dict], current_cases: list[dict]) -> list[dict]:
    previous: dict[str, list[str]] = {}
    current: dict[str, list[str]] = {}
    for row in previous_cases:
        previous.setdefault(row["id"], []).append(row["status"])
    for row in current_cases:
        current.setdefault(row["id"], []).append(row["status"])
    findings = []
    for case_id, statuses in current.items():
        before = previous.get(case_id)
        if not before or set(before) != {"pass"}:
            continue
        if "fail" in statuses:
            findings.append({
                "id": case_id,
                "kind": "regression",
                "previous": "pass",
                "current": "fail",
                "blocking": True,
            })
        elif set(statuses) != {"pass"}:
            findings.append({
                "id": case_id,
                "kind": "evidence_gap",
                "previous": "pass",
                "current": sorted(set(statuses))[0],
                "blocking": True,
            })
    return findings


def parse_semver(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))


def find_previous_baseline(results_root: Path, version: str, exclude: Path | None):
    if not results_root.is_dir():
        return None, None
    rows = []
    for path in sorted(results_root.glob("*/*.json")):
        if exclude and path.resolve() == exclude.resolve():
            continue
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        if payload.get("role") != "release-baseline":
            continue
        if payload.get("schema_version") != SCHEMA_VERSION:
            continue
        rows.append((payload.get("version", "0.0.0"), payload.get("generated_at", ""), path, payload))
    if not rows:
        return None, None
    current = parse_semver(version)
    older = [row for row in rows if parse_semver(row[0]) < current]
    if older:
        highest = max(parse_semver(row[0]) for row in older)
        pool = [row for row in older if parse_semver(row[0]) == highest]
    else:
        pool = [row for row in rows if row[0] == version]
    if not pool:
        return None, None
    pool.sort(key=lambda row: (row[1], row[2].name))
    chosen = pool[-1]
    return chosen[3], chosen[2]


def sanitize(value):
    if isinstance(value, str):
        return PRIVATE_PATH.sub("[path]", value)
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    return value


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    counts = summary["cases"]
    lines = [
        f"# YSAP live eval {payload['version']}",
        "",
        f"- Role: {payload['role']}",
        f"- Mode: {payload['mode']}",
        f"- Commit: `{payload['commit']}`",
        f"- Generated: {payload['generated_at']}",
        f"- Host: {payload['host'].get('name', 'unrecorded')} / {payload['host'].get('model', 'unrecorded')} / {payload['host'].get('os', 'unrecorded')}",
        f"- Repetitions: {payload['repetitions_completed']} of {payload['repetitions_planned']}",
        f"- Live seconds: {payload['timing'].get('live_seconds')}",
        f"- Wall seconds: {payload['timing'].get('wall_seconds')}",
        f"- Usage: {payload['usage'].get('note')}",
        f"- Pass rate: {counts['pass']}/{summary['case_total']} cases ({summary['pass_rate']})",
        "",
        "A case passes only when every recorded repetition passed and every required trace was verified.",
        "",
        "## Skipped",
        "",
    ]
    if payload["skipped"]:
        for item in payload["skipped"]:
            lines.append(f"- {item['item']}: {item['reason']}")
    else:
        lines.append("- Nothing in the planned run was skipped.")
    lines.extend(["", "## Pass rate by category", "", "| Category | Pass | Fail | Unverified | Blocked | Not run |", "| --- | --- | --- | --- | --- | --- |"])
    for name, _ids in BOUNDARIES:
        bucket = summary["by_boundary"].get(name, {status: 0 for status in CASE_STATUSES})
        lines.append(
            f"| {name} | {bucket.get('pass', 0)} | {bucket.get('fail', 0)} | "
            f"{bucket.get('unverified', 0)} | {bucket.get('blocked', 0)} | {bucket.get('not_run', 0)} |"
        )
    lines.extend(["", "## Cases", "", "| Case | Status | Category |", "| --- | --- | --- |"])
    seen = set()
    for case in payload["cases"]:
        if case["id"] in seen:
            continue
        seen.add(case["id"])
        lines.append(f"| {case['id']} | {case['status']} | {case['failure_category'] or ''} |")
    lines.extend(["", "## Failures", ""])
    if summary["failing_cases"]:
        lines.append("| Case | Category | Reason |")
        lines.append("| --- | --- | --- |")
        for failure in summary["failing_cases"]:
            reason = failure["reason"].replace("\n", " ").replace("|", "/")
            lines.append(f"| {failure['id']} | {failure['failure_category']} | {reason} |")
    else:
        lines.append("No failing cases.")
    lines.extend(["", "## Unverified or blocked", ""])
    extras = [
        case for case in payload["cases"]
        if case["status"] in {"unverified", "blocked", "not_run"}
    ]
    if extras:
        for case in extras:
            lines.append(f"- `{case['id']}` repetition {case['repetition']}: {case['status']} ({case['failure_category']}). {case['reason']}")
    else:
        lines.append("None.")
    lines.extend(["", "## Outcome comparison", ""])
    if not payload["outcomes"]:
        lines.append("Not run.")
    for outcome in payload["outcomes"]:
        lines.append(f"### {outcome['id']}")
        lines.append("")
        lines.append(f"- Status: {outcome['status']}")
        lines.append(f"- Blinded preference after unblinding: {outcome.get('preference')}")
        lines.append(f"- Human calibration: {outcome.get('human_calibration')}")
        if outcome.get("words"):
            lines.append(f"- Words: {outcome['words']}")
        if outcome.get("deterministic"):
            lines.append(f"- Deterministic checks: {outcome['deterministic']}")
        lines.append("")
    comparison = payload["baseline_comparison"]
    lines.extend(["## Baseline comparison", ""])
    if not comparison.get("previous_version"):
        lines.append("No earlier release baseline. Nothing is flagged as a regression.")
    else:
        lines.append(
            f"Compared with {comparison.get('previous_version_dir')}/{comparison.get('previous')} "
            f"(version {comparison.get('previous_version')})."
        )
        if comparison["blocking"]:
            for finding in comparison["blocking"]:
                lines.append(
                    f"- Blocking {finding['kind']}: `{finding['id']}` was {finding['previous']} and is now {finding['current']}."
                )
        else:
            lines.append("No blocking regressions.")
    lines.extend([
        "",
        "## Per-PR command",
        "",
        "```text",
        "python -B .cursor/skills/ysap-live-eval/scripts/ysap_live_eval.py plan --mode per-pr --base origin/main",
        "```",
        "",
        "Follow `.cursor/skills/ysap-live-eval/SKILL.md` to execute the plan. Raw transcripts stay outside the repository.",
        "",
    ])
    return "\n".join(lines)


def exclusive_write(path: Path, content: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)


def allocate_result_paths(directory: Path, now: datetime) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    date_stamp = now.astimezone(timezone.utc).strftime("%Y-%m-%d")
    time_stamp = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    for stamp in (date_stamp, time_stamp):
        json_path = directory / f"{stamp}.json"
        md_path = directory / f"{stamp}.md"
        if not json_path.exists() and not md_path.exists():
            return json_path, md_path
    raise FileExistsError(f"result names for {date_stamp} and {time_stamp} already exist")


def write_results(directory: Path, payload: dict, now: datetime) -> tuple[Path, Path]:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported results schema")
    rendered = json.dumps(payload, indent=2) + "\n"
    markdown = render_markdown(payload)
    if PRIVATE_PATH.search(rendered) or PRIVATE_PATH.search(markdown):
        raise ValueError("public results still contain a private path")
    json_path, md_path = allocate_result_paths(directory, now)
    exclusive_write(json_path, rendered)
    try:
        exclusive_write(md_path, markdown)
    except Exception:
        # The JSON is already a kept result. Do not delete it to make a retry fit the same name.
        raise
    return json_path, md_path


def record(root: Path, run_dir: Path, grades_path: Path, timing_path: Path, host_path: Path, now: datetime) -> tuple[Path, Path]:
    payload = assemble_results(
        root,
        run_dir,
        load_json(grades_path),
        load_json(timing_path),
        load_json(host_path),
    )
    version = payload["version"]
    directory = root / "tests" / "behavior" / "results" / version
    return write_results(directory, payload, now)


def make_plan_from_git(root: Path, mode: str, base: str, repetitions: int | None, skip_reason: str, allow_dirty: bool) -> dict:
    if not allow_dirty:
        assert_clean(root)
    version = read_version(root)
    commit = head_commit(root)
    if mode == "release":
        paths: list[str] = []
        case_ids: list[str] = []
        outcomes_changed = False
    else:
        paths = changed_paths(root, base)
        case_ids = changed_case_ids(root, base) if "tests/behavior/cases.json" in paths else []
        outcomes_changed = "tests/behavior/outcomes.json" in paths and outcomes_file_changed(root, base)
    return build_plan(
        mode=mode,
        paths=paths,
        suite=load_suite(root),
        outcomes=load_outcomes(root),
        changed_case_ids=case_ids,
        outcomes_changed=outcomes_changed,
        repetitions=repetitions,
        skip_reason=skip_reason,
        version=version,
        commit=commit,
    )


def command_plan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_root()
    plan = make_plan_from_git(
        root,
        args.mode,
        args.base,
        args.repetitions,
        args.skip_reason,
        args.allow_dirty,
    )
    text = json.dumps(plan, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def command_prepare(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_root()
    plan = make_plan_from_git(
        root,
        args.mode,
        args.base,
        args.repetitions,
        args.skip_reason,
        args.allow_dirty,
    )
    prepare_run(root, Path(args.run_dir), plan)
    print(json.dumps({"run_dir": str(Path(args.run_dir)), "cases": len(plan["cases"]), "outcomes": len(plan["outcome_ids"])}, indent=2))
    return 0


def command_packets(args: argparse.Namespace) -> int:
    written = write_packets(Path(args.run_dir))
    print(json.dumps([str(path) for path in written], indent=2))
    return 0


def command_downstream(args: argparse.Namespace) -> int:
    produced = Path(args.produced).read_text(encoding="utf-8")
    session = prepare_downstream(Path(args.run_dir), args.outcome, args.arm, produced)
    print(session.as_posix())
    return 0


def command_record(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_root()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    json_path, md_path = record(
        root,
        Path(args.run_dir),
        Path(args.grades),
        Path(args.timing),
        Path(args.host),
        now,
    )
    print(json.dumps({"json": json_path.as_posix(), "markdown": md_path.as_posix()}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ysap_live_eval")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="select cases for per-PR or release mode")
    plan.add_argument("--mode", choices=["per-pr", "release"], required=True)
    plan.add_argument("--base", default="origin/main")
    plan.add_argument("--root", default=None)
    plan.add_argument("--repetitions", type=int, default=None)
    plan.add_argument("--skip-reason", default="")
    plan.add_argument("--allow-dirty", action="store_true")
    plan.add_argument("--out", default=None)
    plan.set_defaults(func=command_plan)

    prepare = sub.add_parser("prepare", help="create isolated sessions outside the repository")
    prepare.add_argument("--mode", choices=["per-pr", "release"], required=True)
    prepare.add_argument("--run-dir", required=True)
    prepare.add_argument("--base", default="origin/main")
    prepare.add_argument("--root", default=None)
    prepare.add_argument("--repetitions", type=int, default=None)
    prepare.add_argument("--skip-reason", default="")
    prepare.add_argument("--allow-dirty", action="store_true")
    prepare.set_defaults(func=command_prepare)

    packets = sub.add_parser("grader-packets", help="write reviewer prompts from saved transcripts")
    packets.add_argument("--run-dir", required=True)
    packets.set_defaults(func=command_packets)

    downstream = sub.add_parser("prepare-downstream", help="create a skill-free downstream session")
    downstream.add_argument("--run-dir", required=True)
    downstream.add_argument("--outcome", required=True)
    downstream.add_argument("--arm", choices=["enabled", "disabled"], required=True)
    downstream.add_argument("--produced", required=True)
    downstream.set_defaults(func=command_downstream)

    record = sub.add_parser("record", help="write an append-only public result")
    record.add_argument("--run-dir", required=True)
    record.add_argument("--grades", required=True)
    record.add_argument("--timing", required=True)
    record.add_argument("--host", required=True)
    record.add_argument("--root", default=None)
    record.add_argument("--now", default=None)
    record.set_defaults(func=command_record)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
