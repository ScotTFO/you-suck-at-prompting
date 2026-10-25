---
name: ysap-live-eval
description: Run the You Suck at Prompting public behavioral suite and blinded outcome comparisons in fresh sessions, then write an append-only result. Use for a per-PR live check or a release baseline. Do not use for ordinary prompting, prompt review, or editing the product skill.
metadata:
  internal: true
---

# YSAP live eval

Run the public suite in fresh product sessions and record the result. The product skill under `skills/you-suck-at-prompting/` is the thing under test. Do not edit it, do not edit a rubric to excuse a failure, and do not bump `VERSION`.

This skill is internal to the repository. It is not a second installable package skill. Keep it out of product sessions.

## Hard rules

- A product session receives only the prepared user turn and the host preamble the runner writes. Do not send the case id, rubric, expected route, this skill, or contributor docs.
- Start a fresh session for every case and repetition. Later turns resume that same session. Send only the next user text. Do not invent a missing assistant turn.
- Grade in a different fresh session from the one that produced the answer. Outcome review sees randomized labels before the condition is revealed.
- Failure categories are exactly `product behavior`, `evaluator defect`, `infrastructure`, and `presentation`. Human review settles a disputed judgment. Leave `human_calibration` pending until a person reviews an outcome sample.
- Stop after two repair cycles or 60 minutes of live product testing for one change, whichever comes first. Parallel sessions each consume their own elapsed time. Do not reset that budget by resuming a conversation.
- Public results are append-only under `tests/behavior/results/<version>/`. Never overwrite an earlier file. Raw transcripts, label maps, and machine-local paths stay outside the repository.
- A case with a required reference trace cannot pass unless the host supplies real tool events. A claimed read is unverified. Unverified loading is infrastructure, and the visible answer is still recorded.
- Release mode compares with the last release baseline. A case that passed there and fails now is a blocking regression. A pass that becomes unverified or blocked is a blocking evidence gap.

## Modes

Per-PR mode selects cases that cover the diff plus an unchanged control. One fresh run of each selected case. It is not a release qualification.

Release mode runs every behavior case and all five outcome comparisons, three times, against a clean checkout. Fewer repetitions require an explicit skip reason recorded in the result. The first baseline has no previous release to compare with.

A documentation-only diff does not require live cases. Deterministic checks still run:

```text
python -B -m unittest tests.test_skill_contract tests.test_behavior_cases tests.test_live_eval
```

## Per-PR command

From a clean candidate checkout:

```text
python -B .cursor/skills/ysap-live-eval/scripts/ysap_live_eval.py plan --mode per-pr --base origin/main
```

Use the same flags for `prepare`. Release mode is:

```text
python -B .cursor/skills/ysap-live-eval/scripts/ysap_live_eval.py plan --mode release
```

Add `--repetitions 1 --skip-reason "..."` only when the three-run release is not going to be executed, and record that reason.

## Run

1. Record the checkout path, commit, clean `git status`, and `VERSION`. Refuse a dirty tree. Confirm `prepare` prints the same source fingerprint before and after, and that the candidate skill bytes did not change.
2. Choose a run directory outside the repository. `prepare` rejects a directory inside it.

```text
python -B .cursor/skills/ysap-live-eval/scripts/ysap_live_eval.py prepare --mode per-pr --base origin/main --run-dir <outside-run-dir>
```

3. Read `private/session-index.json` in the run directory. Session directory names are opaque. For each entry, open a fresh product session whose entire task is `sessions/<key>/turn-1-prompt.txt`. The session may read only that session's `project/` directory. The installed skill is the copy under `project/.cursor/skills/you-suck-at-prompting/`. Disabled outcome arms and downstream sessions have no skill.
4. Save the assistant reply to `transcript-turn-1.txt` in that session directory. Copy it from the raw transcript message text with `save-reply`. Do not copy a rendered subagent completion: that channel turns each run of leading whitespace into one space, so nested Python survives in the raw message and collapses in the rendering. Resume the same session with `turn-2-user.txt`, then `turn-3-user.txt`, and so on. If an earlier turn fails, do not continue the product conversation; grade the remaining turns as not run.

```text
python -B .cursor/skills/ysap-live-eval/scripts/ysap_live_eval.py save-reply --transcript <transcript.json> --out <session>/transcript-turn-1.txt
```
5. For each outcome, run the enabled and disabled generation prompts. Save transcripts. If one arm asks a clarifying question, send the same factual answer to both arms when it applies, and keep the extra turns. Do not repair either prompt. If no usable prompt exists, mark that arm incomplete.
6. `prepare-downstream --run-dir <dir> --outcome <id> --arm enabled|disabled --produced <file>` builds the skill-free executor session. Turn 1 is the produced prompt. Turn 2 is the downstream input. Save `transcript-turn-2.txt`.
7. Write reviewer packets only after transcripts exist:

```text
python -B .cursor/skills/ysap-live-eval/scripts/ysap_live_eval.py grader-packets --run-dir <outside-run-dir>
```

Give each behavior packet to a fresh grader. Give each outcome packet to a fresh grader who has not seen the label map. The outcome packet contains Output A and Output B only. Record the preference before opening `private/outcomes/<id>.json`.

8. Write `grades.json`, `timing.json`, and `host.json` outside the repository. `grades.json` uses `visible_status` and, for outcomes, `preference_label` of `A`, `B`, `tie`, or `uncertain`. Do not put enabled or disabled into the outcome preference. `timing.json` includes measured `live_seconds` and `wall_seconds`. Set token fields to null and `usage.note` to `not measured` unless the host actually reported usage. Do not estimate tokens or cost.
9. Record:

```text
python -B .cursor/skills/ysap-live-eval/scripts/ysap_live_eval.py record --run-dir <outside-run-dir> --grades <grades.json> --timing <timing.json> --host <host.json>
```

`record` refuses to overwrite. It downgrades a trace "verified" claim that lacks host tool events, unblinds outcome labels, and flags blocking regressions against the newest older release baseline.

## Grade

Judge each expectation and rejection. A rejection passes only when the reply did not do the rejected thing. Exact output is exact. Equivalent meaning can pass a semantic expectation; say so in the reason. Do not stretch a rubric to protect a candidate.

Use `product behavior` when the reply loses the request, skips a required clarification, executes prompt-only content, or exceeds authority. Use `evaluator defect` when the rubric rejects a valid equivalent. Use `infrastructure` for a missing session, timeout, hidden tool trace, or unavailable model. Use `presentation` for incidental wording that no expectation makes substantive. Set `disputed` true when a person needs to settle it, and do not treat that row as a pass.

## Repair and stop

A repair cycle is a grouped fix after a completed result, followed by new checks. The initial runner and its deterministic tests are not a cycle. Do not change the product skill from an eval failure unless the task you were given is a product fix, and even then stop at the budget. An evaluator defect can be fixed in the runner or the grade, while the original result is kept. A repeated blocker or an exhausted budget ends in a handoff: candidate, category, evidence, budget used, and the decision a person still needs to make.

## Independent validation

Validation of a change to this runner or to testing policy is a new session that did not write the change. A fresh cloud-agent session counts. A fresh local Codex task also counts. The validator checks the candidate and reports findings. It does not implement fixes or start another validator.
