---
name: RIM Core Rules
description: Enforces the core architectural rules, schema boundaries, and environment execution standards for the Risk Influence Map (RIM) project. You MUST use this skill for ALL coding and command execution tasks in this repository.
---

# RIM Core Rules

This skill enforces adherence to the project's foundational architectural rules.

## Core Instruction
Whenever you are asked to generate code, run a command, or analyze the graph architecture in this repository, you **MUST** first read the root document: `AGENT_RULES_AND_CONTEXT.md`.

This document contains critical rules regarding:
1. **The Computational Engine Boundary**: Understanding the strict difference between core types (BusinessRisk, OperationalRisk, Mitigation) and ContextNodes.
2. **Scope Completeness**: Enforcing subgraph isolation correctly in all queries and UI components.
3. **Pydantic Validation**: All new data ingestion must be validated.
4. **Virtual Environment Execution**: All Python and pytest commands must be prefixed with `.\venv\Scripts\activate;`.

Do not attempt to write code, modify the schema, or run commands without adhering to the rules specified in `AGENT_RULES_AND_CONTEXT.md`.

## Standard Development Finalization Steps
At the end of any development task or feature implementation, you **MUST** implicitly complete the following sequence:

1. **Automated Testing**: Execute the automated test suite. If the feature warrants it, write new pytest functions covering the changes before running them.
2. **Manual Validation**: Document the specific actions a human should perform to manually validate your updates within the `walkthrough.md` artifact.
3. **Update Documentation**: Identify and update all necessary documentation files including `CHANGELOG.md`, `README.md`, `ROADMAPv2.md`, and any relevant markdown files in the `docs/` folder.
4. **Git Commit Text**: Finally, generate and provide the user with the recommended text for the git commit.
