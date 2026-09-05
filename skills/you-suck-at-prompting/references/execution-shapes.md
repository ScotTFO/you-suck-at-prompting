# Execution design

Load when iteration, dependencies, independent actors, or scheduled work materially shapes a requested prompt. Keep direct work direct. Preserve the user's supported method and add only controls that change execution or verification.

| Condition | Read | Responsibility |
| --- | --- | --- |
| Feedback determines another attempt | [Loop](controls/loop.md) | Success, progress, and a bounded stop rule |
| Branches have dependencies and a joined result | [Graph](controls/graph.md) | Readiness, separate outputs, and join criteria |
| Independent reasoning or maker/checker separation is required | [Multi-agent](controls/multi-agent.md) | Bounded assignments, independent findings, and integration |
| Work must wake up again later | [Recurring](controls/recurring.md) | Scheduler prerequisites, durable state, deduplication, and closure |

Read only guides needed for the task. Dependencies do not automatically require multiple agents; independent reviewers do not automatically require a dependency graph. Multiple controls may compose when their responsibilities remain distinct. Do not repeat the same budget, approval rule, or reporting template in every branch.

For sequential work, state the useful checkpoints. For mechanical work, prefer a deterministic operation and a check. For research, require sources and freshness where relevant. For an experiment, name the hypothesis, budget, and decisive observation. These do not need extra guide loads or a visible taxonomy.

Guidance shapes the prompt. It does not launch tools, agents, schedules, or persistent state. A prompt for a future host can name necessary capabilities; current execution must use capabilities actually available and permitted. Do not replace the user's method merely because a simpler method is possible.
