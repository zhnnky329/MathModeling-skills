# Implementation Targets

The modeling workflow stays language-neutral until implementation. It supports:

- `python`
- `matlab`, including MATLAB / 北太天元-compatible code

北太天元 is a MATLAB runtime constraint, not a third target.

## Select the target

Record the target in `methods/Qx/qx_method_card.md`:

```json
{
  "implementation": {
    "target": "matlab",
    "runtime_notes": [
      "beita-tianyuan-compatible",
      "avoid-heavy-toolboxes"
    ],
    "random_seed_required": true
  }
}
```

Choose the target from runtime availability, team skill, dependency limits, and required deliverable format. Do not let the language choice change the approved mathematical method.

## Workflow

```text
model-code-analyzer
→ python-model-code-generator | matlab-model-code-generator
→ code-reviewer
→ result-report-generator
→ robustness-checker
```

`model-code-analyzer` plans only the human-approved main method and usable baseline. A conditional fallback is implemented only after its trigger is observed and activation is recorded.

## Paths

```text
Python: code/Qx/
MATLAB: code/matlab/Qx/

results/Qx/experiments/roundN/
├── figures/
├── tables/
├── metrics/
└── run_summary.json
```

Create `logs/` only for failures, warnings, or reproduction needs.

The run summary must identify the approved decision, method roles, scripts, inputs, outputs, comparable metrics, seed, environment, output-degeneracy evidence, fallback state, warnings, and errors.

## Compatibility

For Python:

- prefer a small dependency set and portable scripts;
- avoid notebook-only execution;
- save CSV, JSON, and image artifacts;
- record package versions that affect reproducibility.

For MATLAB / 北太天元:

- prefer basic matrix and table operations;
- avoid Live Scripts, GUI code, Simulink, and optional toolboxes unless approved;
- use portable files for handoff;
- record unverified runtime compatibility honestly.

Mixed-language work is allowed only when the handoff files and official computation source are explicit.

## Practical rule

Keep code language-specific, results language-neutral, and every claim traceable to saved evidence rather than console output.
