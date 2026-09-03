# Graph control

Read this guide only when independent branches have real dependencies and must be joined into one result.

## Required inputs

Name each branch's isolated ownership or output, the dependency edges, the condition that makes a branch ready, the join criteria, and one final owner.

## Procedure

1. Start only branches whose dependencies are satisfied.
2. Keep each branch's inputs and outputs explicit and isolated.
3. Record branch failure without silently treating it as success.
4. Join only when every required branch meets its acceptance condition.
5. Have the named final owner resolve conflicts, verify the joined result, and report any branch that was skipped or failed.

Do not use a graph for sequential work that one actor can complete directly. A graph organizes dependencies; it does not create agents, parallel capacity, or approval.

## Completion and failure

Complete when every required branch meets its acceptance condition and the final owner verifies the joined result. If a branch fails, is skipped, or cannot reach its join condition, stop the join and report that state.

## Composition

Use a bounded loop or deterministic check inside a branch when it changes that branch's acceptance evidence. Combine with staged work only when the final owner preserves every separate approval boundary.

## Example

> Have the data branch produce a validated table and the narrative branch produce a source-linked summary. The narrative waits for the table schema, both outputs remain separate, the integrator joins them only after both acceptance checks pass, and the integrator owns the final consistency check. If either branch fails, report the failure and do not publish the combined result.
