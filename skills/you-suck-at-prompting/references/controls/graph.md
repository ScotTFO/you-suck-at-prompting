# Graph control

Load when branches have real dependencies and must join into one result.

Name each branch's inputs and isolated output, its dependency edges and readiness condition, the join criteria, and one final owner. Start only ready branches. Record failures and skipped branches explicitly. Join only after every required branch passes its acceptance check; the final owner resolves conflicts and verifies the combined result.

Example: produce a validated table, let the narrative branch use its accepted schema, then have an editor join the separate outputs only after both checks pass. An unresolved branch failure blocks that join.

Use a loop inside a branch only when feedback requires it. Dependencies do not create parallel capacity or require additional agents. One actor may execute the graph; simple sequential work can stay a short ordered list.
