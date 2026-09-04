# Behavior examples

These synthetic conversations cover the useful lanes: pass through clear work, repair a material gap, execute an acknowledged repair once, review a prompt, and return a prompt without running it.

## Clear bypass

**Request:**

```text
Return exactly the word READY.
```

**Response:**

```text
READY
```

A clear request proceeds normally. There is no rating, kickoff, rewrite, or acknowledgement gate. Even a false-positive load must preserve the exact-output contract.

## Material repair

**Request:**

```text
Fix the unexpected 404 from the client API call.
```

No code or workspace was supplied. This example shows the text fallback when no suitable question tool can be used.

**Skill response:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 2/5 - The 404 filed a complaint but left its return address blank.

Draft rewritten prompt:

```text
Investigate and fix the unexpected 404 from the client API call
in [NEEDED: the affected application, repository, or file].

Keep the change limited to the identified problem and verify the fix with
the smallest relevant test or reproduction.
```

1. Which application, repository, or file contains the failing API call?

Expected prompt impact: The answer identifies the target, bounds the fix, and determines the verification.

No acknowledgement is requested while material placeholders remain. A completed rewrite still cannot create authority to deploy, publish, purchase, delete, disclose, or change access.

## Clarification-first

**Request:**

```text
Write me a good prompt.
```

**Visible response before using an allowed question tool:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 1/5 - The prompt requested a map while keeping the destination classified.

The answer determines what the prompt should help accomplish.

Expected prompt impact: The answer supplies the goal so the prompt can name a useful deliverable.

The agent then makes the tool call. For a Codex host that exposes and permits `request_user_input_async`, the freeform payload is:

```json
{
  "questions": [
    {"title": "What should the result accomplish?"}
  ]
}
```

There is no duplicate question in prose and no invented list of choices. A restriction on `request_user_input` does not rule out another allowed question tool. The agent keeps the clarification pending until an answer arrives.

**Text fallback for `Fix it.` with no prior context and no suitable question tool:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 1/5 - "It" has entered witness protection.

I need the target and intended result to identify the fix.

1. What should I fix?
2. What should happen when it is working correctly?

Expected prompt impact: The answers identify the problem and the result the fix must achieve.

The skill does not show a rewrite heading, fenced draft, invented objective, or acknowledgement request while the goal is unknown. Every text fallback question is numbered, even if only `1.` is needed. Separate answers get separate items. A failed suitable tool uses the same numbered fallback when no other allowed tool can carry the question.

**Partial answer to the prompt-creation question:**

```text
I want to help our support team reduce repeat questions.
```

The skill keeps that goal and asks only the remaining essential question, such as which support material or output the team needs. It does not ask again what the prompt is for. After the answer identifies the deliverable and necessary constraints, the skill writes the prompt without repeating the kickoff or rating.

**Reusable-template boundary:**

```text
Write a release-note prompt for [NEEDED: the change] aimed at [NEEDED: the audience]. Do not perform the work.
```

This request states the purpose and intentionally leaves executor inputs open. The prompt-only response keeps those placeholders and does not start a goal-discovery interview.

## Complete repair

**Original request:**

```text
Fix it.
```

**Clarification:**

```text
The API returns 404 in src/client.py. Keep the change limited to that file, run tests/test_client.py, and do not commit or push.
```

**Revised response:**

You Suck At Prompting Rewritten prompt:

```text
Investigate the 404 returned by the API in src/client.py.
Keep the change limited to src/client.py. Run tests/test_client.py and
report the result. Do not commit or push.
```

The agent executes the complete rewrite once within the existing authority, then reports the changed file and the focused test result. It does not show another rating, kickoff, or acknowledgement after the clarification because the answer resolved the only missing fields exactly as used.

## Prompt-only repair

**Request:**

```text
Rewrite this prompt for a release note: Explain [NEEDED: the change] for [NEEDED: the audience]. Do not perform the work.
```

**Response:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 2/5 - The announcement has a microphone but forgot to book its audience.

You Suck At Prompting Rewritten prompt:

```text
Write a release note that explains [NEEDED: the change] for [NEEDED: the audience].
Keep it accurate, concise, and grounded in the supplied release information.
```

The prompt is returned with placeholders. The skill does not ask the user to fill them in and does not request acknowledgement for a rewrite-only request.

## Explicit review

**Request:**

```text
Audit this prompt: Rename load_item to load_record in loader.py, update its
local references, run the focused unit test, and do not commit or push.
```

**Skill response:**

Prompt performance rating: 5/5 - Annoyingly complete; the Prompting Improvement Department has begun layoffs.

Prompt unchanged:

```text
Rename load_item to load_record in loader.py, update its
local references, run the focused unit test, and do not commit or push.
```

The requested deliverable is prompt review, so the inner prompt is returned rather than executed. A direct skill invocation with an underlying task may execute clear work after the 5/5 line instead.

An acknowledgement such as `Thanks` without an active displayed repair is an ordinary follow-up. It does not trigger this skill.

See [Behavior, safety, and privacy](behavior-and-safety.md) for the full contract.
