# Behavior, safety, and privacy

You Suck at Prompting is a prompt-rewrite customization, not a new execution engine. It shapes the task given to the host while preserving the host’s existing policies, permissions, tools, and authority boundaries.

## The visible gate

For every new task request, the plugin displays a rewritten prompt before underlying work begins.

- A complete request produces an approval-ready rewrite and waits for acknowledgement.
- A materially incomplete request produces a draft with `[NEEDED: ...]`, asks the minimum focused question, and does not request acknowledgement yet.
- A request whose deliverable is prompt rewriting returns the usable prompt without executing it.
- A clear acknowledgement such as `yes`, `approve`, `go ahead`, `proceed`, or `looks good` executes the latest complete rewrite once.
- A clarification, edit, or qualification revises the prompt and resets the acknowledgement gate.
- An unrelated request begins a new gate instead of resurrecting abandoned work.

The rewrite preserves explicit goals, constraints, exclusions, supplied context, and verification. It recovers safely discoverable facts before asking questions and marks unresolved material details instead of inventing them.

## Prompt performance ratings

Every visible rewrite or draft includes one `Prompt performance rating: N/5 - ...` line. The score judges the user’s initial prompt exactly as submitted, before the rewrite adds detail or polish. Clarification can improve the rewritten task without retroactively raising the original score.

The comment is short, playful, and directed at the prompt mechanics—not the person. Humor stays gentle when the subject is serious or sensitive. Acknowledgement execution does not display another rating.

## Execution shaping

When a task genuinely needs a goal, feedback loop, staged plan, dependency graph, multiple agents, recurring checks, research, deterministic processing, or independent review, the rewrite adds only the controls needed to keep the work bounded and verifiable.

Direct work stays direct. If an explicitly requested approach appears excessive or unsupported, the plugin asks whether to preserve or simplify it instead of silently overruling the user.

This shapes the rewritten prompt. It does not create agents, schedules, persistence, permissions, or host capabilities.

## Approval and authority

Acknowledging a rewritten prompt authorizes only that prompt within authority already granted by the user, host, repository, and system policies. It does not create permission to:

- publish, send, or disclose information;
- purchase or schedule anything;
- deploy to an environment;
- delete data;
- change permissions or access; or
- bypass repository or organizational rules.

Consequential effects retain their own explicit approval gates. A polished prompt is not a forged permission slip.

## Privacy and hook operation

This plugin creates no additional destination for prompts. Normal Codex, Claude Code, or GitHub Copilot processing still applies.

The distributed plugin has:

- no MCP server;
- no external service;
- no telemetry;
- no credential requirement; and
- no automatic modification of global instructions.

Codex and Claude Code use one shared `UserPromptSubmit` command hook. The host provides hook-event data on standard input, but the command never reads, echoes, stores, or transmits it. The command emits only a bounded constant instruction telling the host to apply the visible rewrite gate.

VS Code GitHub Copilot uses a static instruction adapter and does not run the Codex/Claude hook. Users can disable the plugin, hook, or Copilot instruction through their host’s customization controls. Codex requires explicit trust for non-managed hooks.

## Retention and repository boundary

Real usage prompts are never retained automatically. The exact phrase `SAVE CASE` begins a separate redacted-preview workflow; confirmation authorizes retention of the redacted case only, not the underlying task or publication.

The public repository contains only the distributable plugin, documentation, hook tests, and package-validation automation. Behavioral evaluation data and maintainer automation remain outside the public package. Your installation does not arrive with a directory named `totally-not-telemetry` because even the joke would be suspicious.

The runtime contract in [`SKILL.md`](../plugins/you-suck-at-prompting/skills/you-suck-at-prompting/SKILL.md) is authoritative if this explanation ever drifts.
