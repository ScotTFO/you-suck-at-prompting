# Installation, migration, and verification

This repository contains one standard agent skill at `skills/you-suck-at-prompting`. The external [`skills` CLI](https://github.com/vercel-labs/skills) discovers it and installs it into the harnesses you select. There is no repository-local installer or npm package.

## Prerequisites

- Node.js 22.20 or newer, with `npx`, for installation and updates
- Git when installing from GitHub
- A supported agent harness

The installed runtime is plain Markdown plus local references. It does not need Node.js after installation.

## Install for a project

Run this from the project that should receive the skill:

```text
npx skills@latest add ScotTFO/you-suck-at-prompting
```

The CLI detects available harnesses and presents a selection. Choose one or more, confirm the project scope, then start a fresh task or chat.

## Install globally

```text
npx skills@latest add ScotTFO/you-suck-at-prompting --global
```

Choose the harnesses that should receive the user-level skill, then start a fresh task or chat.

## Select harnesses explicitly

For the four priority harnesses:

```text
npx skills@latest add ScotTFO/you-suck-at-prompting --agent codex claude-code github-copilot hermes-agent --yes
```

To install for every harness recognized by the current CLI:

```text
npx skills@latest add ScotTFO/you-suck-at-prompting --agent '*' --yes
```

Add `--global` to either command for user-level installation.

Current project destinations for the priority harnesses are:

| Harness | Project skill directory |
|---|---|
| Codex | `.agents/skills/you-suck-at-prompting` |
| Claude Code | `.claude/skills/you-suck-at-prompting` |
| GitHub Copilot | `.agents/skills/you-suck-at-prompting` |
| Hermes | `.hermes/skills/you-suck-at-prompting` |

Codex and GitHub Copilot intentionally share the standard `.agents/skills` project destination.

## Use copies instead of symlinks

The CLI normally manages a canonical project skill and links harness destinations when the platform supports it. Use `--copy` when links are unavailable, prohibited, or undesirable:

```text
npx skills@latest add ScotTFO/you-suck-at-prompting --agent '*' --copy --yes
```

Release checks use `--copy` so the priority destinations can be compared byte for byte with the tagged source. The all-agent compatibility probe separately checks host adapters.

## Install an exact release

Use a tag URL when reproducibility matters:

```text
npx skills@latest add https://github.com/ScotTFO/you-suck-at-prompting/tree/v0.13.0
```

The release checks pin the installer as well:

```text
npx skills@1.5.23 add https://github.com/ScotTFO/you-suck-at-prompting/tree/v0.13.0 --agent '*' --copy --yes
```

## Update

Update the project installation:

```text
npx skills@latest update you-suck-at-prompting --project --yes
```

Update the global installation:

```text
npx skills@latest update you-suck-at-prompting --global --yes
```

For copied or release-pinned installations, rerun `add` with the desired source, tag, harness list, and `--copy` so the installation mode stays explicit.

## Remove

Remove the project installation from all linked harnesses:

```text
npx skills@latest remove you-suck-at-prompting --yes
```

Remove the global installation:

```text
npx skills@latest remove you-suck-at-prompting --global --yes
```

Limit removal with `--agent <agent-key>` when needed.

## Migrate from an older native installation

The installer does not modify old native installations. Remove an older copy first so the host cannot load two versions of the skill.

### Codex native plugin

```text
codex plugin remove you-suck-at-prompting@scottfo
codex plugin marketplace remove scottfo
```

Skip marketplace removal if another installed item uses that marketplace.

### Claude Code native plugin

```text
claude plugin uninstall you-suck-at-prompting@scottfo
claude plugin marketplace remove scottfo
```

Skip marketplace removal if another installed item uses that marketplace.

### VS Code GitHub Copilot native plugin

1. Open the Copilot Plugins view with `@agentPlugins`.
2. Find **You Suck at Prompting** and select **Uninstall**.
3. Remove only `ScotTFO/you-suck-at-prompting` from `chat.plugins.marketplaces` if no other installed item needs it.
4. Reload VS Code.

### Remove the old v0.7 Copilot instruction file

The v0.7 release also used an always-on instruction file. Delete only the matching file if it still exists:

- Personal: `~/.copilot/instructions/you-suck-at-prompting.instructions.md`
- Repository: `.github/instructions/you-suck-at-prompting.instructions.md`

On Windows PowerShell, resolve the personal path before removing it:

```powershell
$profileRoot = [Environment]::GetFolderPath('UserProfile')
$oldAdapter = Join-Path $profileRoot '.copilot\instructions\you-suck-at-prompting.instructions.md'
if (Test-Path -LiteralPath $oldAdapter -PathType Leaf) {
  Remove-Item -LiteralPath $oldAdapter
}
```

Preserve unrelated instruction files.

## Installer telemetry

The installed skill runtime has no telemetry. The external `skills` installer collects anonymous telemetry by default.

Opt out for a PowerShell session:

```powershell
$env:DISABLE_TELEMETRY = '1'
npx skills@latest add ScotTFO/you-suck-at-prompting
```

Opt out for one macOS or Linux command:

```bash
DISABLE_TELEMETRY=1 npx skills@latest add ScotTFO/you-suck-at-prompting
```

`DO_NOT_TRACK=1` is also honored.

## Smoke tests

Use a fresh task or chat for each case.

1. **Clear bypass:** Submit `Return exactly the word READY.` Expect exactly `READY`, with no rating or preflight markers.
2. **Material repair:** Submit `Fix it.` Expect a draft containing `[NEEDED: ...]`, one focused question, and no acknowledgement request while required details remain.
3. **Completed repair:** Answer every placeholder exactly, and confirm that the task runs once without another rating, kickoff, or acknowledgement.
4. **Prompt-only:** Ask to rewrite `Explain [NEEDED: the change] for [NEEDED: the audience]` without execution. Expect placeholders in the returned prompt, no question, and no acknowledgement request.
5. **Explicit review:** Submit `Audit this prompt: Rename load_item to load_record in loader.py and run the focused unit test.` Expect either a 5/5 unchanged assessment or a material repair grounded in the prompt as written. The inner task must not execute.

Direct invocation is `$you-suck-at-prompting` in Codex. Other harnesses use their installed-skill interface.

## Troubleshooting

- If a host does not select the skill, start a fresh task or chat and confirm the destination directory in the table above.
- If two copies load, remove the older native installation and inspect both project and global destinations.
- If links are blocked, rerun installation with `--copy`.
- For contributor validation, run `python -B -m unittest tests.test_skill_contract` from the repository root. The `-B` flag prevents local bytecode from entering the package scan.

Native selection is model- and host-controlled. Installation checks prove package shape and copied files. Live behavior checks must name the host, version, prompt lane, and result separately.
