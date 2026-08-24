# Installation and verification

You Suck at Prompting supports Codex, Claude Code, and VS Code GitHub Copilot Agent mode. The distributed package contains one shared skill. Each host uses the skill description for native selection; there is no submission hook or always-on Copilot instruction adapter.

## Codex

Install the marketplace and plugin:

```powershell
codex plugin marketplace add ScotTFO/you-suck-at-prompting
codex plugin add you-suck-at-prompting@scottfo
```

Start a new Codex task so the current skill metadata is loaded. No hook review or trust step is required.

### Upgrade Codex

```powershell
codex plugin marketplace upgrade scottfo
codex plugin add you-suck-at-prompting@scottfo
```

Start a fresh task after upgrading. An upgrade from v0.7.0 must leave no You Suck at Prompting entry in `/hooks`; v0.8.0 contains no hook file.

## Claude Code

Install the marketplace and plugin:

```powershell
claude plugin marketplace add ScotTFO/you-suck-at-prompting
claude plugin install you-suck-at-prompting@scottfo
```

Start a new Claude Code session. No `UserPromptSubmit` hook is installed.

### Upgrade Claude Code

```powershell
claude plugin marketplace update scottfo
claude plugin update you-suck-at-prompting@scottfo
```

Start a fresh session. If an earlier cached v0.7.0 installation remains active, remove and reinstall the plugin through Claude Code, then confirm `/hooks` has no You Suck at Prompting hook.

## VS Code GitHub Copilot

1. In VS Code settings, append this repository to the existing `chat.plugins.marketplaces` list. Do not replace other marketplaces.

   ```jsonc
   "chat.plugins.marketplaces": [
     "ScotTFO/you-suck-at-prompting"
   ]
   ```

2. Open Extensions, search for `@agentPlugins`, find **You Suck at Prompting**, and select **Install**.

3. Start a new Copilot chat in **Agent** mode. Run **Chat: Open Customizations** and confirm the plugin skill is enabled.

No instruction-file copy is required. Copilot coverage applies to Agent mode, not inline completions. Enterprise policy can disable agent plugins; if the Plugins view or `chat.plugins.enabled` is unavailable, ask an administrator to allow agent plugins and this marketplace.

### Project-only Copilot installation

Copy only the shared skill into the target repository:

```text
plugins/you-suck-at-prompting/skills/you-suck-at-prompting/
  -> .github/skills/you-suck-at-prompting/
```

Commit it only if collaborators should share the behavior. Start a new Agent-mode chat and confirm the skill appears in **Chat: Open Customizations**.

## Upgrade note for v0.7.0 Copilot users

v0.7.0 asked Copilot users to copy an always-on personal instruction file. v0.8.0 does not use it. Remove that one old adapter so it cannot continue intercepting requests independently of the skill.

**Windows PowerShell:**

```powershell
$oldAdapter = Join-Path $HOME ".copilot\instructions\you-suck-at-prompting.instructions.md"
if (Test-Path -LiteralPath $oldAdapter) {
  Remove-Item -LiteralPath $oldAdapter
}
```

**macOS or Linux:**

```bash
rm -f "$HOME/.copilot/instructions/you-suck-at-prompting.instructions.md"
```

If the adapter was copied into a repository, remove only `.github/instructions/you-suck-at-prompting.instructions.md` from that repository. Preserve unrelated instruction files.

After removal, start a fresh Agent-mode chat and verify **Chat: Open Customizations** lists the skill but not the old instruction adapter.

## Smoke test

Use fresh chats or tasks so selection state does not leak between cases.

1. **Clear bypass:** Submit `Return exactly the word READY.` Expect exactly `READY`, with no rating or preflight markers.
2. **Material trigger:** Submit `Fix it.` Expect a draft containing `[NEEDED: ...]`, one focused question, and no acknowledgement request yet.
3. **Explicit review:** Submit `Audit this prompt: Rename load_item to load_record in loader.py and run the focused unit test.` Expect either a 5/5 unchanged assessment or a material repair grounded in the prompt as written.
4. **Near miss:** Ask an ordinary exploratory question containing the word “prompt.” Expect a normal answer with no performance-review markers.
5. **Active gate:** After an approval-ready rewrite, reply `yes`. Expect the displayed task to execute once without another audit.

Native implicit selection is model- and host-controlled. Repeat representative trigger and bypass cases when qualifying a release; do not infer behavior from one lucky run.

## Direct invocation

- **Codex:** `$you-suck-at-prompting`
- **Claude Code:** `/you-suck-at-prompting:you-suck-at-prompting`
- **VS Code GitHub Copilot:** `/you-suck-at-prompting:you-suck-at-prompting`

Direct invocation explicitly requests the skill’s assessment. It does not broaden tool permissions or authorize consequential effects.
