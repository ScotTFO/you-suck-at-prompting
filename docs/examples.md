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
Fix it.
```

**Skill response:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 1/5 - The prompt brought a verb, but left the target hiding behind the filing cabinet.

Draft rewritten prompt:

```text
Investigate and fix [NEEDED: the specific failure or undesired behavior]
in [NEEDED: the affected application, repository, or file].

Keep the change limited to the identified problem and verify the fix with
the smallest relevant test or reproduction.
```

What is broken, and where are you seeing it?

Expected prompt impact: The answer identifies the target, bounds the fix, and determines the verification.

No acknowledgement is requested while material placeholders remain. A completed rewrite still cannot create authority to deploy, publish, purchase, delete, disclose, or change access.

## Clarification-first

**Request:**

```text
Write me a good prompt.
```

**Skill response when a question tool is available:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 1/5 - The prompt requested a map while keeping the destination classified.

The answer determines what the prompt should help accomplish.

The skill uses its question tool to ask: What should the result accomplish, and who will use it?

Expected prompt impact: The answer supplies the goal and audience so the prompt can name a useful deliverable.

The skill does not show a rewrite heading, fenced draft, invented objective, or acknowledgement request while the goal is unknown. If the question tool is unavailable, unsuitable for the current mode, or fails, it asks the same question directly in the conversation and does not claim a tool call.

**Partial answer:**

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

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 1/5 - The original prompt brought a verb, but left the target hiding behind the filing cabinet.

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
