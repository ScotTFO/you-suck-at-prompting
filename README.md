# You Suck at Prompting

An installable Codex plugin that privately preflights every submitted prompt, catches consequential ambiguity, repairs prompts without changing their intent, and stays out of the way when a request is already clear.

The joke stays in the name. The skill critiques the prompt, never the person.

## Install

```powershell
codex plugin marketplace add ScotTFO/you-suck-at-prompting
codex plugin add you-suck-at-prompting@scottfo
```

Review and trust the plugin hook when Codex prompts you. In Codex CLI, use `/hooks` to inspect and trust the exact command. Start a new Codex task after installation or upgrade so the current skill and hook are loaded.

## Use

After the hook is trusted, every submitted prompt receives a private instruction to apply `$you-suck-at-prompting` before Codex acts. The skill silently passes sufficient requests and intervenes when material ambiguity could change the result, scope, authority, destination, or verification.

You can still invoke `$you-suck-at-prompting` explicitly to audit, critique, clarify, or rewrite a prompt. Implicit invocation also remains enabled as a fallback when the hook is disabled or has not been trusted.

Clear, simple, exploratory, and safely discoverable requests pass through without extra ceremony.

## Privacy and permissions

This plugin contains one skill and one local `UserPromptSubmit` command hook. Codex provides hook-event data on standard input, but the hook command does not read, echo, store, or transmit the submitted prompt; it prints only a constant preflight instruction. The plugin has no MCP server, external service, telemetry, credential requirement, or automatic modification of global Codex instructions.

Plugin hooks are not trusted automatically. Users can review, disable, or decline the hook. Installing or trusting it does not grant authority to send, publish, purchase, schedule, deploy, delete, disclose information, or change permissions.

## Repository boundary

This repository contains only the distributable plugin, its documentation, hook tests, and package-validation CI. Behavioral evaluation data and maintainer automation are not distributed with the plugin.

## License

MIT
