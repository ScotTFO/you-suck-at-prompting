# Multi-agent control

Read this guide only when independent reasoning or maker/checker separation materially improves the result.

## Required inputs

Define why independence matters, each actor's bounded assignment, the isolated output or ownership boundary, the handoff format, and one integrator or final reviewer.

## Procedure

1. Give each actor a distinct question, artifact, or check.
2. Prevent one actor from silently replacing another actor's evidence.
3. Pass only the output needed for the next actor's assignment.
4. Have the integrator reconcile differences against the acceptance criteria.
5. Record whether the final disposition is blocking or advisory and who owns it.

Agent count alone does not justify this control. One mechanical change with one local check should remain direct. A checker must be independent of the maker's reasoning or evidence.

## Completion and failure

Complete when every bounded assignment returns its required output and the integrator reconciles it against the acceptance criteria. If an assignment is missing or the integrator cannot resolve a conflict, report the blocking state and stop.

## Composition

Use a graph when assignments have dependencies, a loop when one actor needs bounded correction, or a deterministic check when an output is mechanical. Omit this control when one actor can supply the needed independent check directly.

## Example

> Ask one analyst to extract claims and a separate checker to verify each claim against the supplied source. Keep their outputs separate, give both the same acceptance criteria, and have the named integrator resolve disagreements and record whether any discrepancy blocks the result.
