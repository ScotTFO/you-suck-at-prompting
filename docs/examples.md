# More prompt interventions

These are synthetic examples, not retained user prompts. They demonstrate how the rewritten prompt changes what an agent may do and what evidence it must return.

## A tiny task gets a receipt

**Original prompt:**

```text
Create a text file named hello.txt containing hello.
```

**Plugin response:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.

You Suck At Prompting Rewritten prompt:

```text
Create hello.txt in the current workspace with text content exactly equal
to hello. Read the file back and report whether its contents match.
```

Prompt performance rating: 4/5 - This prompt knew what it wanted and forgot to ask for a receipt.

Reply with an acknowledgement to use this prompt.

After acknowledgement, the agent creates the file, reads it back, and reports the exact-content check. The rewrite adds a destination and verification without turning five letters into a strategic initiative.

## Production does not accept a casual yes

**Original prompt:**

```text
Deploy the checkout service from the current branch to production.
```

**Plugin response:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.

You Suck At Prompting Rewritten prompt:

```text
Prepare the current branch of the checkout service for a production
deployment. Identify the exact revision, run the existing build and test
checks, and produce a deployment preview that names the target environment
and rollback path. Do not change production. Stop and request separate
explicit approval before executing the deployment.
```

Prompt performance rating: 3/5 - Production was invited before the safety briefing.

Reply with an acknowledgement to use this prompt.

Acknowledging the rewritten prompt authorizes preparation and a deployment preview within existing authority. It does not authorize the production deployment. The rewrite adds an auditable revision, readiness evidence, a rollback path, and a separate approval boundary around the consequential action.

## What changed

| Added to the rewrite | Result |
|---|---|
| Explicit target and preserved behavior | The agent works on the intended surface instead of freelancing. |
| Real verification | Completion includes a test, readback, comparison, or receipt rather than confidence wearing a lanyard. |
| Separate authority boundary | Prompt approval cannot quietly become permission to deploy, publish, purchase, delete, or disclose. |

See [Behavior, safety, and privacy](behavior-and-safety.md) for the full approval and authority contract.
