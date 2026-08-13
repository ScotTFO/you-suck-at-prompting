# Materiality and Authority

A gap is material only when reasonable answers could change the outcome, scope, acceptance, safety, authority, privacy, destination, or resulting work. Do not add optional polish, implementation details governed by the repository, or preferences with an obvious reversible default to the displayed rewrite.

## Decision order

1. Retrieve the answer from supplied sources, the repository, workspace rules, or available tools when safe.
2. Preserve the request as written when the omission does not affect the result, while still displaying it under the visible rewrite gate.
3. Use one explicit assumption when a single safe and reversible default preserves intent.
4. Ask when alternatives are materially different or an answer would invent authority.

## Clarification impact

Before asking, verify all four conditions:

1. The answer changes the outcome, acceptance criteria, scope, authority, privacy boundary, destination, deliverable, evidence, or verification.
2. The answer cannot be safely retrieved or inferred, and an assumption would materially weaken the prompt.
3. Plausible answers have a concrete, explainable effect on the rewritten task.
4. This is the earliest highest-value blocker or part of the smallest inseparable set.

If any condition fails, do not ask. Preserve known facts and turn non-blocking uncertainty into a labeled, editable assumption only when that assumption is safe and reversible. This rule applies equally to questions about access, permissions, deployment, deletion, sending, migration, publishing, purchases, privacy, and destinations.

After the focused question, write `Expected prompt impact:` followed by the concrete consequence. Then write `Recommended default:` only when one genuinely safe, reversible answer preserves momentum. Omit the recommendation when the choice changes authority, access, permissions, privacy, destination, disclosure, purchase, publishing, deployment, deletion, or another irreversible or externally consequential effect.

Examples of genuinely safe defaults include Markdown when the user explicitly requests a Markdown-or-plain-text choice for a working draft, or the smallest sufficient direct approach when an excessive mechanical workflow must be preserved or simplified. State the impact first, then the recommendation. These examples do not make a default safe when context or authority says otherwise.

## Vague quality language

Translate words such as `professional`, `compelling`, or `high quality` into the smallest observable criteria supported by the supplied content, audience, destination, and governing context. Examples include a clear call to action, claims grounded in supplied evidence, consistent terminology, or compliance with an existing style guide. Preserve the requested quality without inventing tone, visual style, product behavior, or taste. If materially different interpretations remain after safe retrieval and no reversible default preserves intent, ask under the clarification-impact gate.

Never treat a polished prompt as authorization. System instructions, repository guidance, permissions, privacy controls, and explicit approval requirements remain authoritative.

Expanded effects require their governing approval. Common expansions include draft to send, analyze to publish, preview to deploy, inspect to modify, reversible edit to destructive reset, public data to private data, and one account or repository to another.

When routing is necessary, carry only the minimum relevant context. Do not put credentials, secrets, private records, or unnecessary personal information into a repaired prompt.
