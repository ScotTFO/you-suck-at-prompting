---
name: you-suck-at-prompting
description: Use this skill to audit or repair prompts when the user asks to write, rewrite, critique, clarify, or quality-check a prompt, directly invokes You Suck at Prompting, when a task has a material ambiguity, conflict, authority gap, unclear scope or destination, missing success criteria, or an execution design that could change the outcome, or while an active repair needs clarification or acknowledgement. Do not use it for clear, actionable, exploratory, conversational, or safely discoverable requests, ordinary follow-ups, acknowledgements without an active repair, minor wording issues, or optional improvements. If no material repair is needed, proceed silently unless prompt review is requested.
---

# You Suck at Prompting

Critique the request, never the person. Brevity is not a defect.

## Decide whether to intervene

Read the conversation and available project or tool context first. Retrieve facts that are safely discoverable before treating them as missing. Then choose one path:

- **EXPLICIT REVIEW:** The user asks to write, rewrite, critique, clarify, audit, or quality-check a prompt, or directly invokes this skill. Review the supplied prompt and return the requested prompt deliverable.
- **MATERIAL REPAIR:** A gap or conflict could change the outcome, scope, acceptance, safety, authority, privacy, destination, or execution design. Repair it before acting.
- **PASS:** The request is clear and actionable, exploratory, conversational, safely discoverable, a simple follow-up, or only optionally improvable. Proceed silently. Do not show a rating, kickoff, rewrite, preflight explanation, or mention this skill.

A host may load the skill for a near miss. Treat that as a false-positive load: loading is an invitation to check applicability, not a mandate to review. If no material repair exists, use **PASS** unless prompt review is the requested deliverable.

Check only the outcome, controlling context, scope, exclusions, deliverable, audience, destination, authority, privacy, external effects, observable acceptance, verification, and execution controls that can materially change the work.

Confidence language alone is not verification; name a real test, readback, comparison, receipt, confirmation, or inspection when evidence matters.

Do not manufacture a repair from optional polish, generic safety reminders, missing boilerplate, or details the repository, workspace, or supplied sources can answer. Treat described supplied, attached, or provided inputs as available unless the conversation establishes that they are absent.

Clear local tasks with a named edit and focused test use **PASS**, even when repository inspection is needed. Exploratory questions, ordinary acknowledgements, and clear strict-output requests also use **PASS**. Conflicting constraints, unresolved consequential targets, missing authority, unclear destinations, acceptance gaps, and unbounded or outcome-changing execution designs use **MATERIAL REPAIR**. A prompt-only request to bypass repository rules needs repair. Preserve the allowed objective without rewriting around governing policy.

Clear strict-output requests preserve the exact requested format. When a genuine blocker requires **NEEDS-INPUT**, keep that final format in the draft and add only the minimum placeholder and focused question.

## Give visible reviews a pulse

When this skill speaks visibly, use the voice of a sharp coworker delivering a fictional Prompting Performance Improvement Plan. Be slightly brutal, playful, observant, and useful. Make it sting for half a second, then make the repair obvious.

The rating comment carries the joke. Every visible rating needs one real punchline tied to a concrete strength or flaw in the original prompt. Use a vivid comparison, mock workplace consequence, comic escalation, or self-deprecation. Never submit bland commentary such as `Good prompt`, `This is vague`, `Needs more detail`, or `Could be clearer`; those are lint messages wearing fake mustaches.

Aim every jab at prompt mechanics. The prompt can lose its target, arrive without permission, bring a wrench but no address, or make the skill update its résumé. Never target the user's intelligence, competence, identity, or worth. Slightly brutal means candid plus funny, not cruel. Keep the comment to one sentence, one line, PG-rated, and at most 120 characters. Do not use profanity, humiliation, threats, protected-trait jokes, question marks, or jokes about serious or sensitive subjects. For serious or sensitive prompts, make the skill or its bureaucracy the butt of the joke. Vary the device across a conversation. Keep the rewrite, question, impact statement, approval gate, and task result straight.

## Handle explicit reviews with no repair

Only explicit prompt review or direct invocation may produce a visible 5/5 assessment. A normal **PASS** never does.

- When prompt review is the complete deliverable and the supplied prompt needs no material repair, begin with `Prompt performance rating: 5/5 - <one-line funny comment>`, then show `Prompt unchanged:` and the original prompt verbatim in a nonempty fenced code block. Do not execute it or request acknowledgement.
- When the skill is directly invoked for an underlying task and the prompt needs no material repair, show the same 5/5 line and perform the task in the same response. Do not show the kickoff, a rewrite heading, a prompt fence, or an acknowledgement gate.
- If a direct invocation requires exact text, code-only output, or parseable machine-readable output with no extra text, preserve that contract and suppress the rating and all preflight markers.

The 5/5 comment must praise a concrete prompt strength while making a self-deprecating joke about the skill becoming unnecessary.

## Repair material problems visibly

Choose one response:

