# Obsidian Manage Skills

`obsidian-manage-skill` is a multi-skill repository for Obsidian Vault workflows.
It is organized for `skills.sh` discovery and can be installed into supported agents such as Codex, Claude Code, Cursor, and others through the `skills` CLI.

## Included skills

- `note-exploration`: Expands pre-writing directions, questions, contrasts, and example candidates before a note draft exists.
- `vault-content`: Focuses on note-type decisions, note structure, writing, and rewrites.
- `vault-manage`: Focuses on file contracts, frontmatter validation, module placement, and vault governance.
- `playwright-image-reference`: Captures clean image references from websites with Playwright MCP.

## Repository structure

This repository intentionally uses a multi-skill layout:

```text
skills/
├── note-exploration/
│   ├── SKILL.md
│   ├── evals/
│   └── references/
├── playwright-image-reference/
│   └── SKILL.md
├── vault-content/
│   ├── SKILL.md
│   └── references/
└── vault-manage/
    ├── SKILL.md
    ├── assets/
    ├── references/
    └── scripts/
```

Each skill lives at `skills/<skill-name>/SKILL.md`, which is one of the standard discovery locations used by the `skills` CLI.

## Quick start

List the skills exposed by this repository:

```bash
npx skills add . --list
```

Install the note writing skill into Codex for the current project:

```bash
npx skills add . --agent codex --skill vault-content -y
```

Install from GitHub instead of a local path:

```bash
npx skills add <OWNER>/<REPO> --agent codex --skill vault-content -y
```

## Documentation

- [Codex installation guide](./docs/codex_install.md)

## Notes for maintainers

- Keep each skill self-contained under `skills/<name>/`.
- Put reusable scripts in `scripts/`, reference material in `references/`, and output templates or fixtures in `assets/`.
- Avoid adding a root-level `SKILL.md` unless the repository is intentionally being converted into a single-skill package.
