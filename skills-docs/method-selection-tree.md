# Method Selection Guide

This is a family-routing reference, not a candidate quota or automatic recommendation table. The current role and gate contract is defined by `AGENTS.md`.

## Start with the required output

For each subquestion identify:

1. the required decision, prediction, explanation, ranking, or simulation output;
2. the available data and its coverage;
3. hard constraints, units, time budget, and interpretability needs;
4. how success and failure will be observed.

Only then screen method families.

| Task structure | Families worth screening | Typical failure risks |
|---|---|---|
| Evaluation or ranking | transparent scoring, TOPSIS/grey/fuzzy methods, dimension reduction | arbitrary weights, duplicated indicators, concentrated rankings |
| Prediction | naive/seasonal baseline, regression, tree or time-series models | leakage, weak holdout, nonstationarity, small samples |
| Optimization | feasible heuristic, linear/integer/nonlinear/robust optimization | infeasible baseline, hidden constraints, scale and solver sensitivity |
| Mechanism modeling | balance laws, differential/difference equations, system dynamics | unidentifiable parameters, unit errors, unsupported assumptions |
| Classification or clustering | majority/simple rule baseline, interpretable classifiers, clustering | imbalance, label leakage, unstable clusters |
| Graph or routing | shortest-path/greedy baseline, flow/routing optimization | disconnected graphs, capacity violations, brittle edge weights |
| Simulation | deterministic scenario reference, Monte Carlo, discrete-event/agent simulation | too few trials, seed sensitivity, uncalibrated behavior |
| Data analysis | descriptive baseline, regression/correlation, PCA or anomaly analysis | spurious correlation, outlier dominance, subgroup imbalance |

## Role-based shortlist

Build:

- one `main_candidate` that directly answers the question;
- one `usable_baseline` that is runnable, explainable, and produces a meaningfully comparable output;
- at most one `conditional_fallback`, with a measurable trigger.

A diagnostic reference may be useful for debugging but cannot stand in for the usable baseline.

## Risk probe

The probe is method-specific and may contain code, analytical checks, or both. It must cover every applicable item:

- execution on the intended data path;
- coverage of important groups, time ranges, or constraints;
- method-specific assumptions;
- output degeneracy or concentration;
- one targeted perturbation;
- size and runtime risk.

Predeclare warning/failure criteria where possible. A small slice that merely runs is insufficient.

## Human choice

Show a compact comparison card after the evidence is available. Ask only questions that materially change the method, trade-off, or fallback decision. Record the exact answer in `methods/Qx/qx_decisions.jsonl`.

The AI may summarize evidence and, in speed mode, make a labeled suggestion. It must not silently choose for the modeler.

## Complexity rule

Increase complexity only when a measured failure of the baseline or simpler main candidate justifies it. If the complex option is hard to implement, validate, or explain within the contest budget, demote it to a conditional fallback or omit it.
