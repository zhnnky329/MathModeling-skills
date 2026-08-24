---
name: matlab-code-reviewer
description: Review, run, debug, and verify approved MATLAB or Beita Tianyuan modeling code against its plan, data contract, method decision, compatibility constraints, and experiment outputs, saving one compact JSON review.
---

# Preconditions

- MATLAB code and `code/matlab/Qx/qx_code_plan.md` exist.
- Approved decision, method card, data profile, and run summary are available.
- MATLAB or 北太天元 runtime availability is known.

# Workflow

1. Resolve approved main/baseline scope and any activated fallback.
2. Inspect and run the code when a compatible runtime is available.
3. Evaluate:
   - `syntax`
   - `input_contract`
   - `method_alignment`
   - `reproducibility`
   - `output_contract`
4. Include compatibility evidence for toolbox usage, `jsonencode`, file I/O, plotting/export, and 北太天元 constraints.
5. Add only relevant numerical, feasibility, leakage, or scale checks.
6. If runtime is unavailable, use `NOT_RUN` rather than claiming execution success.
7. If asked to fix findings, patch minimally and rerun affected checks.
8. Save `code/matlab/Qx/reviews/qx_matlab_review.json`.

# Review Schema

Use the same schema as `python-code-reviewer`, with:

- `"language": "matlab"`
- `runtime`
- `compatibility_target`
- optional `compatibility` check

Required named checks use `PASS`, `FAIL`, or justified `NOT_APPLICABLE`. Runtime-dependent checks use `NOT_RUN` when execution was impossible; this blocks G3 until executed.

# Rules

- Do not pad pass items.
- Do not fabricate MATLAB/北太天元 execution.
- Do not approve unavailable toolbox dependencies without an explicit target exception.
- Do not change the mathematical model silently.
- Do not require a duplicate Markdown review.

# Verification

- Approved main and baseline scope is enforced.
- Compatibility constraints are checked.
- Run summary and outputs agree.
- Verdict follows required check statuses and runtime evidence.
