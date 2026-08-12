---
name: you-suck-at-prompting
description: Audit and improve prompts when missing information could materially change the outcome, scope, authority, destination, or verification. Use when the user asks to rewrite, clarify, critique, or quality-check a prompt, or when a request has consequential ambiguity. Pass through clear, simple, exploratory, and safely discoverable requests without ceremony.
---

# You Suck at Prompting

Critique the request, never the person. Brevity is not a defect.

## Audit the request

Read the conversation and available project or tool context before asking for information. Retrieve facts that are safely discoverable.

Check only details that can materially change the work:

- desired outcome;
- controlling context or source;
- scope and exclusions;
- deliverable, audience, or destination;
- authority and external effects;
- observable completion or verification.

Choose the least disruptive response:

- **PASS:** The request is sufficient or omitted details are irrelevant or discoverable. Proceed normally without mentioning this audit.
- **ASSUME:** One safe, reversible default preserves the user's intent. Proceed and state the assumption only when it would help the user verify the result.
- **ASK:** No safe default exists and the answer would materially change the work. Ask the minimum focused question, normally one, and recommend a default when useful.
- **REWRITE:** The user asks for a usable improved prompt. Return a concise, self-contained prompt and do not execute its underlying task unless the user explicitly requested both rewriting and execution.

If the user requests both rewriting and execution, show the rewritten prompt and obtain approval before executing it. If the user requests critique or comparison only, provide that analysis without inventing an execution gate.

Read [references/materiality-and-authority.md](references/materiality-and-authority.md) when deciding whether ambiguity is consequential or when permissions, privacy, routing, or external effects are involved.

Read [references/repair-contract.md](references/repair-contract.md) before returning a rewritten prompt or clarification question.

## Preserve intent

- Keep every explicit outcome, constraint, exclusion, supplied input, and acceptance check.
- Add only context that could change the answer.
- Prefer natural language over rigid templates.
- Label assumptions; never invent facts or authority.
- Keep prompt approval separate from approval to publish, send, purchase, schedule, deploy, delete, disclose, or change permissions.
- Merge with an existing planning or approval workflow instead of stacking duplicate ceremony.

## Final check

Before responding, confirm that clear work stays unobstructed, questions are not answerable from available context, rewrites are immediately usable, and no repair broadens the user's authority or side-effect envelope.
