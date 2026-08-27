# Programming and Git isolation

Use this reference only when the request may create or change files intended to be tracked in a Git repository. A programming request is read-only when it asks for planning, explanation, review, diagnosis, or test execution without changing tracked files. Do not add Git setup to a non-Git task or initialize Git as an unrequested side effect.

## Read-only preflight

Retrieve the answer from the conversation, repository rules, and available tools before asking the user. When Git inspection is available, identify:

- the repository root and whether the current directory is a bare repository;
- the current branch or detached state;
- tracked and untracked status;
- every registered checkout, including linked worktrees;
- the repository-designated default or base ref; and
- closer repository or host instructions that govern isolation.

Use read-only Git inspection such as `git rev-parse`, `git status --porcelain=v2`, `git branch --show-current`, and `git worktree list --porcelain`. Never open `.env` files, credentials, or unrelated private data to answer an isolation question.

## Choose the smallest safe checkout

Git branches and worktrees are not competing kinds of branch. The choice is between a dedicated branch in the current checkout and a branch-backed linked worktree.

| Context | Choice |
|---|---|
| A task-specific branch or linked worktree already exists and is not owned by another task | Reuse it. A clear request can pass silently. |
| The checkout is clean, available, and the change is an ordinary bounded solo task | Create a dedicated task branch in the current checkout after acknowledgement. |
| Existing edits clearly belong to this task | Create or reuse the task branch in place and preserve the files and index exactly. |
| Existing edits are unrelated or ownership is unknown, another task is active, work is parallel, or the change is high risk | Use a dedicated branch-backed linked worktree from a usable base and leave the original checkout untouched. Unrelated or unclear dirty ownership always takes this route. |
| The checkout is a host-managed isolated detached worktree | Reuse it without manufacturing another branch. An unmanaged detached checkout may use its current commit as a base only when that commit is usable. |
| The current location is a bare coordinator with a usable base | Work through a registered or newly created linked worktree, never by pretending the bare directory is editable. |
| No Git repository exists | Do not initialize Git or invent a branch. |
| Dirty-file ownership or a usable base cannot be determined | Use **NEEDS-INPUT** and ask one focused question before changing Git state. |

Treat repository-wide rewrites, migrations, dependency or toolchain upgrades, broad code generation, and experiments likely to be abandoned as high risk. Follow an explicit user, host, or closer repository choice when it is valid; a stronger rule still wins.

## Put the decision in the rewrite

When the choice is known, name it briefly in the rewritten prompt. For a current-checkout branch, require a task-specific branch, preservation of any related edits, and no commit, push, merge, cleanup, or deletion unless separately authorized. For a linked worktree, require the absolute worktree location when safely known, the selected base ref, preservation of the original checkout, and no copying of untracked or ignored files.

When Git state is unavailable during rewriting, embed the preflight and the decision table in the prompt instead of asking the user to report discoverable facts. Ask only when the executor cannot safely determine dirty-file ownership or a usable base. Branch or worktree creation is execution work and must wait for the existing prompt acknowledgement gate, without creating either before acknowledgement. Every tracked-mutation rewrite should state that branch or worktree creation waits for acknowledgement, including a prompt-only review. Do not stash, reset, clean, overwrite, or move existing edits.

When the underlying programming task is requested, a complete isolation repair is **APPROVAL-READY**: end the visible response with the exact line `Reply with an acknowledgement to use this prompt.` and do not perform the work yet.

For a task spanning repositories, repeat the preflight and choice for each repository. Do not let prompt approval authorize commits, pushes, merges, rebases, cleanup, publication, or other external effects.
