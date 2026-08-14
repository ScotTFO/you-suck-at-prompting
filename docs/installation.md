# Installation and verification

You Suck at Prompting supports Codex, Claude Code, and VS Code GitHub Copilot Agent mode. Each host discovers the same shared skill, but activation differs by host.

## Codex

Install the marketplace and plugin:

```powershell
codex plugin marketplace add ScotTFO/you-suck-at-prompting
codex plugin add you-suck-at-prompting@scottfo
```

Review and trust the plugin hook when Codex prompts you. In Codex CLI, use `/hooks` to inspect the exact command before trusting it.

Start a new Codex task after installation so the current skill and hook are loaded.

### Upgrade Codex

```powershell
codex plugin marketplace upgrade scottfo
codex plugin add you-suck-at-prompting@scottfo
```

Start a fresh task after upgrading.

## Claude Code

Install the marketplace and plugin:

```powershell
claude plugin marketplace add ScotTFO/you-suck-at-prompting
claude plugin install you-suck-at-prompting@scottfo
```

Use `/hooks` to inspect the installed `UserPromptSubmit` hook, then start a new Claude Code session.

### Upgrade Claude Code

```powershell
claude plugin marketplace update scottfo
claude plugin update you-suck-at-prompting@scottfo
```

Start a fresh session after upgrading.

## VS Code GitHub Copilot

Copilot support has two parts: the plugin supplies the shared skill, and a personal instruction file applies the approval gate to every new Agent-mode task.

1. In VS Code settings, append this repository to your existing `chat.plugins.marketplaces` list. Do not replace marketplaces already configured there.

   ```jsonc
   "chat.plugins.marketplaces": [
     "ScotTFO/you-suck-at-prompting"
   ]
   ```

2. Open the Extensions view, search for `@agentPlugins`, find **You Suck at Prompting**, and select **Install**. Review the source and trust prompt before confirming.

3. Install the always-on instruction adapter without replacing other Copilot instructions.

   **Windows PowerShell:**

   ```powershell
   $instructionsDirectory = Join-Path $HOME ".copilot\instructions"
   New-Item -ItemType Directory -Force -Path $instructionsDirectory | Out-Null
   Invoke-WebRequest `
     -Uri "https://raw.githubusercontent.com/ScotTFO/you-suck-at-prompting/main/plugins/you-suck-at-prompting/copilot/you-suck-at-prompting.instructions.md" `
     -OutFile (Join-Path $instructionsDirectory "you-suck-at-prompting.instructions.md")
   ```

   **macOS or Linux:**

   ```bash
   mkdir -p "$HOME/.copilot/instructions"
   curl -fL \
     "https://raw.githubusercontent.com/ScotTFO/you-suck-at-prompting/main/plugins/you-suck-at-prompting/copilot/you-suck-at-prompting.instructions.md" \
     -o "$HOME/.copilot/instructions/you-suck-at-prompting.instructions.md"
   ```

4. Start a new GitHub Copilot chat in **Agent** mode. Run **Chat: Open Customizations** and confirm that both the plugin skill and **You Suck at Prompting** instruction appear and are enabled.

Agent plugins can be disabled by enterprise policy. If the Plugins view or `chat.plugins.enabled` is unavailable, ask your administrator to allow agent plugins and this marketplace.

### Project-only Copilot installation

To keep the customization in one repository instead of a personal profile, copy these release directories into the target project:

```text
plugins/you-suck-at-prompting/skills/you-suck-at-prompting/
  -> .github/skills/you-suck-at-prompting/

plugins/you-suck-at-prompting/copilot/you-suck-at-prompting.instructions.md
  -> .github/instructions/you-suck-at-prompting.instructions.md
```

Commit the copied files only if the project should share the behavior with collaborators. Start a new Agent-mode chat and verify both entries in **Chat: Open Customizations**.

Copilot coverage applies to Chat in Agent mode. It does not affect inline code completions. Installing only the skill leaves automatic selection best-effort; the instruction adapter supplies the always-on gate.

## Smoke test

Use the same behavior check on each installed host:

1. Submit `Create a text file named hello.txt containing hello.` Confirm the host shows a rewritten prompt before using a tool or changing a file.
2. Reply `yes`. Confirm the host performs the task once without showing the rewrite gate again.
3. Start a new task and submit `Fix it`. Confirm the host shows a draft containing `[NEEDED: ...]`, asks one focused question, and does not request acknowledgement yet.

For Copilot, first confirm the skill and instruction are enabled in **Chat: Open Customizations**.

## Direct invocation

You can also invoke the skill explicitly:

- **Codex:** `$you-suck-at-prompting`
- **Claude Code:** `/you-suck-at-prompting:you-suck-at-prompting`
- **VS Code GitHub Copilot:** `/you-suck-at-prompting:you-suck-at-prompting`

When a hook or instruction adapter is disabled or unavailable, model-driven implicit skill selection remains a best-effort fallback.
