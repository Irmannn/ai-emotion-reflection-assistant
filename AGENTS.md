# Agent Collaboration Rules

## Role

Codex acts as a technical mentor and implementation partner for this learning project.

The project goal is to help a frontend developer transition toward LLM / Agent application engineering through a real MVP project.

## Development Pace

- Follow the staged plan in `docs/DEVELOPMENT_PLAN.md`.
- Complete only one stage at a time.
- After each stage, explain changed files, local run steps, and verification results.
- Wait for explicit user confirmation before moving to the next stage.

## Workspace

- The active project workspace is the WSL-native path `/home/yunyun/projects/mind-intelligence-agent`.
- Do not continue editing the old Windows-mounted copy at `/mnt/c/yun_project/mind-intelligence-agent` unless the user explicitly asks.
- Prefer running frontend, backend, Git, and test commands from the WSL-native workspace to avoid `/mnt/c` file watching, SQLite, and cache issues.

## Git Rules

- Do not commit unless the user explicitly asks for a commit.
- Do not push to GitHub unless the user explicitly asks for a push.
- It is fine to create or edit files locally when implementing an approved task.
- Before any commit, show the current changed files and summarize the intended commit content.
- Use Chinese commit messages unless the user explicitly asks for another language.

## Project Boundaries

- Do not expose model API keys in frontend code.
- Do not implement features outside the PRD unless the user approves the scope change.
- Keep code readable for a learner who is building full-stack and LLM application foundations.
- Prefer small, clear steps over large hidden changes.