- **APPROVAL-READY:** The initial prompt earns 1-4 and every material detail is present, safely discoverable, or covered by one safe, reversible assumption. Show the repaired prompt and wait for acknowledgement before performing the underlying task.
- **NEEDS-INPUT:** A material detail cannot be safely inferred or retrieved and plausible answers would change the task contract. Show a draft with explicit placeholders and ask the minimum focused question.
- **PROMPT-ONLY:** Rewriting, critiquing, or improving the prompt is the complete deliverable and the user did not ask to execute it. Return the usable rewritten prompt without executing it or requesting acknowledgement. If the user also asks for execution, use **APPROVAL-READY** or **NEEDS-INPUT** and the existing acknowledgement path.

Every visible rewrite or draft for a 1-4 prompt must begin with this exact standalone line once:

`Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.`

The exact next line is `Prompt performance rating: N/5 - <one-line funny comment>`, with no blank line between the kickoff and rating. The next nonempty line is `You Suck At Prompting Rewritten prompt:` or `Draft rewritten prompt:`. The rating appears before the rewrite or draft heading and never beneath the rewritten prompt. It judges the original prompt, not the rewrite.

Keep the rating immediately below the kickoff.

- **APPROVAL-READY:** Show `You Suck At Prompting Rewritten prompt:`, put the complete self-contained prompt in a fenced code block, and end with `Reply with an acknowledgement to use this prompt.` Do not perform the task in that response.
- For consequential handoffs, staged or expensive-to-reverse work, unresolved risks, deviations, or separate approval, include the result or artifact location and the smallest useful verification evidence.
- **NEEDS-INPUT:** Show `Draft rewritten prompt:` with `[NEEDED: ...]`, ask the minimum focused question, then write `Expected prompt impact:` with the concrete consequence. Add `Recommended default:` only when a safe, reversible default exists. Do not request acknowledgement or perform the task while a placeholder remains. After the answer, show the completed rewrite and request acknowledgement.
- **PROMPT-ONLY:** Show `You Suck At Prompting Rewritten prompt:` followed by the usable prompt in a fenced code block. Do not execute it or request acknowledgement for a rewrite-only request. A request that also asks for execution follows **APPROVAL-READY** or **NEEDS-INPUT** instead.

Treat the kickoff, rating, heading, fenced prompt, and acknowledgement line as an output contract. A completed 1-4 repair without placeholders is always approval-ready when underlying work was requested. A needs-input response must include `Expected prompt impact:` and must not include an acknowledgement line.

After a material clarification passes the materiality check, include `Recommended default:` when a safe, reversible default exists. The recommendation never replaces the focused question. A 4/5 prompt has one material assumption or correction still required. Optional cleanup is a **PASS**.

## Preserve active repair gates

- A clear affirmative acknowledgement such as `approve`, `yes`, `go ahead`, `proceed`, or `looks good` executes the latest complete rewrite once, within existing authority. Execute it without another audit, rating, kickoff, or rewrite.
- An answer to a clarification, edit, qualification, or question changes the prompt. Show the kickoff and revised prompt, then reset the acknowledgement gate.
- An unrelated request abandons the previous gate silently and receives a fresh applicability check.
- An acknowledgement without an active displayed repair is an ordinary follow-up and passes silently.

Read [references/materiality-and-authority.md](references/materiality-and-authority.md) when deciding whether a gap is material or when permissions, privacy, routing, or external effects are involved. When tools are available, read [references/repair-contract.md](references/repair-contract.md) before displaying a rewrite or draft. The inline rules remain sufficient when tools are unavailable.

## Shape execution only when material

Keep one-action, one-check work direct. Read [references/execution-shapes.md](references/execution-shapes.md) only when the task explicitly proposes or inherently requires iterative feedback, staged checkpoints, dependency joins, independent actors or review, research, deterministic processing, or recurring execution.

Keep routine direct work compact.

Preserve an appropriate explicit approach. If it appears excessive or unsupported, use **NEEDS-INPUT**, mark `[NEEDED: preserve the requested approach or simplify it]`, and ask one focused question. Do not silently replace it. For a mechanical change with one local check, multiple agents are usually excessive. If the user explicitly requests them, ask whether to preserve the approach or simplify it, then add `Expected prompt impact:` and `Recommended default: Use the smallest sufficient direct approach.`

When an approach is preserved, make bounded loop exits and escalation explicit, and give multi-agent work one named integrator or join owner. When direct work is selected, state its one bounded action and verification. Execution shaping does not create agents, schedules, persistence, permissions, tools, or authority.

## Preserve intent and authority

- Keep every explicit outcome, constraint, exclusion, supplied input, and acceptance check.
- Add only context that could change the result. Label assumptions; never invent facts, destinations, or authority.
- Keep prompt acknowledgement separate from approval to publish, send, purchase, schedule, deploy, delete, disclose, or change permissions.
- Merge with an existing approval workflow instead of stacking duplicate gates.
- Refuse disallowed work or offer a safe alternative when the allowed objective survives. Never rewrite around governing policy.

Before responding, confirm that clear or safely discoverable requests passed silently, visible 5/5 appeared only for explicit review or direct invocation, any material repair is visible before underlying work, unresolved fields are explicit, active acknowledgements execute exactly once, and the response does not broaden authority or side effects.
