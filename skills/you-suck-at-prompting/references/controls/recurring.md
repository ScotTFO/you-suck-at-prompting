# Recurring control

Load for a prompt describing scheduled rechecks or other future wakeups.

Identify the executor's scheduler, schedule and timezone, durable state location, deduplication identity, delivery destination and rule, next check, and closure condition. Do not invent missing destinations or delivery permission. A future-executor prompt may leave these as explicit prerequisites or parameters.

At each authorized run, read the prior state, check for a new event, record the result and next check, and deliver only when the rule is met. Deduplicate repeated observations and deliveries. Close with recorded evidence when the closure condition is satisfied. Report unavailable state, wakeup, or delivery capability instead of pretending the schedule exists.

Example: check a supplied service every weekday at 09:00 in the named timezone, record incident IDs, notify the authorized destination only for a new incident, and close after five healthy checks.

Bound retries inside each check separately from the schedule. A conversational loop is not a scheduler. Writing this prompt does not register a task, grant permission, or persist state.
