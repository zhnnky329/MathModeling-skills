# MATLAB / 北太天元 Guidelines

Use `matlab` as the implementation target and record 北太天元 as a runtime constraint:

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

Do not create a separate target or change the approved mathematical method to fit a favorite function.

## Scope and paths

After the human method choice, implement only the approved main and usable baseline. Add a conditional fallback only after its trigger is observed and activation is recorded.

```text
code/matlab/Qx/
├── qx_code_plan.md
├── qx_baseline.m
├── qx_main.m
└── run_all.m          # optional

results/Qx/experiments/roundN/
├── figures/
├── tables/
├── metrics/
└── run_summary.json
```

Create `logs/` only for failures, warnings, or reproduction needs. Treat `workspace/data_raw/` as read-only and read cleaned inputs from `workspace/data_clean/`.

## Conservative compatibility

Prefer:

- plain `.m` scripts and small explicit helpers;
- basic matrix and table operations;
- `readtable`, `readmatrix`, `writetable`, `writematrix`, `load`, and `save`;
- `fullfile` for paths;
- portable CSV, MAT, JSON, PNG, or PDF artifacts;
- a fixed seed such as `rng(2026)` when randomness is used.

Avoid unless explicitly approved and verified:

- Live Scripts, App Designer, GUI code, and Simulink;
- optional or specialized toolboxes;
- version-specific syntax;
- interactive workspace state;
- hard-coded local absolute paths.

If a required function is unavailable, either implement a transparent compatible alternative without changing the model, or return to the method decision. Never claim an unexecuted run succeeded.

## Array and table checks

Review:

- row/column-vector orientation and matrix dimensions;
- element-wise versus matrix operators;
- 1-based indexing and loop boundaries;
- column-name transformations;
- units, indicator directions, missing-value handling, and preserved rows;
- solver exit state and constraint feasibility where applicable.

Do not silently rename important fields, discard records, or hide assumptions inside code.

## Directly comparable outputs

The baseline and main method must use the same input scope and produce the same output type or a justified comparison mapping. Save their artifacts separately:

```text
tables/qx_baseline_results.csv
tables/qx_main_results.csv
metrics/qx_comparison.json
```

A diagnostic reference does not count as the baseline. Evaluate the output-degeneracy/concentration measures and fallback trigger specified by the code plan.

## Run summary

`run_summary.json` records:

- question, round, runtime, environment, and seed;
- approved decision ID;
- main and baseline roles, scripts, status, runtime, inputs, outputs, metrics, warnings, and errors;
- direct comparison;
- output concentration or degeneracy;
- fallback trigger and activation state.

Console output alone is not evidence.

## Minimal script pattern

```matlab
% Q1 approved main model
% Input and output paths are defined in q1_code_plan.md.
clear; clc; close all;
rng(2026);

dataDir = fullfile('workspace', 'data_clean');
roundDir = fullfile('results', 'Q1', 'experiments', 'round1');
tableDir = fullfile(roundDir, 'tables');
figureDir = fullfile(roundDir, 'figures');

if ~exist(tableDir, 'dir'), mkdir(tableDir); end
if ~exist(figureDir, 'dir'), mkdir(figureDir); end
```

Use comments for non-obvious formulas, inherited assumptions, compatibility constraints, and artifact paths—not for trivial syntax.

## Blockers

Stop and return upstream when:

- the human method choice or code plan is missing;
- target/runtime constraints are unresolved;
- required cleaned fields are absent;
- a toolbox dependency is unsupported;
- main and baseline cannot be compared;
- the required output cannot be saved;
- a code fix would alter the mathematical model.

The preferred contest implementation is the simplest reviewable compatible script that produces traceable evidence.
