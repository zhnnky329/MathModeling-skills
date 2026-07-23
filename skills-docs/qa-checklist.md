# QA Checklist

This document provides a final checklist before assembling or submitting a mathematical modeling contest paper.

QA should find blockers. It should not hide them.

## Final decision

Use three possible QA states:

- `passed`: final assembly is allowed
- `passed_with_warnings`: final assembly is allowed, but limitations should remain visible
- `failed`: final assembly is blocked

If any required subquestion is unanswered, QA fails.

## Workflow completeness (must pass for all Qx)

For each subquestion, check:

- [ ] Manifest exists (`planning/manifests/Qx.json`)
- [ ] Method card exists (`methods/Qx/qx_method_card.md`)
- [ ] Human decision ledger exists (`methods/Qx/qx_decisions.jsonl`)
- [ ] Risk-probe summary exists (`methods/Qx/probes/risk_probe_summary.json`)
- [ ] Final experiment `run_summary.json` exists
- [ ] Language review JSON exists with all required named checks passing
- [ ] Final method explanation exists (`methods/Qx/qx_final_method_explanation.md`)  ← Rule 1
- [ ] Final result analysis exists (`results/Qx/reports/qx_final_result_analysis.md`)  ← Rule 2
- [ ] Solution package exists (`results/Qx/reports/qx_solution_package_for_writer.md`)  ← Rule 3
- [ ] Robustness report exists (`robustness/Qx/qx_robustness_report.md`) or justified exception
- [ ] Figure-table plan exists (`methods/Qx/qx_figure_table_plan.md`)

## Problem coverage

Check:

- every original subquestion is listed
- every subquestion has a corresponding answer
- every answer has a model, result, or justified non-model response
- dependencies between subquestions are handled
- final conclusions map back to the original problem

Blocking issues:

- missing subquestion
- wrong interpretation of a subquestion
- conclusion does not answer the question asked

## Method consistency

Check:

- task type matches the chosen method
- paper's method description matches the final method explanation and approved method card
- baseline exists for every main model unless justified
- conditional fallback is dormant unless its recorded trigger fired
- eliminated methods are mentioned appropriately
- rejected methods are not later described as used

Blocking issues:

- paper describes a different method than the final method explanation
- main model has no baseline and no justification
- method cannot produce the required output

## Data consistency

Check:

- raw data remains unchanged
- cleaned data is documented
- field meanings and units are clear
- missing values and outliers are handled or discussed
- data used in scripts matches the canonical data profile
- derived features are explained

Blocking issues:

- required data field missing
- raw data overwritten
- undocumented cleaning changes results materially
- unit mismatch affects interpretation

## Code and result consistency

Check:

- scripts exist under `code/Qx/` or `code/matlab/Qx/`
- run instructions are available in `qx_code_plan.md`
- output files follow `experiments/roundN/` structure
- `run_summary.json` exists for every executed round
- successful runs do not need full logs; failures and reproducibility warnings retain them
- paper numbers match result files
- random seeds are fixed when needed

Blocking issues:

- result in paper cannot be found in output files
- code output contradicts paper text
- script cannot be mapped to any subquestion
- runtime failure blocks required result

## Baseline and robustness

Check:

- baseline result exists where needed
- main model is compared with baseline
- robustness or sensitivity checks exist per subquestion
- fragile conclusions are marked
- robustness claims do not exceed completed checks
- conclusion boundaries are stated

Blocking issues:

- claim of improvement without baseline
- claim of stability without robustness check
- planned robustness check presented as completed

## Figures and tables

Check:

- every referenced figure exists or is clearly marked as planned
- every referenced table exists
- every figure or table has a source artifact
- paper figures are Type 3 (论文图) — no Type 1 (诊断图) accidentally in the paper
- captions explain the takeaway
- visual evidence supports the related claim
- no decorative figure is used as evidence

Blocking issues:

- figure or table referenced but missing
- table contains invented values
- figure contradicts result file
- visual overstates the evidence

## Paper writing

Check:

- assumptions are necessary and linked to modeling needs
- notation is defined before use and consistent with global symbol table
- equations match variables and units
- numerical claims have artifacts
- method description matches final method explanation (not candidate pool)
- results come from final result analysis (not raw experiment outputs)
- limitations are included
- conclusion does not introduce new claims
- abstract does not overstate results

Blocking issues:

- unsupported numerical claim
- invented reference or result
- hidden limitation that affects the conclusion
- conclusion exceeds evidence

## Anti-fabrication

Check:

- no fabricated data, references, results, figures, or experiments
- no invented numerical values
- no unsupported superiority claims
- no hidden uncertainty
- no decorative figures presented as evidence

## Artifact traceability

For each major claim, identify at least one supporting artifact:

| Claim type | Expected artifact |
|------------|-------------------|
| problem interpretation | problem parse |
| method choice | human decision ledger + final method explanation |
| data statement | `workspace/data_clean/data_profile.json` |
| numerical result | `frozen_numbers.json` + canonical result file |
| figure claim | figure source file |
| robustness claim | robustness report under `robustness/Qx/` |
| code-based result | reviewed script and output + `run_summary.json` |
| final conclusion | paper section plus supporting result |
| reference | `paper/refs.bib` entry + reference audit |

If the artifact cannot be found, the claim should be removed or marked incomplete.

## Repair routing

Use the earliest skill that can fix the issue.

| Issue | Repair skill |
|-------|-------------|
| problem misunderstood | `problem-parser` |
| wrong task type | `problem-classifier` |
| method does not fit task or data | `method-selector` |
| symbol conflict across subquestions | `symbol-table-builder` |
| missing or conflicting assumptions | `model-assumptions-builder` |
| data issue | `data-auditor-cleaner` |
| missing method explanation (Rule 1) | `final-method-explainer` |
| missing result analysis (Rule 2) | `result-report-generator` |
| missing solution package (Rule 3) | `solution-package-builder` |
| missing result generation | code generators |
| code or output mismatch | `code-reviewer` |
| missing robustness evidence | `robustness-checker` |
| unsupported visual | `figure-table-planner` |
| missing or low-quality figure | `math-figure-generator` |
| unsupported or unclear writing | `paper-section-writer` |
| language or overclaim issues | `paper-polisher` |
| unverified or fabricated citation | `reference-manager` |
| multiple blockers across stages | `workflow-orchestrator` |

## Practical rule

If QA fails, do not assemble the final paper.

Fix the earliest blocker first.
