# You Suck at Prompting

An installable Codex skill that catches consequential ambiguity, repairs prompts without changing their intent, and stays out of the way when a request is already clear.

The joke stays in the name. The skill critiques the prompt, never the person.

## Install

```powershell
codex plugin marketplace add ScotTFO/you-suck-at-prompting
codex plugin add you-suck-at-prompting@scottfo
```

Start a new Codex task after installation or upgrade so the current skill version is loaded.

## Use

Invoke `$you-suck-at-prompting` explicitly to audit, critique, clarify, or rewrite a prompt. The skill also supports implicit invocation when material ambiguity could change the result, scope, authority, destination, or verification.

Clear, simple, exploratory, and safely discoverable requests pass through without extra ceremony.

## Privacy and permissions

This is a skills-only plugin. It has no MCP server, external service, telemetry, credential requirement, or automatic modification of global Codex instructions. Installing it does not grant authority to send, publish, purchase, schedule, deploy, delete, disclose information, or change permissions.

## Repository boundary

This repository contains only the distributable plugin, its documentation, and package-validation CI. Behavioral evaluation data and maintainer automation are not distributed with the plugin.

## License

MIT
