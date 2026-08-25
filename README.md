<h1 align="center">You Suck at Prompting</h1>

<p align="center">
  <strong>Your prompt is not always in trouble. We checked the policy.</strong><br>
  A selective performance review for requests that could actually change the outcome.
</p>

<p align="center">
  <img alt="Prompting status: review when material" src="https://img.shields.io/badge/prompting_status-review_when_material-ff4d4d?style=for-the-badge">
  <img alt="Standard agent skill" src="https://img.shields.io/badge/package-standard_agent_skill-6f42c1?style=for-the-badge">
  <img alt="Skill runtime telemetry: none" src="https://img.shields.io/badge/skill_runtime_telemetry-none-2ea44f?style=for-the-badge">
</p>

> [!WARNING]
> **“Fix it.” has been placed on a PIP.** Clear requests may continue working without supervision.

## Install

You need Node.js 22.20 or newer for installation and updates. The installed skill itself is plain Markdown and does not need Node.js.

### Project

```text
npx skills@latest add ScotTFO/you-suck-at-prompting
```

### Global

```text
npx skills@latest add ScotTFO/you-suck-at-prompting --global
```

The installer detects available harnesses and lets you choose where the skill goes. For CI, explicit harness selection, pinned releases, removal of older native plugins, and systems that need `--copy`, use the [complete installation and migration guide](docs/installation.md).

> [!IMPORTANT]
> Already installed the old Codex, Claude Code, or VS Code Copilot plugin? Remove it first. Two copies produce two tiny managers, and neither accepts shared accountability.

The [`skills` CLI](https://github.com/vercel-labs/skills) can install this standard skill for every harness it currently supports. Release verification explicitly checks Codex, Claude Code, GitHub Copilot, and Hermes destinations. Behavioral certification is reported separately from installation compatibility.

## Exhibit A: a verb arrives without adult supervision

**Before:**

```text
Fix it.
```

**After:**

```text
Investigate and fix [NEEDED: the specific failure or undesired behavior]
in [NEEDED: the affected application, repository, or file].

Keep the change limited to the identified problem and verify the fix with
the smallest relevant test or reproduction.
```

The skill asks what is broken and where. It does not request acknowledgement while material placeholders remain. Once the missing facts are supplied, it shows the complete repair and waits before execution. HR keeps the original 1/5 rating for training purposes.

## What earns a meeting

| Request | Result |
|---|---|
| “Rename `load_item` to `load_record` in `loader.py` and run the focused unit test.” | Proceeds silently. Local details are safely discoverable. |
| “What does `git rebase` do?” | Proceeds silently. Exploratory questions are not misconduct. |
| “Improve this prompt: …” | Loads because prompt review is the requested work. |
| “Deploy it.” | Loads because the target and authority are material. |
| “Thanks.” | Proceeds normally unless it acknowledges an active displayed rewrite. |

The host uses the skill description to decide whether to load it. The skill then checks applicability again. A near miss passes through silently, with no rating, kickoff, rewrite, or surprise annual review.

## The performance contract

- Preserve the user’s goal, scope, constraints, voice, and explicit choices.
- Recover safely discoverable facts before calling them missing.
- Repair only material problems that could change the result.
- Give every visible review one slightly brutal, playful punchline aimed at the prompt mechanics. Beige feedback goes back to training.
- Ask one focused question when a required decision is still unknown.
- Keep prompt acknowledgement separate from permission to publish, deploy, purchase, delete, disclose, schedule, or change access.
- Never create tools, agents, persistence, schedules, or authority the host did not already provide.

Direct invocation requests a visible review. In Codex, use `$you-suck-at-prompting`. Other harnesses expose installed skills through their own skill interface.

## Privacy reviewed the clipboard

The skill runtime has no telemetry, MCP server, hook, credential requirement, external service, or always-on instruction file. Normal processing by the selected host still applies.

The external `skills` installer collects anonymous telemetry by default. Set `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` while running it to opt out. See the [installation guide](docs/installation.md) for shell-specific examples.

## The filing cabinet

- [Installation, migration, updates, removal, and smoke tests](docs/installation.md)
- [Three representative behaviors](docs/examples.md)
- [Behavior, safety, privacy, retention, and repository boundaries](docs/behavior-and-safety.md)
- [Canonical skill runtime](skills/you-suck-at-prompting/SKILL.md)

MIT licensed. No clear prompts were detained during this review.
