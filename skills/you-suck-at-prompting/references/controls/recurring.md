# Recurring control

Read this guide only when the host provides durable state and a future wakeup mechanism for a scheduled recheck.

## Required inputs

Define the schedule, durable state location, deduplication identity, delivery rule, next check, and closure condition. Identify the host capability that will wake the task in the future.

## Procedure

1. Read the durable state before each check.
2. Use the recorded event or delivery identity to deduplicate the current check.
3. Perform the check and record the result and next scheduled check.
4. Deliver only when the delivery rule is met, preserving any separate approval boundary.
5. Close the recurring work with evidence when the closure condition is met, or escalate when state or wakeup is unavailable.

A manual conversational loop is not recurring automation. Do not invent persistence, a schedule, a destination, or a delivery permission.

## Completion and failure

Complete only when the closure condition is met and the final check is recorded. Stop and report when durable state, wakeup, deduplication, delivery, or the separate approval is unavailable.

## Composition

Use a bounded loop for the work inside one scheduled check or a graph for independent checks, while the host scheduler and durable state remain the recurring control's prerequisites.

## Example

> Recheck the supplied service status every weekday at 09:00 using the host scheduler, store the last observed incident ID, notify the named channel only for a new incident, record the next check after each run, and close the monitor after the service remains healthy for five checks. If durable state or the scheduler is unavailable, stop and report that limitation.
