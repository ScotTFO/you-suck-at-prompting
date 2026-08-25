# Three representative behaviors

These synthetic examples cover the skill’s three useful lanes: stay out of the way, repair a material problem, and review a prompt when review is the requested deliverable.

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

Draft rewritten prompt:

```text
Investigate and fix [NEEDED: the specific failure or undesired behavior]
in [NEEDED: the affected application, repository, or file].

Keep the change limited to the identified problem and verify the fix with
the smallest relevant test or reproduction.
```

Prompt performance rating: 1/5 - This prompt filed a verb, lost the target, and still requested expedited handling.

What is broken, and where are you seeing it?

Expected prompt impact: The answer identifies the target, bounds the fix, and determines the verification.

No acknowledgement is requested while material placeholders remain. A completed rewrite still cannot create authority to deploy, publish, purchase, delete, disclose, or change access.

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
Rename load_item to load_record in loader.py, update its local references,
run the focused unit test, and do not commit or push.
```

The requested deliverable is prompt review, so the inner prompt is returned rather than executed. Ordinary clear tasks do not receive the 5/5 ceremony.

See [Behavior, safety, and privacy](behavior-and-safety.md) for the full contract.
