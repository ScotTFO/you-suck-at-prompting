# Execution Design

Read this reference only when the task explicitly proposes or inherently requires iterative, staged, parallel, recurring, research-heavy, deterministic, experimental, or independently reviewed execution.

## Operating rule

Keep direct work direct. Select the fewest controls that preserve the requested outcome, acceptance checks, safety boundaries, and required independence. Treat the controls as composable dimensions, not as a mandatory single label.

Execution design shapes the rewritten prompt; it does not run tools, create agents or schedules, persist state, or grant authority. Host capabilities and governing instructions remain controlling.

Preserve an appropriate explicit approach. If an explicit approach appears excessive or the host cannot support it, use **NEEDS-INPUT** and ask whether to preserve the requested approach or simplify it. Do not silently substitute an approach, and do not request acknowledgement while the choice remains unresolved.

Do not require an `Approach:` line or expose internal shape labels. Put only material execution controls into the rewritten prompt.

## Controls

- **GOAL:** Define the user-owned outcome and observable acceptance criteria while leaving implementation choices flexible. A goal is an outcome contract, not authority or permission to continue indefinitely.
- **DIRECT:** Perform one bounded action followed by its check.
- **LOOP:** Repeat act, check, and correct only when feedback must determine another attempt.
- **PLAN:** Stage dependent, consequential, or expensive-to-reverse work behind ordered checkpoints and explicit approval boundaries.
- **GRAPH:** Coordinate genuinely independent branches through explicit dependencies and join semantics.
- **MULTI-AGENT:** Use independent reasoning-heavy actors or maker/checker separation when that independence materially improves the result.
- **DETERMINISTIC:** Prefer a script or tool for mechanical, repeatable, or calculable work.
- **RESEARCH:** Retrieve, compare, synthesize, and ground time-sensitive or source-backed claims.
- **SPIKE:** Test one uncertain assumption cheaply before committing to full implementation.
- **RECURRING:** Recheck on a schedule only when durable state and a future wakeup mechanism exist.
- **REVIEW:** Add independent review when it is explicitly required or materially improves confidence.

## Required controls

- A loop requires progress evidence, a success exit, a no-progress exit, a bounded iteration, time, or cost budget, and escalation with the last verified state. State all five controls in the rewrite; do not compress them into a generic instruction to retry until success.
- A plan requires ordered checkpoints and must stop before irreversible or separately approved effects.
- A graph requires real dependency edges, explicit join criteria, and one final owner.
- Multi-agent work requires independent reasoning or maker/checker separation, isolated ownership or outputs, and one explicitly identified integrator or join owner. Agent count alone is not a reason to use multiple agents.
- Deterministic work requires defined inputs, outputs, error handling, and a verification check.
- Research requires source retrieval, claim-to-source grounding, conflict handling, and freshness checks for changeable claims.
- A spike requires a narrow hypothesis, a budget, and a pass/fail decision that determines the next step.
- Recurring work requires durable state, deduplication, schedule and delivery rules, a next check, and closure evidence. Do not describe a manual conversational loop as recurring automation.
- Review requires an independent reviewer and a clear blocking or advisory disposition.

When controls compose, keep their responsibilities distinct. For example, a goal may use a bounded loop, independent branches may join through one integrator, and a deterministic check may supply loop progress evidence. Do not add another control unless it changes execution or verification.
