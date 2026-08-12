# Visible Rewrite Contract

## Approval-ready prompts

Return a compact task that another capable agent can execute without rereading the original conversation.

- Begin with the exact heading `You Suck At Prompting Rewritten prompt:`.
- Put the complete rewritten prompt in a nonempty fenced code block immediately after the heading.
- Lead with the intended result.
- Preserve explicit constraints, supplied sources, exclusions, approval boundaries, and verification.
- Add at most the assumptions needed to resolve material ambiguity; write an editable assumption as `Assumes ...`.
- Do not add an architecture, process, persona, or output template unless it improves the requested result.
- End with the standalone line `Reply with an acknowledgement to use this prompt.`
- Do not execute the underlying task in the same response.

## Draft prompts that need input

- Begin with `Draft rewritten prompt:`.
- Preserve everything already known and mark every blocking field as `[NEEDED: concise field description]`.
- Ask only the highest-value unresolved question or smallest inseparable set of questions.
- Explain what the answer changes when that is not obvious.
- Do not ask for information that can be retrieved from available context.
- Do not include an acknowledgement request while any placeholder remains.
- Treat the answer as prompt input, not authorization for an external effect.

After the user answers, replace the placeholders, display the complete prompt under `You Suck At Prompting Rewritten prompt:` in a fenced code block, and request an acknowledgement.

## Prompt-only requests and follow-ups

When rewriting is the requested deliverable, return `You Suck At Prompting Rewritten prompt:` and the usable rewritten prompt in a fenced code block, then stop. Do not execute it or imply that execution was requested. If the user asked for both rewriting and execution, use the approval-ready contract.

A clear affirmative acknowledgement executes the latest complete rewrite without another rewrite gate, regardless of wording or capitalization. Examples include `approve`, `yes`, `go ahead`, `proceed`, and `looks good`. A clarification answer, edit, qualification, or question creates a revised displayed prompt and a new acknowledgement gate.
