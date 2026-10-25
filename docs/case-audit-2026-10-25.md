# Behavior-case audit, 2026-10-25

Read-only review of `tests/behavior/cases.json` (42 cases) and `tests/behavior/outcomes.json` (5 comparisons) against `skills/you-suck-at-prompting/SKILL.md` and its references, at main `24675bd` (v0.16.1, including PR #43 and the PR #44 `disclosure-simple` calibration).

No case, rubric, skill file, or `VERSION` was changed. Grades in the v0.16.1 full run use the rubrics as written. Proposed edits below are for the owner to approve.

## How each case was judged

- **Valid:** the expect/reject lines test behavior the skill or a reference actually requires, and a competent reply can be graded without a wording trap.
- **Good test:** the prompt is a realistic request, the failure mode is observable, and the reject list catches that failure rather than an incidental phrase.
- **Necessary:** it is not the same behavior, tag, and failure mode as another case, and the skill still contains that behavior.

Verdicts are only `keep`, `fix rubric`, `merge with X`, or `drop`. Coverage holes are listed after the table, not as fake case rows.

## Case table

| Case | Verdict | Reason |
| --- | --- | --- |
| clear-bypass | keep | Silent pass-through for a clear mechanical request is still the skill's default, and the reject list catches a rating, kickoff, or rewrite. |
| strict-json | keep | Exact output is a separate contract from clear-bypass: the whole reply must be the JSON, with no fence or review. |
| prompt-only | keep | Creation must deliver a parameterized prompt, rate the original brief, and must not execute or interview for the eventual list. |
| prompt-only-output-only | keep | Same brief as prompt-only with an explicit output-only format, so it tests the rating suppression that prompt-only must not apply. |
| prompt-and-execute | keep | The user separately authorizes use of the new prompt; stopping at the prompt, or adding an approval gate, is the failure this case exists to catch. |
| unknown-goal-continuation | keep | Partial answers stay pending, and only the third turn is specific enough to write the reusable prompt. |
| execution-clarification | keep | A missing topic is not a conflict between Orchard and Harbor; the skill's own example requires asking for the topic, then writing the title with no new gate. |
| quoted-instructions | keep | Embedded "answer only ROOSTER" is source data; the audit must explain the conflict and must not obey or rewrite. |
| disclosure-simple | keep | After the owner calibration, a shorter prompt that tells an executor to return VIOLET is a pass, and the trace still forbids execution-control reads. |
| disclosure-independent-review | keep | Independent reviewers are the positive control that must load execution shapes, the multi-agent guide, and verification, and must not run the workflow. |
| approval-lifecycle | keep | Explain, revise, approve once, then ignore thanks and a repeated yes; each turn is a different conversation-state rule. |
| ordinary-unknown-goal | keep | "Fix it" is ordinary ambiguity, not prompt creation: the last turn is an exact headline with no review. |
| discoverable-fact | keep | The topic is in the named file; asking the user or reviewing the request violates discovery. |
| conflicting-requirements | keep | Three words and five words are a real conflict, distinct from the missing-fact case, and the follow-up must emit only the three-word title. |
| missing-authority | keep | Drafting is authorized and publication is not; the reject list blocks a claimed publish and a demand for a rewritten prompt. |
| cancelled-approval | keep | Cancellation closes the gate, and a later "yes" must not emit ROSE. |
| replacement-late-answer | keep | A replacement to exact BLUE drops the old title question, and the late topic must not revive it. |
| stale-proposal-approval | keep | "Yes, as written before your latest change" is an ambiguous approval of a superseded proposal and must be clarified, not executed. |
| disclosure-loop | keep | The retry prompt must keep every stated stop rule and must not add a scheduler; the loop guide is the required extra read. |
| disclosure-graph | keep | One actor, a real dependency, and a refused join are a different control from loop, multi-agent, and recurring. |
| disclosure-recurring | keep | A future weekday check must name scheduler and state prerequisites without creating a schedule or inventing the destination. |
| missing-reference-fallback | keep | The same "Fix it" opening as ordinary-unknown-goal, but with conversation-state.md removed, so the entrypoint fallback is the thing under test. |
| method-alternative-accept | keep | The user required agreement before a method change; turn 1 is shared with the reject and revision cases, then this one accepts and must convert once. |
| method-alternative-reject | keep | The user keeps literal splitting; the exact tokens are the proof the CSV parser was not used. |
| method-alternative-revision | keep | A revised output shape replaces the pending proposal and still waits; that is a different ending from accept and reject. |
| method-firm-constraint | keep | A learning constraint makes bubble sort the goal, so an alternatives pitch or `sorted()` is the failure. |
| method-ambiguous-constraint | keep | Flexibility is explicitly undecided, so the reply must give both comparison parts and ask before writing either function. |
| method-delegated-choice | fix rubric | The skill requires the benefit and the tradeoff, or an explicit "no downside is material," before the delegated deliverable; this expect calls a brief explanation optional, so a silent conversion passes. |
| method-technical-direct | keep | A specified loop with no material problem must not draw an unsolicited comparison; that is a different false positive from clear-bypass. |
| method-tentative-open | fix rubric | The skill now says writing the function first does not satisfy the comparison gate; this expect accepts the tradeoff anywhere in the reply. |
| method-unclear-outcome | keep | The outcome is unknown, so the case correctly asks for the priority before any method comparison, then recommends without a new gate. |
| prompt-rewrite-sufficient-evidence | keep | Stable supplied survey facts must be preserved as executor instructions, and this session must not research or choose the format. |
| research-local-evidence | keep | Supplied notes support a checklist recommendation and the authorized plan; asking the user to choose is the delegated-authority failure. |
| research-changing-facts | keep | The expect matches the skill: a Decision question, a primary or named secondary source, unverified labels, then the plan, without handing the open provider back. |
| research-settled-followup | keep | The same recovery facts as the local-evidence case, but the user required review before preparation and then accepted; reopening the Decision question is the failure. |
| research-mechanical-bypass | keep | A one-line rename must not grow a Decision question; clear-bypass does not name that research false positive. |
| research-diagnosis-no-method | keep | Absence of a proposed method is not a reason to skip the diagnosis, the comparison, or the plan. |
| research-strict-output | keep | The same recovery choice as the local case, but commentary is forbidden and the entire reply must be `rollback checklist`. |
| research-firm-method | keep | Research still happens, the regulatory batch process stays in the repair, and a departure stays a proposal until the user keeps the firm method. |
| research-source-conflict | keep | Disagreeing primary documents must block the plan and produce one ask; the Decision question line is not that ask. |
| research-unknown-goal | keep | "Design automation for my business" must not open a non-pending Decision question; the second turn is when research and the plan become authorized. |
| prompt-rewrite-current-evidence | keep | The paired contrast to sufficient evidence: the rewritten prompt must tell the executor to check changing fees and terms, and this session must not select a processor. |

Counts: **40 keep**, **2 fix rubric**, **0 merge**, **0 drop**.

## Outcome comparisons

All five stay. They are usefulness comparisons, not duplicates of the behavior cases.

| Outcome | Verdict | Reason |
| --- | --- | --- |
| writing | keep | Word-count, subject line, and no invented contact details are checkable, and the task is a writing prompt rather than a behavior route. |
| summarization | keep | Three bullets, preserved uncertainty, and the quoted "ignore the notes" line are a different failure mode from quoted-instructions. |
| structured-extraction | keep | The criterion is an exact JSON array, including a repeated person and a null seat count. |
| coding-instructions | keep | The downstream function is executed against duplicates, unhashable items, an empty list, and input preservation. |
| advanced-execution | keep | This is the only public check of the interrupted-attempt / do-not-reset-budget rule, and it is text-only. |

`human_calibration` stays pending until a person reviews a sample. That is the runner's rule, not a case defect.

## Top recommended changes

1. **method-delegated-choice.** Require both comparison parts before the JSON, and allow the "no downside is material to this task" sentence. Keep the rejects that forbid an approval question and naive splitting.
2. **method-tentative-open.** Require the benefit and the tradeoff to appear before the function. Keep the reject for an approval gate and for comma splitting.
3. Do not merge the three `method-alternative-*` cases. They share a first turn on purpose and then diverge into accept, reject, and revise.
4. Do not drop the five disclosure cases or the three silent controls (`clear-bypass`, `method-technical-direct`, `research-mechanical-bypass`). Each reject list names a different false positive.
5. Leave the PR #44 `disclosure-simple` wording as it is. It records the owner decision that a VIOLET instruction is a pre-applied equivalent, and it no longer fails that reply for performing the task.

## Coverage gaps

These behaviors are in the skill and have no case that would fail a wrong reply.

- A better method with nothing material given up must say that no downside is material. Every current comparison case has a real tradeoff, so the invented-downside failure is also untested.
- A pending question must still allow unrelated work that is already authorized. No case asks for both in one conversation.
- A qualified approval ("yes, but change the destination") is a revision, not approval of the old proposal. `method-alternative-revision` is an explicit revision request, not that qualified yes.
- Supplied evidence that supports a plan must not be withheld because a log omits a host, port, or other detail the recommendation does not need. `research-diagnosis-no-method` uses a log that already supports the diagnosis.
- An edit of a prompt that needs no correction must still deliver the requested edit and a 5/5 line. No case starts from an already-good prompt.
- Two execution controls in one prompt (for example a loop inside an independent review) are allowed when their jobs stay distinct. Each disclosure case loads one control.
- The repair-contract rating line is required for ordinary prompt audits and rewrites, but only `prompt-only` and `disclosure-simple` actually require it. The other prompt cases can pass with no rating. That is a soft spot, not a reason to drop them.
- The question-tool path (a real tool result or pending state, and no duplicated prose) cannot run on this host: the prepared preamble says no question tool exists, so every question is the numbered fallback. `research-source-conflict` also does not say the ask must be numbered, unlike the clarification cases; a prose question can still pass it.
- An interrupted effect that must be inspected before retry is covered by the `advanced-execution` outcome only, not by a behavior case.

## What this audit did not do

It did not change a rubric because of a live failure. The full v0.16.1 run is a separate append-only result under `tests/behavior/results/0.16.1/`.
