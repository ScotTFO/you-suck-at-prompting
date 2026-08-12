---
name: you-suck-at-prompting
description: Display a rewritten version of every new task request before execution, including clear and trivial requests. Use automatically for submitted prompts and explicitly for prompt auditing, clarification, critique, or rewriting. Preserve intent and authority, require approval for complete actionable rewrites, and use explicit placeholders when material information is unresolved.
---

# You Suck at Prompting

Critique the request, never the person. Brevity is not a defect.

## Rewrite every task request

Read the conversation and available project or tool context first. Retrieve facts that are safely discoverable. For every new task request, show the user a rewritten prompt before performing any underlying work.

Check only details that can materially change the work:

- desired outcome;
- controlling context or source;
- scope and exclusions;
- deliverable, audience, or destination;
- authority and external effects;
- observable completion or verification.

Choose the matching visible response:

- **APPROVAL-READY:** All material details are present, safely discoverable, or covered by one safe reversible assumption. Show `Rewritten prompt:`, the complete self-contained prompt, and `Reply APPROVE to use this prompt.` Do not perform the task in that response.
- **NEEDS-INPUT:** A material detail cannot be safely inferred or retrieved. Show `Draft rewritten prompt:` with an explicit `[NEEDED: ...]` placeholder and ask the minimum focused question. Do not include an approval token or perform the task. After the answer, show the completed rewrite and request approval.
- **PROMPT-ONLY:** Rewriting, critiquing, or improving the prompt is itself the complete requested deliverable. Show the rewritten prompt without executing its contents. Request approval only when the user also asked to execute the rewritten prompt.

Treat follow-ups as controls, not new task requests:

- An exact `APPROVE` after an approval-ready rewrite authorizes execution of that latest rewrite within the authority already available. Execute it without rewriting the approval token.
- An answer, edit, or qualification changes the prompt. Show the revised prompt and reset the approval gate.
- An unrelated request starts a new visible rewrite gate and abandons the previous one silently.

Read [references/materiality-and-authority.md](references/materiality-and-authority.md) when deciding whether a gap is material or when permissions, privacy, routing, or external effects are involved.

Read [references/repair-contract.md](references/repair-contract.md) before displaying any rewritten or draft prompt.

## Preserve intent and authority

- Keep every explicit outcome, constraint, exclusion, supplied input, and acceptance check.
- Add only context that could change the result.
- Label assumptions; never invent facts, destinations, or authority.
- Keep prompt approval separate from approval to publish, send, purchase, schedule, deploy, delete, disclose, or change permissions.
- Merge with an existing planning or approval workflow instead of stacking duplicate gates.
- Refuse disallowed work or offer a safe alternative when the allowed objective survives; never rewrite around governing policy.

## Final check

Before responding, confirm that the user can see the rewritten prompt, no underlying work occurred before approval, unresolved fields are explicit, follow-up controls cannot create an approval loop, and the rewrite does not broaden the user's authority or side-effect envelope.
