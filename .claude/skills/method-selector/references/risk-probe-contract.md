# Risk Probe Contract

Use only checks relevant to the method, but always cover executability, representative data coverage, output degeneracy, small perturbations, and scale.

## Canonical summary

Save `methods/Qx/probes/risk_probe_summary.json`:

```json
{
  "schema_version": 1,
  "question_id": "Q1",
  "generated_at": "ISO-8601",
  "data_refs": ["workspace/data/data_report.md"],
  "methods": [
    {
      "id": "M1",
      "role": "usable_baseline",
      "executability": {
        "status": "PASS",
        "evidence": {"runtime_seconds": 0.2}
      },
      "data_coverage": {
        "status": "PASS",
        "evidence": {
          "rows_used": 420,
          "effective_sample_size": 398,
          "missing_rate": 0.01
        }
      },
      "assumption_checks": [
        {
          "name": "multicollinearity",
          "status": "CONDITIONAL",
          "metric": "max_vif",
          "value": 8.3,
          "threshold": 10
        }
      ],
      "output_degeneracy": {
        "status": "PASS",
        "metrics": {
          "unique_output_count": 37,
          "coefficient_of_variation": 0.18,
          "top_k_mass": 0.22
        }
      },
      "perturbation_sensitivity": {
        "status": "PASS",
        "perturbation": "weights +/- 5%",
        "metric": "top_10_overlap",
        "value": 0.9
      },
      "scale_check": {
        "status": "PASS",
        "representative_n": 420,
        "runtime_seconds": 0.2,
        "peak_memory_mb": 35
      },
      "verdict": "PASS",
      "conditions": [],
      "evidence_refs": []
    }
  ]
}
```

## Representative data

- Do not default to the first N rows.
- Preserve chronological order for forecasting probes.
- Use stratified or distribution-covering samples for imbalanced data.
- Use the full dataset for inexpensive distribution and concentration diagnostics.
- Record the selection rule and row count.

## Method-specific checks

- Evaluation/ranking: indicator redundancy, weight dominance, score variance, unique ranks, top-k mass, rank overlap under normalization/weight perturbations.
- Prediction: leakage, split validity, stationarity where assumed, residual behavior, interval coverage, baseline error, extrapolation limits.
- Optimization: constraint feasibility, slack, integrality, sensitivity to costs/capacities, solution implementability, runtime scaling.
- Clustering/classification: class or cluster imbalance, separation, label availability, calibration, stability across seeds.
- Mechanism models: units, identifiability, boundary/initial conditions, conservation, parameter sensitivity.
- Simulation: seed control, number of replications, distribution assumptions, confidence interval stability.

## Interpretation

- Prefer several cheap targeted checks over one impressive but weakly related metric.
- A concentration metric needs a problem-specific interpretation; low variance is not automatically bad when the expected truth is genuinely concentrated.
- Record thresholds before using them as pass/fail criteria, or label the verdict `CONDITIONAL`.
