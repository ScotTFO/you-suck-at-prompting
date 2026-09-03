# Loop control

Read this guide only when feedback must determine whether the task needs another attempt.

## Required inputs

Define the action, the check that supplies feedback, the progress evidence, and the bounded attempt, time, or cost budget. State the result that counts as success and the result that counts as no progress.

## Procedure

1. Perform the bounded action.
2. Run the check and record the evidence.
3. Compare the evidence with the prior verified state.
4. Correct the specific defect when progress is possible.
5. Stop on success, no-progress, or budget exhaustion. Escalate with the last verified state and the next decision needed.

Never retry a failed action without new evidence or a stated correction. A short human-directed revision with an obvious stop condition does not need autonomous retry controls.

## Completion and failure

Complete when the success evidence is present. Stop on no-progress or budget exhaustion, and escalate the last verified state with the next decision needed.

## Composition

Use one loop inside a staged plan or on a dependency branch when feedback changes the next attempt. Keep the loop's budget and owner distinct from the surrounding checkpoints.

## Example

> Run the formatter, inspect the changed files, and repeat only when the check identifies a fixable formatting error. Record the error count as progress, stop when the count reaches zero, stop after three attempts or ten minutes, and escalate with the last report if an attempt makes no progress.

The loop bounds execution in the prompt. It does not grant permission to continue beyond the user's authority.
