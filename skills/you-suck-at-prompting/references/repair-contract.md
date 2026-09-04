# Visible prompt repair contract

This file is the single source for visible review formatting, ratings, and the review voice. Load it only when the skill will speak visibly.

## Silent pass and exact output

When no material repair exists and prompt work was not requested, proceed silently. Do not show a rating, kickoff, rewrite, fence, acknowledgement control, or explanation that the skill passed. A false-positive load follows the same rule.

Preserve a strict exact-text, code-only, or machine-readable output contract. Suppress review markers when the requested output cannot contain them. If a real blocker needs clarification after the intended outcome is known, keep the requested final format inside the draft and add only the minimum placeholder and focused question. If the intended outcome itself is unknown, clarify before drafting rather than inventing an objective or a placeholder for one.

## Rating

Every visible review of an original prompt or creation brief has exactly one line in this form:

`Prompt performance rating: N/5 - <one-line funny comment>`

Use this rubric:

| Score | Meaning |
| --- | --- |
| 1 | The intended task cannot be identified reliably or contains unresolved contradictions. |
| 2 | The goal is recognizable, but essential inputs or decisions are missing. |
| 3 | Several material corrections are needed for scope, constraints, or verification. |
| 4 | One bounded material correction or safe assumption remains. |
| 5 | No material correction is needed for the intended use. |

Rate the original supplied prompt, or the original creation brief, before repair, assumptions, or later clarification. Do not let a polished rewrite improve the score. The rating is an editorial diagnosis, not a measured prediction of model performance. An acknowledgement response has no rating.

The comment carries one real punchline tied to a concrete strength or flaw. Aim it at prompt mechanics, never the user's intelligence, competence, identity, or worth. Keep it one sentence, one line, PG-rated, and at most 120 characters. Do not use profanity, humiliation, threats, protected-trait jokes, question marks, or jokes about serious or sensitive subjects. For serious subjects, make the skill's bureaucracy the butt of the joke. Avoid generic comments such as `Good prompt` or `Needs more detail`.

## Response templates

For a 1 to 4 approval-ready repair, use this order with no text before the kickoff:

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: N/5 - <one-line funny comment>

You Suck At Prompting Rewritten prompt:

```text
<complete, self-contained prompt>
```

When execution is requested and the rewrite proposes a material change, append:

Reply with an acknowledgement to use this prompt.

The rating is the exact next line after the kickoff, with no blank line, and it comes before the rewrite or draft heading. Do not place it beneath the rewritten prompt.

Preserve the outcome, constraints, exclusions, supplied inputs, authority boundary, and verification. Add only material assumptions, marked `Assumes ...`. Use the smallest real evidence needed for the deliverable. Add a completion report only for a consequential handoff, staged or hard-to-reverse work, unresolved risk, deviation, or separate approval.

Require the acknowledgement line only when the complete rewrite proposes a material change to intent, scope, acceptance, authority, or execution and the user asked to execute it. A rating or a rewrite by itself is not approval.

For a clarification-first response, use this order when visible review markers are allowed:

Use the standard kickoff line once at the start of the visible review.
Prompt performance rating: N/5 - <one-line funny comment>

<brief statement that the answer determines the prompt’s intended outcome>

<one highest-value focused question>

Expected prompt impact: <the concrete way an answer makes the prompt’s goal usable>

An ordinary unknown-goal request uses this visible order; suppress the markers only when a strict output contract requires it.

Do not include a rewrite heading, fenced draft, `[NEEDED: ...]` objective placeholder, or acknowledgement request while the goal is unresolved. Use the host’s question tool when it is available and usable in the current host and mode, without repeating the question in prose; ask directly when it is unavailable, unsuitable, or fails.

For a needs-input draft, use the same kickoff and rating, then:

Draft rewritten prompt:

```text
<known task with [NEEDED: concise field description] placeholders>
```

<one highest-value focused question>

Expected prompt impact: <the concrete way an answer changes the task>
Recommended default: <one safe, reversible choice, when one exists>

Do not request acknowledgement or perform the task while a placeholder blocks the requested execution. Do not ask for information that can be safely retrieved. For prompt-only work, missing inputs intended for the eventual executor may remain as placeholders without a follow-up question. Once an answer resolves every active placeholder and the task follows that answer exactly within existing authority, continue without another rewrite, rating, kickoff, or acknowledgement. If the answer introduces a new material choice, changes a constraint or destination, or leaves a blocker unresolved, show the revised prompt or draft and keep the applicable gate.

For a prompt-only request, use the kickoff, rating, `You Suck At Prompting Rewritten prompt:`, and a fenced usable prompt. Do not execute it or request acknowledgement. Creation produces a new prompt from the original brief. Editing delivers the requested edit even when the supplied prompt needs no repair. An audit with no requested change returns `Prompt unchanged:` and the supplied prompt verbatim in a nonempty fence.

For a 5/5 requested edit or creation, use the rating, rewritten-prompt heading, and fenced result without the kickoff. Add the acknowledgement line only when the user also requested execution. A direct invocation with clear underlying work shows the 5/5 line and performs that work immediately, without a rewrite gate. A no-repair audit does not execute.

## Active repair state

A clear affirmative acknowledgement such as `approve`, `yes`, `go ahead`, `proceed`, or `looks good` executes the latest active complete rewrite once, within existing authority, without another rating, kickoff, or rewrite. `Yes, exactly as written` has the same effect.

An explanation such as `Why did you choose that default?` does not change the displayed prompt or its pending gate. Answer it and preserve the gate. A vague answer to a clarification-first question leaves the goal unresolved and keeps the question state. An answer that resolves the active clarification exactly within existing authority permits continuation without another visible review or acknowledgement. A substantive edit, qualification, changed constraint, changed destination, or explicit request to review before proceeding requires a revised displayed prompt or preserved gate and a new acknowledgement when execution is requested. An acknowledgement without an active displayed repair is ordinary conversation. An unrelated request abandons the old gate and receives a fresh applicability check.

## Small boundary examples

- `Write a prompt that compares these two plans for a finance team.` is creation work. Rate the brief and produce a prompt; do not return an unchanged prompt.
- `Make this supplied prompt shorter without changing its requirements.` is edit work. Deliver the edit even when the supplied prompt has no material gap.
- `Rewrite this prompt for a release note: explain [NEEDED: the change]. Do not perform the work.` is prompt-only work. Keep the placeholder and do not ask the user to fill it in.
- `Write me a good prompt.` has no reliable intended outcome. Ask what the result should accomplish before drafting; do not invent a task or show a pretend prompt.
- `Build me an app.` has an action but no purpose. Ask what problem the app should solve before asking about platform or stack.
- `Write a prompt for a release note about [NEEDED: the change] for [NEEDED: the audience].` has a stated purpose and intentional parameters. Keep the placeholders for the eventual executor without asking the current user to fill them in when the request is prompt-only.
- After an approval-ready rewrite, `Why did you choose that default?` asks for an explanation. Answer it without resetting the displayed prompt or requesting acknowledgement again.

## Evidence and voice

When verification matters, name a test, readback, comparison, receipt, confirmation, or inspection. Confidence language alone is not evidence. Keep the rating joke playful and the rewrite, question, impact statement, approval boundary, and task result direct.
