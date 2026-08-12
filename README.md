# You Suck at Prompting

An installable Codex and Claude Code plugin that visibly rewrites every task request, preserves its intent and authority boundaries, and waits for approval before execution.

The joke stays in the name. The skill critiques the prompt, never the person.

## Install for Codex

```powershell
codex plugin marketplace add ScotTFO/you-suck-at-prompting
codex plugin add you-suck-at-prompting@scottfo
```

Review and trust the plugin hook when Codex prompts you. In Codex CLI, use `/hooks` to inspect and trust the exact command. Start a new Codex task after installation or upgrade so the current skill and hook are loaded.

Upgrade with `codex plugin marketplace upgrade scottfo`, then run `codex plugin add you-suck-at-prompting@scottfo` and start a fresh task.

## Install for Claude Code

```powershell
claude plugin marketplace add ScotTFO/you-suck-at-prompting
claude plugin install you-suck-at-prompting@scottfo
```

Use `/hooks` to inspect the installed `UserPromptSubmit` hook. Start a new Claude Code session after installation or upgrade. Upgrade with `claude plugin marketplace update scottfo`, then run `claude plugin update you-suck-at-prompting@scottfo`.

## Use

Every new task request receives the same visible rewrite gate before the harness acts, including requests that are already clear or trivial. A complete rewrite ends with `Reply APPROVE to use this prompt.` and no underlying work occurs until that exact approval.

When material information cannot be safely recovered, the skill displays `Draft rewritten prompt:` with explicit `[NEEDED: ...]` placeholders and asks the minimum focused question. Answers revise the displayed prompt; an exact `APPROVE` executes the latest complete rewrite instead of starting another gate.

Invoke `$you-suck-at-prompting` explicitly in Codex or `/you-suck-at-prompting:you-suck-at-prompting` in Claude Code to display a rewrite on demand. Model-driven implicit invocation remains a best-effort fallback when the hook is disabled or unavailable.

## Privacy and permissions

This plugin contains one shared skill and one shared `UserPromptSubmit` command hook that each harness discovers through its native plugin contract. Codex and Claude Code provide hook-event data on standard input, but the hook command does not read, echo, store, or transmit the submitted prompt; it prints only a constant visible-gate instruction. The plugin has no MCP server, external service, telemetry, credential requirement, or automatic modification of global instructions.

The Claude manifest intentionally uses default `hooks/hooks.json` discovery. Declaring a second hook path would make Claude merge both definitions and run the preflight twice.

Users can inspect and disable plugin hooks; Codex additionally requires explicit trust for non-managed hooks. Installing or trusting this plugin does not grant authority to send, publish, purchase, schedule, deploy, delete, disclose information, or change permissions.

## Repository boundary

This repository contains only the distributable plugin, its documentation, hook tests, and package-validation CI. Behavioral evaluation data and maintainer automation are not distributed with the plugin.

## License

MIT
