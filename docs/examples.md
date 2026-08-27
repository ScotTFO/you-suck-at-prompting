# Four representative behaviors

These synthetic examples cover the skill’s four useful lanes: stay out of the way, repair a material problem, choose safe Git isolation for a tracked programming mutation, and review a prompt when review is the requested deliverable.

## Clear bypass

**Request:**

```text
Return exactly the word READY.
```

**Response:**

```text
READY
```

A clear request proceeds normally. There is no rating, kickoff, rewrite, or acknowledgement gate. Even a false-positive load must preserve the exact-output contract.

## Material repair

**Request:**

```text
Fix it.
```

**Skill response:**

Analyzing whether You Suck at Prompting… your prompt’s performance review is underway.
Prompt performance rating: 1/5 - This prompt filed a verb, lost the target, and still requested expedited handling.

Draft rewritten prompt:

```text
Investigate and fix [NEEDED: the specific failure or undesired behavior]
in [NEEDED: the affected application, repository, or file].

Keep the change limited to the identified problem and verify the fix with
the smallest relevant test or reproduction.
```

What is broken, and where are you seeing it?

Expected prompt impact: The answer identifies the target, bounds the fix, and determines the verification.

No acknowledgement is requested while material placeholders remain. A completed rewrite still cannot create authority to deploy, publish, purchase, delete, disclose, or change access.

## Programming isolation

**Request:**

```text
Fix the parser regression in parser.py and run the focused tests.
```

**Repository context:** The checkout is clean on the default branch and no task branch or linked worktree exists.

**Skill response:**

The request is actionable, but the tracked-file mutation needs a bounded location. The rewrite says to create and switch to a dedicated task branch in the current checkout after acknowledgement. If the checkout were dirty with unrelated work, or if this were a high-risk migration, the rewrite would choose a branch-backed linked worktree and leave the original checkout untouched. The preflight is read-only; no branch or worktree is created before acknowledgement.

Read-only programming and work outside Git remain silent passes.

## Explicit review

**Request:**

```text
Audit this prompt: Rename load_item to load_record in loader.py, update its
local references, run the focused unit test, and do not commit or push. The
change is already scoped to a dedicated task branch-backed linked worktree.
```

**Skill response:**

Prompt performance rating: 5/5 - Annoyingly complete; the Prompting Improvement Department has begun layoffs.

Prompt unchanged:

```text
Rename load_item to load_record in loader.py, update its local references,
run the focused unit test, and do not commit or push. The change is already
scoped to a dedicated task branch-backed linked worktree.
```

The requested deliverable is prompt review, so the inner prompt is returned rather than executed. Ordinary clear tasks do not receive the 5/5 ceremony.

See [Behavior, safety, and privacy](behavior-and-safety.md) for the full contract.
