---
name: code-reviewer
description: Detect whether approved modeling code is Python or MATLAB/Beita Tianyuan and route it to the matching reviewer using the compact named-check review contract.
---

# Workflow

1. Inspect target code extensions and the implementation target in `qx_code_plan.md`.
2. Route `.py` work to `python-code-reviewer`.
3. Route `.m` work to `matlab-code-reviewer`.
4. If both languages are intentionally present, review each separately.
5. If the language or target is ambiguous, report the exact conflict.

# Review Contract

New reviews write JSON and evaluate these named checks:

- `syntax`
- `input_contract`
- `method_alignment`
- `reproducibility`
- `output_contract`

Additional checks are allowed when risk-driven. A review passes when all required applicable checks pass; no arbitrary bullet count is used.

# Rules

- Do not perform a second independent review in this router.
- Do not infer success because scripts exist.
- Do not require a Markdown review when the canonical JSON review exists.
- Read legacy Markdown reviews only for compatibility.
