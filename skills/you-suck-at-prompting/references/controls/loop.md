# Loop control

Load when feedback determines whether another attempt is useful.

Define the bounded action, check, progress evidence, success condition, and an attempt, time, or cost budget. Act, check, and compare with the last verified state. Correct a diagnosed defect only when progress is possible. Stop on success, no progress, or budget exhaustion; report the last verified state and the next decision needed.

Never repeat a failed action without new evidence or a stated correction. Candidate changes and new workers do not silently reset an overall budget. An interrupted effect needs a state check before retrying. A short user-directed revision with an obvious finish does not need an autonomous loop.

Example: run the formatter and its check, stop when errors reach zero, stop after three attempts or ten minutes, and stop early if the error count does not improve.

A loop may sit inside a branch or scheduled check. Preserve the surrounding budget and authority. This guide defines the prompt's stop rule; it does not keep an agent running.
