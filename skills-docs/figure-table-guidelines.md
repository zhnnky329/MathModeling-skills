# Figure and Table Guidelines

This document explains how to plan figures and tables for a mathematical modeling contest paper.

Figures and tables should support the argument. They should not be used as decoration.

## Basic rule

Every figure or table should answer three questions:

1. What claim does it support?
2. Which artifact is its source?
3. Where will it appear in the paper?

If these questions cannot be answered, the figure or table is probably not needed.

## Figure types

### Workflow figure

Use for:

- overall modeling pipeline
- subquestion dependency
- data-to-result process
- algorithm flow

A workflow figure should show real transformations. Avoid vague blocks such as “analyze data” or “build model” unless they are made specific.

### Principle figure

Use for:

- mechanism explanation
- geometric relationship
- state transition
- variable interaction
- model structure

A principle figure should clarify a formula, assumption, or system relationship. It should not replace the derivation.

### Result figure

Use for:

- trends
- rankings
- prediction vs actual
- residuals
- spatial patterns
- baseline vs main model comparison

A result figure must come from model output files.

It should have:

- clear axes
- units where relevant
- readable labels
- a specific takeaway

### Robustness figure

Use for:

- sensitivity curves
- ranking stability
- perturbation effects
- error distribution
- seed stability
- constraint sensitivity

A robustness figure must come from completed checks. Planned checks should not be shown as completed evidence.

## Table types

### Data summary table

Use for:

- field names
- units
- missing values
- descriptive statistics
- preprocessing actions

This table should match the data audit report.

### Symbol table

Use for:

- variables
- parameters
- sets
- indices
- units
- definitions

Separate decision variables, state variables, parameters, inputs, and outputs when relevant.

### Model result table

Use for:

- scores
- rankings
- predictions
- optimal decisions
- objective values
- parameter estimates

Every number should trace back to a result file.

### Comparison table

Use for:

- baseline vs main model
- method alternatives
- scenario comparison
- before/after comparison

State the comparison criteria clearly.

### Sensitivity table

Use for:

- weight perturbation
- parameter perturbation
- constraint changes
- scenario results

The table should include the perturbation setting and the effect on conclusions.

## Captions

A good caption should explain what the reader should learn.

Weak caption:

```text
Figure 3. Prediction result.
```

Better caption:

```text
Figure 3. Actual and predicted demand on the test period. The main model follows the short-term trend but underestimates the last two high-demand points.
```

Captions should not exaggerate what the figure shows.

## **Common mistakes**

Avoid:

- figures with no source artifact
- tables with invented values
- decorative flowcharts
- repeated figures that show the same information
- unreadable axes or legends
- figures that imply stronger conclusions than the results support
- robustness plots based on planned but unrun checks
- result tables that do not match the paper text

## **Minimum figure-table plan**

A useful figure-table plan should include:

```json
{
  "planned_figures": [
    {
      "id": "Fig.1",
      "type": "workflow",
      "title": "Modeling workflow",
      "source_artifacts": [
        "methods/Q1/q1_method_card.md"
      ],
      "paper_section": "Model overview",
      "supports_claim": "The solution follows a staged modeling pipeline."
    }
  ],
  "planned_tables": [
    {
      "id": "Table 1",
      "type": "model_result_table",
      "title": "Q1 scores and rankings",
      "source_artifacts": [
        "results/Q1/experiments/round1/tables/q1_main_results.csv"
      ],
      "paper_section": "Q1 results",
      "supports_claim": "The evaluation model produces comparable scores and rankings."
    }
  ]
}
```

## **Practical rule**

Use tables when exact values matter.

Use figures when patterns, trends, comparisons, or stability need to be seen.
