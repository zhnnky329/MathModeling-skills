---
name: math-figure-generator
description: Generate and render-verify publication-quality mathematical-modeling figures from saved evidence, using the approved figure plan, source data, claim, type, and consistent visual system.
---

# Preconditions

- Figure type, source artifacts, and target claim are known.
- Type 3 claim is human-confirmed.
- Submission figures use final/frozen evidence.

# References

Load only what the requested chart needs:

- `references/chart-patterns.md`
- `references/color-systems.md`
- `references/layout-guide.md`
- `references/render-check.md`

# Workflow

1. Verify source files and the exact variables/units to plot.
2. Choose the smallest chart form that communicates the claim.
3. Generate with deterministic code, preferably matplotlib.
4. Save editable source code and the requested output format.
5. Apply the shared color, typography, sizing, and labeling conventions.
6. Render the final output and inspect it visually.
7. Check clipping, overlap, illegible text, misleading axes, legends, empty panels, and source/claim mismatch.
8. Iterate until render checks pass.

# Output Locations

- Type 1/2 exploration: `results/Qx/experiments/roundN/figures/`
- Type 3/4 submission: `paper/figures/`

Use stable descriptive filenames. Do not copy Type 1 diagnostics into the paper directory.

# Figure Requirements

- Labels include units where applicable.
- Captions state what is shown and the evidence-backed takeaway without overstating causality.
- Baseline is visually distinct but not exaggerated.
- Uncertainty is shown when it is part of the claim.
- Type 3 raster output is at least 300 dpi; vector output is preferred when compatible.
- Accessibility and grayscale differentiation are considered.

# Rules

- Do not fabricate or manually alter plotted values.
- Do not use a chart type that hides concentration, uncertainty, or negative results.
- Do not truncate axes misleadingly.
- Do not create decorative 3D effects.
- Do not treat code execution as render verification.
- Keep diagnostic and paper roles separate.

# Verification

- Source, claim, type, and target section agree.
- Render inspection passed.
- Text is readable at final paper size.
- Legends, colors, markers, axes, units, and captions are consistent.
- Final output path exists and is recorded in the figure plan.
