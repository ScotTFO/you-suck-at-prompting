# Repair Contract

## Rewritten prompts

Return a compact task that another capable agent can execute without rereading the original conversation.

- Lead with the intended result.
- Preserve explicit constraints, supplied sources, exclusions, approval boundaries, and verification.
- Add at most the assumptions needed to resolve material ambiguity.
- Use `Assumes ...` for an editable assumption when one matters.
- Do not add an architecture, process, persona, or output template unless it improves the requested result.
- Do not execute the underlying task unless the user explicitly requested rewrite and execution and then approved the rewrite.

## Clarification questions

Ask only the highest-value unresolved question or the smallest inseparable set of questions.

- Explain what the answer changes when that is not obvious.
- Recommend a safe default when one would preserve momentum.
- Do not ask for information that can be retrieved from available context.
- Do not turn optional preferences into blockers.
- Treat the answer as the missing input, not as authorization for a separate side effect.

Prefer one consequential question over a checklist of optional preferences.
