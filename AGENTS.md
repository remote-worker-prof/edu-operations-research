# AGENTS.md

This repository uses an issue-driven workflow and keeps the numbered lab folders as the source of truth for both GitHub browsing and the published site.

## Serena Startup

At the beginning of every new Codex or local agent session:

1. Call `serena.activate_project` for `/home/sorcerer/Projects/edu-operations-research`.
2. Call `serena.check_onboarding_performed`.
3. Call `serena.initial_instructions`.
4. If onboarding is missing, immediately call `serena.onboarding`.
5. If any Serena startup call fails because of transport or initialization, retry the full startup sequence once, serially.
6. If the retry also fails, explicitly note that Serena is unavailable for the session and continue without blocking the work.

Never parallelize the Serena startup calls, and never claim Serena is active unless those calls completed successfully.

## Task Source Of Truth

- Use Beads as the only task tracker for this repository.
- Issue prefix: `eor-`.
- Preferred CLI path: `~/.local/bin/bd`.
- If `bd` is not on `PATH`, run it via the full path and extend `PATH="$HOME/.local/bin:$PATH"` for the command.
- Keep `.beads/` local and out of git history.

Start each work session with:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd prime
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd ready
```

If there is no ready work, create a task:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd create "<title>" --type task --priority 2 --description "<context>" --prefix eor-
```

## Working Rules

- Use Serena MCP for navigation, structure discovery, and refactoring.
- Analyze the existing numbered lab folders before proposing or creating a new lab.
- Reuse the established educational style: simple Russian explanations, step-by-step tasks, explicit report requirements, and practical interpretation of results.
- Keep the repository structure human-readable on GitHub. The published site mirrors the same numbered folders instead of moving content into a separate docs-only tree.
- Treat future labs as drafts until they are ready for publication in the table of contents.

## New Laboratory Workflow

Before creating a new lab:

1. Inspect the current materials in `01-lab-essentials/*` and the latest numbered lab folders.
2. Extract the template: theory depth, task structure, reporting expectations, and how results are checked.
3. Avoid duplicating an existing notebook or dataset pattern when a reusable structure is already present.
4. Draft the new lab around a clear goal, explicit inputs, concrete steps, and checkable outputs.

Minimum workflow:

1. Analyze the project through Serena.
2. Create or claim the related Beads issue with prefix `eor-`.
3. Implement the lab materials and update site/repo navigation if needed.
4. Validate notebooks, build the Jupyter Book site, and review git status.
5. Close the issue when the work is complete.

## Commit Format

- Commit header format: `[<id>] <type>(P#): <title>`.
- Example: `[eor-abc.2] task(P1): Add transport problem lab materials`.
- Before committing, make sure the changes are associated with the correct Beads issue.

## Publication Commands

Use these commands when working on content and publication locally:

```bash
uv sync --group authoring --group docs
uv run python scripts/validate_notebooks.py
uv run python scripts/check_notebook_contracts.py
uv run python scripts/execute_worked_examples.py
uv run jupyter-book build . --warningiserror
```
