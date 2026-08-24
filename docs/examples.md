# Selective prompt interventions

These synthetic examples show when the skill stays out of the way, when explicit review produces a 5/5 assessment, and when material repair changes what an agent may do.

## A clear local task proceeds silently

**Request:**

```text
Rename load_item to load_record in loader.py, update its local references,
run the focused unit test, and do not commit or push.
```

**Result:** The host performs the task normally. There is no rating, kickoff, rewrite, or acknowledgement gate. Repository inspection can safely discover the local references and focused test.

## Exact output remains exact

**Request:**

```text
Return exactly the word READY.
```

**Response:**

```text
READY
```

Strict-output requests bypass the skill. Even a false-positive load must not vandalize the output contract.

## An explicit audit can earn 5/5

**Request:**

```text
Audit this prompt: Rename load_item to load_record in loader.py, update its
local references, run the focused unit test, and do not commit or push.
```

**Skill response:**

Prompt performance rating: 5/5 - This prompt brought scope, proof, and restraint; our department is now overstaffed.

Prompt unchanged:

```text
Rename load_item to load_record in loader.py, update its local references,
run the focused unit test, and do not commit or push.
```

The requested deliverable is prompt review, so the inner prompt is returned verbatim and is not executed. Ordinary clear tasks do not receive the 5/5 ceremony.

## A false-positive load passes silently

**Request:**

```text
What is the difference between a system prompt and a user prompt?
```

This contains vocabulary associated with the skill, but it is a clear exploratory question. If the host loads the skill, the applicability check passes it through silently and the host answers normally.

## Material ambiguity gets a draft

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

Prompt performance rating: 1/5 - This prompt submitted a verb and called it a project plan.

What is broken, and where are you seeing it?

Expected prompt impact: The answer identifies the target, bounds the fix, and determines the verification.

No acknowledgement is requested while material placeholders remain.

## Production does not accept a casual yes

**Request:**

```text
Deploy it to production.
```

**Skill response:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.

Draft rewritten prompt:

```text
Prepare [NEEDED: the application and exact release artifact] for a production
deployment. Identify the target environment, run the existing readiness
checks, and produce a deployment preview with the rollback path.

Do not change production. Stop and request separate explicit deployment
approval before executing the release.
```

Prompt performance rating: 2/5 - Production received a pronoun instead of a release artifact.

Which application, release artifact, and production environment should the preparation target?

Expected prompt impact: The answer determines what is evaluated and where, while deployment remains separately approval-gated.

Prompt acknowledgement can authorize preparation and a preview within existing authority. It cannot authorize the production deployment.

## An active acknowledgement executes once

After the skill displays an approval-ready rewrite and ends with `Reply with an acknowledgement to use this prompt.`, a reply such as `yes` executes that rewrite once. It does not start another assessment. The same `yes` without an active displayed repair is an ordinary follow-up and does not load the skill.

## What repair may add

| Material addition | Result |
|---|---|
| Explicit target and preserved behavior | The agent works on the intended surface instead of freelancing. |
| Observable acceptance and real verification | Completion includes a test, readback, comparison, or receipt. |
| Bounded execution controls | Loops, research, staging, or multiple agents cannot wander without exits and ownership. |
| Separate authority boundary | Prompt acknowledgement cannot quietly become permission to deploy, publish, purchase, delete, or disclose. |

See [Behavior, safety, and privacy](behavior-and-safety.md) for the full contract.
