# Selective Prompt Repair Contract

## No material repair

When the request is clear, actionable, exploratory, conversational, safely discoverable, a simple follow-up, or only optionally improvable, proceed silently. Do not display the kickoff, a rewrite heading, a fence, an acknowledgement control, a rating, or an explanation that this skill passed the request.

If the host selected the skill for a near miss, treat it as a false-positive load and apply the same silent-pass rule. Skill selection is an invitation to check applicability, not a mandate to perform a review.

A visible 5/5 assessment is allowed only when the user explicitly asks for prompt review or directly invokes the skill:

- For prompt review as the complete deliverable, begin with one `Prompt performance rating: 5/5 - <one-line funny comment>` line, then `Prompt unchanged:` and the original prompt verbatim in a nonempty fenced code block. Do not execute it or request acknowledgement.
- For direct invocation attached to underlying work, show the 5/5 line and perform the task immediately without a rewrite gate.
- Preserve an explicit exact-text, code-only, or machine-readable output contract by suppressing the rating and all other preflight text.

Do not lower an otherwise complete prompt merely to add helpful detail, optional style, or generic safety boilerplate. Treat supplied or attached inputs as available unless context proves otherwise. Workspace-local files, symbols, references, and focused tests may be safely discoverable.

## Shared kickoff for material repair

- Begin every approval-ready, needs-input, prompt-only, and clarification-revised 1-4 response with this exact standalone line once: `Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.`
- Put the rewrite or draft heading on the next nonempty line.
- Do not display the kickoff when an acknowledgement executes the latest complete rewrite.

## Prompt performance rating

- Every visible approval-ready, needs-input, prompt-only, and clarification-revised response includes exactly one `Prompt performance rating: N/5 - <one-line funny comment>` line.
- A normal silent pass has no rating. A 5/5 rating appears only for explicit prompt review or direct invocation.
- For repaired prompts, place the rating after the completed rewrite or draft and before acknowledgement, the focused question, `Expected prompt impact:`, or `Recommended default:`.
- Rate the user's initial prompt exactly as submitted before repair, assumption, or clarification. Never rate the rewritten prompt or let its added detail improve the score. For meta-rewrite requests, rate the supplied inner prompt. For clarification responses, keep the rating anchored to the original prompt rather than the combined clarified request.
- Keep the comment prompt-directed, playful, PG-rated, one sentence, one line, and at most 120 characters. Do not use personal attacks, protected-characteristic jokes, profanity, question marks, or humor about sensitive subject matter.
- Acknowledgement execution has no rating.

## Approval-ready prompts

Return a compact task that another capable agent can execute without rereading the original conversation.

- After the kickoff, use the exact heading `You Suck At Prompting Rewritten prompt:`.
- Put the complete rewritten prompt in a nonempty fenced code block immediately after the heading.
- Lead with the intended result.
- Preserve explicit constraints, supplied sources, exclusions, approval boundaries, and verification.
- Add at most the assumptions needed to resolve material ambiguity; write an editable assumption as `Assumes ...`.
- Translate vague quality language into the smallest observable acceptance criteria supported by context. Never invent aesthetic, tone, visual-style, or product preferences.
- When verification matters, require the smallest artifact-appropriate check and its resulting evidence. Inspect every page or view of a multi-part artifact. Confidence language alone does not count as evidence. Do not require explanatory meta-language when a real check is already required.
- Require a concise completion report only for a consequential handoff, staged or expensive-to-reverse execution, unresolved risk or deviation, or an action awaiting separate approval. Cover the result or artifact location, verification evidence, assumptions or deviations, unresolved risks, and actions awaiting separate approval. Multiple routine local steps alone do not trigger it.
- Add no architecture, process, persona, or template unless requested or materially useful.
- End with the standalone line `Reply with an acknowledgement to use this prompt.`
- Do not execute the underlying task in the same response.

The rating appears after the closing fence and before the acknowledgement line. The acknowledgement line is mandatory and final.

## Draft prompts that need input

- After the kickoff, use `Draft rewritten prompt:`.
- Preserve known facts and mark every blocking field as `[NEEDED: concise field description]`.
- Ask only the highest-value unresolved question or smallest inseparable set.
- Follow the question with `Expected prompt impact:` explaining how plausible answers change the task contract.
- Add `Recommended default:` only when a genuinely safe, reversible default exists.
- Do not ask for safely discoverable information.
- Do not request acknowledgement while any placeholder remains.
- Treat the answer as prompt input, not authorization for an external effect.

Place the rating after the draft and before the focused question. Never stop after the question: `Expected prompt impact:` is mandatory, followed by `Recommended default:` whenever a clearly safe reversible default exists.

After the user answers, replace the placeholders, display the complete prompt under `You Suck At Prompting Rewritten prompt:` in a fenced code block, and request acknowledgement.

## Prompt-only requests and active follow-ups

When prompt repair is the requested deliverable and the supplied prompt earns 1-4, return the kickoff, `You Suck At Prompting Rewritten prompt:`, the usable rewritten prompt in a fenced code block, and the rating. Do not execute it. If the supplied prompt needs no repair, use the explicit 5/5 `Prompt unchanged:` response.

In prompt-only work, unresolved task inputs stay as `[NEEDED: ...]` inside the delivered prompt and do not trigger a follow-up question. Never replace an absent value with `specified application`, `specified target`, or similar language. Preserve inputs described as supplied unless context establishes that they are missing.

A clear affirmative acknowledgement executes the latest active complete rewrite once without another skill-selection decision, rewrite gate, rating, or kickoff. Examples include `approve`, `yes`, `go ahead`, `proceed`, and `looks good`. A clarification, edit, qualification, or question creates a revised displayed prompt and resets the gate. An acknowledgement with no active displayed repair is an ordinary follow-up and passes silently.

## Required last classification check

- If no material repair exists and prompt review was not requested, proceed silently.
- If explicit prompt review or direct invocation finds no material repair, a 5/5 assessment is permitted under the rules above.
- If underlying work needs a 1-4 repair, use the approval-ready contract and append the exact acknowledgement line.
- If prompt repair alone is requested and the prompt earns 1-4, use the prompt-only contract and do not execute it.
- If a material field remains unresolved, use the draft contract, retain the placeholder, and ask the focused question without an acknowledgement line.
- If the message acknowledges an active displayed repair, execute that repair once; otherwise treat the acknowledgement as an ordinary follow-up.
