# skills.sh compatibility

This repository is structured so that `skills.sh` and the `skills` CLI can discover multiple skills from a single repo without extra packaging steps.

## Why this repo uses `skills/`

The `skills` CLI looks for skills in standard locations inside a repository, including:

- the repository root if it contains `SKILL.md`
- `skills/`
- `.agents/skills/`
- `.claude/skills/`
- several other agent-specific skill directories

For a multi-skill repository, `skills/<skill-name>/SKILL.md` is the safest and clearest layout. That is the pattern used here.

## Expected shape of each skill

Each installable skill should look like this:

```text
skills/<skill-name>/
├── SKILL.md
├── scripts/      # optional
├── references/   # optional
└── assets/       # optional
```

`SKILL.md` should start with YAML frontmatter like this:

```md
---
name: my-skill
description: What the skill does and when to use it.
---
```

Required fields:

- `name`
- `description`

Optional field:

- `metadata.internal: true`
  Use this only when a skill should be hidden from normal discovery.

## Why there is no root `SKILL.md`

This repository is meant to expose several installable skills, not one monolithic skill.

Keeping the repo root free of `SKILL.md` helps communicate that clearly and avoids depending on `--full-depth` behavior when a consumer wants subdirectory discovery.

## Validation commands

From the repository root, these commands are useful:

```bash
npx skills add . --list
```

List while targeting Codex as the installation destination:

```bash
npx skills add . --list --agent codex
```

If you ever add a root `SKILL.md` temporarily and still want to inspect nested skills:

```bash
npx skills add . --list --full-depth
```

## Publishing checklist

- Keep every public skill under `skills/<name>/SKILL.md`.
- Make sure every `SKILL.md` has a unique `name`.
- Put strong trigger phrases in `description` so agents know when to use the skill.
- Keep bundled resources next to the skill that uses them.
- Use `metadata.internal: true` only for hidden or work-in-progress skills.
- Validate locally with `npx skills add . --list` before sharing the repository.

## Repository-specific guidance

This repo currently exposes these public skills:

- `using-vaults`
- `vault-content`
- `vault-manage`
- `note-brainstorming`
- `playwright-image-reference`

For most users, `using-vaults` should be the first skill they install because it acts as the Obsidian entry point and routes work to the more specialized skills.
