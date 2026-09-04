# Test the change you made

Routine maintenance needs the public package, Python, and checks matched to the change. The private evaluation lab is optional for that work. It is neither a runtime dependency nor a prerequisite for contributing a fix.

The [public behavioral suite](../tests/behavior/cases.json) contains ten synthetic conversations with reviewer rubrics. It has no model runner, service, credential requirement, or private cases. Every task is text-only. No test needs to send a message, write a user file, access an account, or change permissions.

## Choose the required evidence

Run the public package and fixture checks for every Public change, from the candidate checkout:

```text
python -B -m unittest tests.test_skill_contract tests.test_behavior_cases
```

These are offline checks. They validate package rules and fixture integrity, including malformed-fixture rejection. They do not invoke a model or prove that a host follows the skill. CI runs them on Linux and Windows while retaining the existing installer, version-policy, protected validation, and release checks.

Choose the highest applicable row before testing. Record the changed behavior and why the selected cases cover it.

| Change | Additional evidence | Fresh independent local Codex validation |
| --- | --- | --- |
| Documentation or cosmetic edits with no instruction or behavior change | Review the text, links, examples, and affected structure. | Not required solely for cosmetics. |
| Prompt wording or ordinary behavior | Run changed-case conversations plus unchanged controls. | Required. |
| Activation, authority, clarification lifecycle, or progressive disclosure | Run targeted positive, negative, and multi-turn cases, including the relevant read or tool traces. | Required. |
| Evaluator or host integration | Run the affected runner's deterministic regressions and broader affected-host checks. A broad compatibility qualification uses its full suite and default three fresh repetitions. | Required. |
| Testing policy, fixtures, or check logic | Run deterministic positive and negative checks and review the affected policy and case scenarios. Live runs are needed only if runtime behavior or a live-behavior claim changes. | Required. |

A focused selection normally needs one fresh run per selected case. Repeat when results are inconsistent or the risk calls for it, with the repetition count and reason recorded before rerunning. Preserve every failure; do not rerun until green. A focused pass is not a full qualification.

Ordinary prompt-behavior changes need a case that exercises the change and a control expected to remain unchanged. For activation or authority changes, also exercise the opposite decision and a relevant multi-turn conversation. Add a small synthetic regression if the current suite misses the defect. Do not change a rubric merely to excuse a candidate's failure.

Testing-policy and fixture changes do not themselves qualify the runtime. A known failed or unqualified candidate stays failed or unqualified until its required evidence passes. Automated research retains its separate qualification, calibration, allowlist, and human-promotion gates. This guide does not lower those requirements or authorize publication by a research worker.

## Select public cases

| Boundary | Cases |
| --- | --- |
| Silent activation and exact output controls | `clear-bypass`, `strict-json` |
| Prompt deliverable versus requested execution | `prompt-only`, `prompt-and-execute` |
| Unknown goal and resolved clarification | `unknown-goal-continuation`, `execution-clarification` |
| Source instructions and approval state | `quoted-instructions`, `approval-lifecycle` |
| Selective reference loading | `disclosure-simple`, `disclosure-independent-review` |

The JSON has a `user` message and reviewer-only `expect` and `reject` lists for each turn. `trace.required` and `trace.forbidden` refer to files under the candidate skill's `references/` directory. Those lists describe observable reads, not text the model should recite. Static tests check their paths and structure; a reviewer judges actual responses and traces.

## Run a selected conversation manually

1. Record the candidate's absolute checkout path, exact commit, clean tracked state, and package version. Use that exact skill, not an older global installation. Verify any session-local copy against the candidate before testing.
2. Start a fresh session for each case and repetition. Give the host access to only the candidate runtime, including its metadata and lazily readable references, plus the case's user messages. Keep contributor instructions, this guide, fixtures, rubrics, prior conversations, and private lab material out of the product session. Use the host's supported session-local skill loading or an isolated project that exposes only this runtime. If the host requires a project directory, a small disposable project may be needed; the private Test repository is not. Do not change global configuration, permissions, or installations to make a test run.
3. Record the host and version, model, OS, skill-loading method, allowed tools, and any unavoidable host instructions. Disable external-effect tools where the host permits it. Keep only the reads needed for skill references and an allowed question tool if available. If the exact candidate or required isolation cannot be established, mark the run blocked.
4. Send only the first turn's `user` string. Do not tell the model the case ID, expected route, rubric, pass criteria, or reference files it should load. For implicit activation checks, do not force an invocation or paste the full skill into the user prompt.
5. Review the response and actual tool events. Then send the next user string in the same conversation, answering through the host's question UI when applicable. Never seed an expected assistant response or replace a missing prior turn. If a failure makes later turns inapplicable, retain the failure and mark the remaining turns not run. Separate fresh calls do not prove multi-turn behavior.
6. Evaluate each turn against every expectation and rejection. Record pass, fail, blocked, or not run with a short reason and private evidence. A claimed tool call without an event or confirmed pending state is not execution. Unavailable tool or read proof is unverified, never a pass.

All execution cases request only visible text transformations. They test whether the requested work happened in the conversation, not file-write or external-action permissions. Do not infer safe file, account, or publication behavior from them. An actual tool-boundary change needs a separate synthetic, isolated test of that boundary.

For selective loading, run both disclosure cases in fresh sessions and capture a complete reference-read trace. Check required reads and forbidden reads against that trace. The complex case is the positive control that confirms reference reads are observable; absence in the simple case is not enough. If the host preloads all references, hides reads, or cannot expose them independently, mark selective-loading evidence blocked on that host. You may still report its visible response result separately. Prompt length or a good answer does not prove progressive disclosure.

## Independent validation and evidence

For a change that requires independent validation, use a fresh local Codex task with no inherited implementation conversation. Give it bounded criteria, the diff, selected checks, and a separate detached checkout of the exact candidate commit. The validator verifies its path, commit, detached HEAD, and clean tracked state, then runs the required checks itself. It reports findings without implementing fixes or creating another validator. A later candidate change requires renewed validation against the final commit.

Keep the validator's contributor review separate from product-behavior sessions. Local execution may call a remote model service; live checks are not offline. Report only the hosts and versions actually tested. Codex evidence does not qualify another host, and installer compatibility does not establish live behavior.

Keep raw transcripts and machine-local details outside the public package and public PR. A compact private record can use this template:

```text
Change and risk tier:
Candidate checkout / commit / VERSION:
Fixture revision and selected case IDs:
Selection rationale and unchanged controls:
Host / version / model / OS:
Skill loading and source verification:
Allowed tools and unavoidable host instructions:
Commands, exit codes, and deterministic results:
Case / repetition / turn / response result / trace result / evidence location:
Failures, blocked or unrun checks, and remaining limitations:
Independent validation task and final candidate identity:
```

Report a failed required check or unavailable required evidence as a merge blocker. Do not erase earlier results, substitute a different host without saying so, or claim broad qualification from this small suite. The private lab remains available for broader compatibility, research, and promotion evidence; its private cases, historical results, and automation stay separate from this public maintenance path.
