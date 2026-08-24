---
name: symbol-table-builder
description: Build and maintain one global mathematical symbol and unit table from the problem frame and active method cards, resolving cross-subquestion conflicts before code or paper work.
---

# Purpose

Ensure the same concept uses one symbol and different concepts do not collide.

# Inputs

- problem parse and relationships;
- active `methods/Qx/qx_method_card.md`;
- approved code plans when available;
- question dependency map;
- existing `planning/symbol_table.md`.

Read legacy candidate pools only when method cards are absent.

# Workflow

1. Extract inputs, outputs, parameters, decisions, states, indices, sets, functions, and intermediate quantities.
2. Preserve user-established notation unless it conflicts or is ambiguous.
3. Resolve:
   - same meaning with different symbols;
   - different meanings with the same symbol;
   - unit/domain conflicts;
   - Qx output-to-input handoff conflicts.
4. Classify each symbol by role and scope.
5. Save or update `planning/symbol_table.md`.
6. If a canonical symbol changes, classify it `CANONICAL` and run scoped consistency for affected Qx.

# Table Fields

- symbol;
- plain name;
- definition;
- type: input, output, parameter, estimated parameter, decision, state, intermediate, index, set, function;
- domain/range;
- unit;
- scope/Qx;
- source artifact;
- notes or conflict resolution.

# Rules

- Define every symbol before first use.
- Record units and domains when applicable.
- Use one notation for cross-question handoffs.
- Do not invent variables to make a table look complete.
- Do not maintain a separate verbose conflict log; record material resolutions in the table notes.

# Verification

- Active method-card and code-plan variables are covered.
- No unresolved symbol or unit collision remains.
- Shared quantities agree across Qx.
- Downstream artifacts can cite one canonical table.
