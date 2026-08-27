# Behavior, safety, and privacy

You Suck at Prompting is a selectively loaded prompt-repair skill, not an execution engine. It shapes a task only when prompt review is requested or a material problem could change the work. Host policies, permissions, tools, and authority boundaries remain controlling.

## Selective activation

Supported agent harnesses can select a skill when a request matches its description. This package describes both positive and negative applicability. Installation compatibility and live behavioral certification are reported separately.

- Load for explicit prompt writing, rewriting, critique, clarification, audit, or quality review.
- Load for material ambiguity, conflicting constraints, missing authority, unclear scope or destination, missing success criteria, or an execution design that could change the outcome.
- Load for programming requests that may create or change repository-tracked files when task isolation is missing, unsafe, or unknown.
- Do not load for clear, actionable, exploratory, conversational, or safely discoverable requests; read-only programming; work outside Git; simple follow-ups; acknowledgements without an active repair; minor wording issues; or optional improvements.

Selection is host-controlled and may be imperfect. The skill repeats the applicability check after loading. A false-positive load passes silently when no material repair exists.

## Response paths

- **Silent pass:** A clear or safely discoverable request proceeds with no rating, kickoff, rewrite, or skill commentary.
- **Explicit 5/5 review:** A visible 5/5 assessment appears only for explicit prompt review or direct invocation. Prompt-only review returns the unchanged prompt without executing it.
- **Approval-ready repair:** A materially flawed but complete request receives a visible rewrite and waits for acknowledgement.
- **Needs input:** An unresolved material field appears as `[NEEDED: ...]`; the skill asks the minimum focused question and explains its impact.
- **Prompt-only repair:** When the deliverable is the prompt itself, the skill returns a usable rewrite without executing it.
- **Active acknowledgement:** `yes`, `approve`, `go ahead`, `proceed`, or `looks good` executes the latest displayed complete rewrite once without another audit.
- **Ordinary acknowledgement:** The same words without an active repair are normal conversation and do not trigger the skill.

A clarification, edit, or qualification revises the displayed prompt and resets its acknowledgement gate. An unrelated request abandons the old gate and receives a new applicability check.

Every visible 1-4 rewrite or draft puts one `Prompt performance rating: N/5 - ...` line immediately below the kickoff and before the rewrite heading. The score judges the initial prompt before repair. Its position makes that target visible. Clarification can improve the task without retroactively improving the original score.

That rating line carries one real punchline. The voice is slightly brutal and playful, but the joke targets prompt mechanics, never the person. Generic comments such as `Needs more detail` fail the personality contract. Serious and sensitive subjects get dry plugin self-deprecation instead of jokes about the subject.

## Materiality and execution shaping

A gap is material only when reasonable answers could change the outcome, scope, acceptance, safety, authority, privacy, destination, or resulting work. The skill retrieves safely discoverable facts before asking and does not manufacture repair from optional polish.

## Programming and Git isolation

Programming is treated as a context, not a blanket trigger. Feature work, fixes, refactors, migrations, upgrades, code generation, and tracked code, configuration, test, or infrastructure changes may need isolation. Planning, review, explanation, diagnosis, and test execution without tracked changes remain read-only passes.

For a tracked mutation, the skill performs a read-only preflight covering the repository root and bare state, branch or detached state, tracked and untracked status, registered worktrees, a usable base or default ref, and applicable repository rules. It repeats the check for each repository in a multi-repository request and never opens credential files or copies untracked secrets.

The rewrite makes one location choice visible: reuse an existing task-specific branch or linked worktree; use a dedicated branch in the current checkout for a clean bounded solo change or clearly related dirty changes; use a branch-backed linked worktree when dirty ownership is unrelated or unclear, another task is active, work is parallel, the coordinator is bare, or the change is high risk. A host-managed isolated detached worktree is reused as-is. A non-Git directory is not initialized. If Git context is unavailable, the rewrite embeds this read-only preflight and decision rule. If dirty ownership or a usable base is unclear, it asks one focused question with concrete impact.

Branch or worktree creation waits for acknowledgement. The skill never grants authority to stash, reset, clean, overwrite, move existing edits, commit, push, merge, rebase, delete, or publish.

When a task genuinely needs a feedback loop, staged plan, dependency graph, multiple agents, recurring checks, research, deterministic processing, a spike, or independent review, the repair adds only the controls needed to keep work bounded and verifiable. Direct work stays direct.

Execution shaping does not create agents, schedules, persistence, permissions, or host capabilities.

## Approval and authority

Acknowledging a rewritten prompt authorizes only that prompt within authority already granted by the user, host, repository, and governing policies. It does not create permission to:

- publish, send, or disclose information;
- purchase or schedule anything;
- deploy to an environment;
- delete data;
- change permissions or access; or
- bypass repository or organizational rules.

Consequential effects retain their own explicit approval gates. A polished prompt is not a forged permission slip.

## Privacy and package operation

This skill creates no additional destination for prompts. Normal processing by the selected harness still applies.

The skill runtime has no telemetry.

The distributed skill has:

- one Markdown runtime;
- no prompt-submission hook;
- no always-on Copilot instruction adapter;
- no MCP server;
- no external service;
- no runtime telemetry;
- no credential requirement; and
- no automatic modification of global instructions.

Because there is no hook or adapter, the skill does not receive a second copy of each submitted prompt or run an auxiliary process on submission. The selected host reads the skill instructions as part of its normal customization flow. The external `skills` installer collects anonymous installation telemetry by default; set `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` during installation to opt out. See the [installation guide](installation.md) for lifecycle commands.

## Retention and repository boundary

Real usage prompts are never retained automatically. The exact phrase `SAVE CASE` begins a separate redacted-preview workflow; confirmation authorizes retention of the redacted case only, not the underlying task or publication.

The public repository contains only the distributable skill, documentation, package-contract tests, and validation automation. Behavioral evaluation data and maintainer automation remain outside the public package. Your installation does not arrive with a directory named `totally-not-telemetry` because even the joke would be suspicious.

The runtime contract in [`SKILL.md`](../skills/you-suck-at-prompting/SKILL.md) is authoritative if this explanation ever drifts.
