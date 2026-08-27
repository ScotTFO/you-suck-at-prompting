# Installation, migration, and verification

This repository contains one standard agent skill at `skills/you-suck-at-prompting`. The external [`skills` CLI](https://github.com/vercel-labs/skills) discovers that skill and installs it into the harnesses you select. There is no repository-local installer or npm package.

## Prerequisites

- Node.js 22.20 or newer, with `npx`, for installation and updates
- Git when installing from GitHub
- A supported agent harness

Node.js is not part of the installed runtime. Once installed, the skill is plain Markdown plus local references and optional display metadata.

## Remove an older native installation first

The installer does not modify old native plugin installations. Remove any old copy before NPX installation so the host cannot load the same skill twice.

### Codex native plugin

```text
codex plugin remove you-suck-at-prompting@scottfo
codex plugin marketplace remove scottfo
```

Skip the marketplace removal if other plugins still use that marketplace.

### Claude Code native plugin

```text
claude plugin uninstall you-suck-at-prompting@scottfo
claude plugin marketplace remove scottfo
```

Skip the marketplace removal if other plugins still use it.

### VS Code GitHub Copilot native plugin

1. Open the Copilot Plugins view with `@agentPlugins`.
2. Find **You Suck at Prompting** under installed plugins and select **Uninstall**.
3. Remove only `ScotTFO/you-suck-at-prompting` from `chat.plugins.marketplaces` if no other installed plugin needs it.
4. Reload VS Code.

### Condensed v0.7 Copilot cleanup

v0.7 also used an always-on instruction adapter. Delete only the matching file if it still exists:

- Personal: `~/.copilot/instructions/you-suck-at-prompting.instructions.md`
- Repository: `.github/instructions/you-suck-at-prompting.instructions.md`

On Windows PowerShell, the personal file can be removed with a resolved, literal target:

```powershell
$profileRoot = [Environment]::GetFolderPath('UserProfile')
$oldAdapter = Join-Path $profileRoot '.copilot\instructions\you-suck-at-prompting.instructions.md'
if (Test-Path -LiteralPath $oldAdapter -PathType Leaf) {
  Remove-Item -LiteralPath $oldAdapter
}
```

Preserve every unrelated instruction file.

## Install for a project

Run this from the project that should receive the skill:

```text
npx skills@latest add ScotTFO/you-suck-at-prompting
```

The CLI detects available harnesses and presents a selection. Choose one or more, confirm the project scope, and start a fresh task or chat after installation.

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

The CLI normally manages a canonical project skill and links harness destinations when the platform supports it. Use `--copy` when symlinks are unavailable, prohibited, or undesirable:

```text
npx skills@latest add ScotTFO/you-suck-at-prompting --agent '*' --copy --yes
```

Release verification uses `--copy` so the Codex, Claude Code, GitHub Copilot, and Hermes destinations can be compared byte for byte with the tagged source. The all-agent compatibility probe separately validates harness adapters. For example, `skills@1.5.23` normalizes Eve frontmatter into Eve's schema while preserving the description and runtime body.

## Install an exact release

Use a tag URL when reproducibility matters:

```text
npx skills@latest add https://github.com/ScotTFO/you-suck-at-prompting/tree/v0.12.0
```

The private release gate pins the installer as well:

```text
npx skills@1.5.23 add https://github.com/ScotTFO/you-suck-at-prompting/tree/v0.12.0 --agent '*' --copy --yes
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

You can limit removal with `--agent <agent-key>`.

## Installer telemetry

The installed skill runtime has no telemetry. The external `skills` installer collects anonymous installation telemetry by default.

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
3. **Explicit review:** Submit `Audit this prompt: Rename load_item to load_record in loader.py and run the focused unit test.` Expect either a 5/5 unchanged assessment or a material repair grounded in the prompt as written. The inner task must not execute.

Direct invocation is `$you-suck-at-prompting` in Codex. For other harnesses, use the installed-skill interface provided by that host.

Native selection is model- and host-controlled. Qualify releases with both trigger and bypass cases, and report installation compatibility separately from live behavioral certification.
