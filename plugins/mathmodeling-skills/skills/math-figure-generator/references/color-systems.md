# Color Systems for Mathematical Modeling Figures

## Design Philosophy

Color in mathematical modeling figures serves three purposes:
1. **Identity**: which method/data series is this?
2. **Direction**: is this better (+) or worse (-)?
3. **Hierarchy**: is this primary evidence or supporting information?

Every color choice should answer one of these. Avoid using color purely decoratively.

## Palette System

### Primary palette (hero + baseline)

```
PALETTE = {
    'primary':        '#1A6FC4',   # ═══ Your method / main series
    'primary_light':  '#5B9BD5',
    'primary_pale':   '#B4D4F0',
    'baseline':       '#767676',   # ─── Baseline / reference (always grey)
    'baseline_dark':  '#4D4D4D',
}
```

**Invariant**: `primary` is your method in every panel. `baseline` is always grey. These two colors never change meaning.

### Signal palette (direction only)

```
PALETTE_SIGNAL = {
    'positive':  '#2E9E44',    # ↑ improvement / gain / increase
    'negative':  '#E53935',    # ↓ degradation / loss / decrease
}
```

**Rule**: Use `positive`/`negative` ONLY for signed changes (deltas, differences, improvements). Never use them for general category coloring. A model that scores 0.8 is not "green" — it's "primary". A model that improved by 0.1 from baseline IS green.

### Accent palette (additional categories)

```
PALETTE_ACCENT = {
    'accent1': '#E28E2C',    # orange — secondary method or category
    'accent2': '#7B5FD6',    # purple — tertiary method or category
    'accent3': '#33B5A5',    # teal — quaternary
    'accent4': '#D9544D',    # coral — fifth
    'accent5': '#B89BD9',    # lavender — sixth
}
```

Use accents sequentially for additional methods or categories. If you have more than 6 categories, consider whether a grouped bar chart is the right visualization.

### Neutral palette (background, reference, grid)

```
PALETTE_NEUTRAL = {
    'neutral_bg':    '#F5F5F5',    # panel background
    'neutral_light': '#D8D8D8',    # reference lines, light bars
    'neutral_mid':   '#A8A8A8',    # gridlines, secondary text
    'neutral_dark':  '#606060',    # axis text, tick labels
    'neutral_black': '#333333',    # title, primary text
}
```

### Unified comparison palette (for multi-method families)

When comparing related methods (e.g., "our method" family with variants):
```
PALETTE_COMPARISON = {
    'method1_dark':  '#1A6FC4',    # main method
    'method1_mid':   '#5B9BD5',    # main method variant
    'method1_light': '#B4D4F0',    # main method simplified
    'method2_dark':  '#E28E2C',    # competing method
    'method2_mid':   '#F0B860',    # competing method variant
    'method2_light': '#F5D9A0',
    'delta_up':      '#2E9E44',
    'delta_down':    '#E53935',
}
```

## Color Consistency Rules

1. **Same method = same color**. If "Entropy-TOPSIS" is blue (`#1A6FC4`) in panel a, it must be blue in panel b, c, and d. Do not recolor it orange for contrast.

2. **Baseline is always grey**. Equal-weight scoring, moving average, greedy heuristic — whatever the baseline is, it gets `#767676`.

3. **Direction colors are reserved**. Green (`#2E9E44`) means "went up/improved". Red (`#E53935`) means "went down/degraded". If your plot doesn't show a directional change, don't use these colors.

4. **Saturation encodes confidence**. Full saturation for primary results. Lower saturation for secondary/supporting information.

5. **Luminance encodes hierarchy**. Dark = important (hero method, main finding). Light = supporting (reference, background, alternative).

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Each panel uses different colors for the same method | Pick one color per method and reuse everywhere |
| Green used for "Method A" and red for "Method B" just to differentiate | Use blue/orange/purple for identity; reserve green/red for deltas |
| All bars equally bright and equally important | Darken the hero method, lighten supporting bars |
| Too many colors (8+ distinct hues) | Group related items with shared hue, varied saturation |
| Grey used for the main method, bright color for baseline | Invert: main method gets the strong color, baseline gets grey |

## Choosing a Palette for Your Figure

1. **Single method + baseline**: Use `primary` + `baseline`.
2. **2-3 competing methods**: Use `primary` (your best) + `accent1` + `accent2`. Baseline stays grey.
3. **Method family comparison** (e.g., Tiny/Base/Large variants): Use `PALETTE_COMPARISON` with one hue family per method.
4. **Sensitivity/robustness**: Use `primary` for the baseline parameter value, `primary_light` for perturbations.
5. **Multi-panel with many categories**: Consider whether a heatmap or radar chart would be clearer than a bar chart with many colors.
