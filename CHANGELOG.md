# Changelog

All notable changes to the **AegisFlow** project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Conventional Commits](https://www.conventionalcommits.org/).

## [1.0.0] - 2026-09-20

### Added
- **AegisFlow Micro-kernel Engine (`tools/`)**:
  - `state_manager.py`: Complete task lifecycle engine with SRP $\le 8.0\text{h}$ cap, 4-dimensional veto rejections (`#QR/#SR/#FR/#DR`), 3-round circuit breaker, LangGraph time-travel checkpoints, and OpenHands immutable EventStream auditing.
  - `gatekeeper.py`: Evaluator for Quality Gates 1-5, Conventional Commits regex validation, SWE-agent fast AST linter, OWASP/secret scanner, and cryptographic receipt generator (`REC-xxxx.json`).
  - `repo_hygiene.py`: Zero-pollution root whitelist enforcer, test-mirror gap checker, depth guard, and Aider-inspired AST Repo Map generator.
  - `board_renderer.py`: High-visibility ANSI terminal sprint kanban with Top-5 Anti-Token Bleed protection.
  - `kanban_server.py` & `web/index.html`: Zero-dependency offline single-file Web board running on `localhost:8848`.
  - `vc_cli.py`: Unified multi-command CLI entrypoint (`init`, `board`, `create`, `start`, `advance`, `reject`, `gate-check`, `lint`, `repomap`, `rollback`, `hygiene`, `accept`, `status`, `web`).
- **Antigravity Skill Package (`.agents/skills/virtual-company/`)**:
  - `SKILL.md`: Skill metadata and Tier 0-3 Elastic Gateway triage rules.
  - `roles/`: 11 enterprise role prompts (`pm`, `architect`, `uiux_designer`, `dba`, `developer`, `code_reviewer`, `security_engineer`, `qa_engineer`, `doc_engineer`, `release_engineer`, `cto`).
  - `templates/`: Markdown and JSON templates for REQ, ADR, SPEC, Rejections, and Conventional Commits.
  - `workflows/`: Standard SOPs for Feature Delivery, Hotfix/Spike, and Circuit Breaker Arbitration.
- **Automated Test Suites (`tests/`)**:
  - 34 comprehensive automated tests covering state transitions, role permission lockdown, circuit breakers, gate evaluations, and CLI interactions with 100% pass rate.
- **Seed Architecture & Contracts (`docs/`)**:
  - `REQ-0001-system-init.md`: System requirement specification.
  - `ADR-0001-aegisflow-architecture.md`: Architecture decision record for checks-and-balances multi-agent studio.
  - `SPEC-0001-auth-contract.json`: JSON Schema authentication contract.
  - `PROJECT_STRUCTURE.md`: AST-generated codebase structural overview.
