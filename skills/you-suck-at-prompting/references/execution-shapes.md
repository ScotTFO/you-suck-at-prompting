# Execution design

Read this reference only when the task explicitly proposes or inherently requires iterative feedback, staged checkpoints, parallel or independent work, recurring execution, research, deterministic processing, an experiment, or independent review.

Keep direct work direct. State the user-owned outcome and observable acceptance criteria, then add only the controls that change execution or verification. Execution design shapes the prompt. It does not run tools, create agents or schedules, persist state, or grant authority. Do not require an `Approach:` line or expose these internal categories.

| Selector | Minimum useful instruction |
| --- | --- |
| **DIRECT** | Keep direct work direct. Perform one bounded action followed by its check. |
| **GOAL** | State the user-owned outcome and observable acceptance criteria while leaving implementation choices flexible. |
| **LOOP** — iteration or autonomous retry | Repeat act, check, and correct only when feedback requires another attempt. Define progress evidence, a success exit, a no-progress exit, and a bounded attempt, time, or cost budget. Escalate with the last verified state. A short human-directed revision with an obvious stop condition does not need retry bureaucracy. |
| **PLAN** — staged or consequential work | Use ordered checkpoints. Stop before an irreversible effect or an effect with a separate approval requirement. |
| **GRAPH** — dependency branches | Give each branch isolated ownership or output. Define real dependencies, dependency edges, the join criteria, and one final integrator. |
| **MULTI-AGENT** — independent actors or review | Use independent reasoning only when it materially improves the result. Give each actor isolated ownership or output, and identify an integrator. If review is required, identify an independent reviewer and a blocking or advisory disposition. Do not add a second reviewer just because the task contains the word `review`. |
| **DETERMINISTIC** — mechanical or calculable work | Prefer a script or tool. Define inputs, outputs, error handling, and the verification check. |
| **RESEARCH** — source-backed claims | Retrieve and compare sources, ground claims to them, handle conflicts, and check freshness for changeable facts. |
| **SPIKE** — experiment | Test one narrow hypothesis within a stated budget. Define the pass or fail result that determines the next step. |
| **RECURRING** — scheduled execution | Use durable state, deduplication, schedule and delivery rules, a next check, and closure evidence. A manual conversational loop is not recurring automation. |
| **REVIEW** — independent check | Add an independent reviewer only when it is explicitly required or materially improves confidence. Define whether its disposition blocks the result. |

Controls can compose. For example, independent branches can use a deterministic check, or a staged plan can contain a bounded loop. Keep each control's responsibility distinct and omit any control that does not change the result, safety boundary, or evidence.

## Procedural guides

Read only the selected guide. Each guide adds an executable procedure and an example; it does not create capabilities or approval.

- For iterative work, read [the loop guide](controls/loop.md).
- For dependency branches, read [the graph guide](controls/graph.md).
- For independent actors or maker/checker work, read [the multi-agent guide](controls/multi-agent.md).
- For scheduled rechecks, read [the recurring guide](controls/recurring.md).
