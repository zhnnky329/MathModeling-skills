# Render Check

Inspect the rendered image or PDF page, not only the plotting code.

## Required checks

- no clipped title, axis label, legend, annotation, or colorbar;
- no overlapping labels that obscure values;
- readable font size at final placement dimensions;
- correct units, ordering, scales, and category labels;
- no empty or unintended subplot;
- color and marker distinctions survive grayscale or common color-vision deficiencies;
- uncertainty, baseline, and main method are identified correctly;
- caption and visual support the same claim;
- source row/count/metric agrees with the canonical data artifact;
- Type 3/4 output exists under `paper/figures/`.

Record failures concisely and rerender after correction.
