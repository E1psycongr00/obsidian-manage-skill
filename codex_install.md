# Install for Codex CLI

This guide shows how to install skills from this repository into Codex with the `skills` CLI.

## Codex target paths

According to the `skills` CLI, Codex uses:

- project-level install path: `.agents/skills/`
- global install path: `~/.codex/skills/`

By default, `skills add` installs at the project level. Add `-g` to install globally.

## 1. Preview what this repo exposes

From the repository root:

```bash
npx skills add . --list --agent codex
```

That lets you confirm the available skill names before installing anything.

## 2. Install one skill into the current project

Install the main Obsidian entry-point skill:

```bash
npx skills add . --agent codex --skill using-vaults -y
```

Recommended first install:

- `using-vaults`

## 3. Install multiple related skills

If you want the orchestration skill plus the two main downstream skills:

```bash
npx skills add . --agent codex --skill using-vaults vault-content vault-manage -y
```

If you want every public skill in this repository:

```bash
npx skills add . --agent codex --skill note-brainstorming playwright-image-reference using-vaults vault-content vault-manage -y
```

## 4. Install globally instead of per project

```bash
npx skills add . --agent codex --skill using-vaults -g -y
```

Use this when you want the skill available across repositories.

## 5. Install from GitHub

If the repository is published on GitHub, install it without cloning first:

```bash
npx skills add <OWNER>/<REPO> --agent codex --skill using-vaults -y
```

You can also use a full repository URL:

```bash
npx skills add https://github.com/<OWNER>/<REPO> --agent codex --skill using-vaults -y
```

## 6. Verify the installation

List installed skills filtered to Codex:

```bash
npx skills list --agent codex
```

JSON output is also available:

```bash
npx skills list --agent codex --json
```

## Helpful flags

- `--list`: show discoverable skills without installing
- `--copy`: copy files instead of creating symlinks
- `-g`: install globally
- `-y`: skip confirmation prompts

Example using copies instead of symlinks:

```bash
npx skills add . --agent codex --skill using-vaults --copy -y
```

## Recommendation for this repository

Start with `using-vaults`.
It is the best default entry point because it decides when to bring in `note-brainstorming`, `vault-content`, and `vault-manage` during Obsidian Vault work.
