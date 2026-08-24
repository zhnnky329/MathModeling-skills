# Layout Guide for Multi-Panel Mathematical Modeling Figures

## Panel Architecture Principles

Each panel in a multi-panel figure must answer a **unique** question. If two panels can be covered by the same sentence, one is redundant.

### The three-level model (adapted for math modeling)

| Level | Question | Visual Role | Typical Panel |
|-------|----------|-------------|---------------|
| **Overview** | What is the system / workflow? | Establish context | Workflow diagram, schematic, data overview |
| **Main Evidence** | What does the model produce? | Carry the primary claim | Ranking bar, prediction plot, optimization result |
| **Validation** | Is the result reliable? | Support with evidence | Sensitivity analysis, baseline comparison |

### Panel ordering conventions

Left-to-right, top-to-bottom reading order should match the argument flow:

```
Panel a (top-left)    → Establish the system or show the main result
Panel b (top-right)   → Secondary evidence or method detail
Panel c (bottom-left) → Validation or comparison
Panel d (bottom-right)→ Robustness or supplementary evidence
```

## Layout Patterns

### Pattern 1: Hero + validation (2×1 or 1.5:1 split)

```
┌──────────────────────────┬──────────┐
│                          │          │
│    Panel a (hero)        │ Panel b  │
│    Main result           │ Baseline │
│                          │ compare  │
└──────────────────────────┴──────────┘
```

Use when: one main result needs to dominate, with a smaller comparison panel. The hero panel is 1.5x to 2x wider.

```python
fig = plt.figure(figsize=(12, 6))
gs = fig.add_gridspec(1, 2, width_ratios=[1.6, 1])
```

### Pattern 2: Two-by-two grid (2×2)

```
┌──────────────────┬──────────────────┐
│                  │                  │
│    Panel a       │    Panel b       │
│    Final result  │    Method detail │
│                  │                  │
├──────────────────┼──────────────────┤
│                  │                  │
│    Panel c       │    Panel d       │
│    Comparison    │    Sensitivity   │
│                  │                  │
└──────────────────┴──────────────────┘
```

Use when: four distinct pieces of evidence are needed. Each panel is equal size. Most common pattern for contest papers.

```python
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
```

### Pattern 3: One-row comparison (1×3)

```
┌──────────┬──────────┬──────────┐
│          │          │          │
│ Panel a  │ Panel b  │ Panel c  │
│ Method 1 │ Method 2 │ Method 3 │
│          │          │          │
└──────────┴──────────┴──────────┘
```

Use when: comparing 3 methods on the same metric. All panels share the same axis scale.

```python
fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
```

### Pattern 4: Asymmetric (hero spans rows)

```
┌──────────────────┬──────────┐
│                  │ Panel b  │
│    Panel a       │ Detail   │
│    (hero)        ├──────────┤
│                  │ Panel c  │
│                  │ Validate │
└──────────────────┴──────────┘
```

Use when: a schematic or main result needs 50-60% of the figure area, with smaller supporting panels.

```python
fig = plt.figure(figsize=(12, 9))
gs = fig.add_gridspec(2, 2, width_ratios=[1.5, 1])
ax_hero = fig.add_subplot(gs[:, 0])  # spans both rows
ax_top = fig.add_subplot(gs[0, 1])
ax_bot = fig.add_subplot(gs[1, 1])
```

### Pattern 5: Full-width workflow + 2 results

```
┌──────────────────────────────────┐
│         Panel a (workflow)       │
├────────────────┬─────────────────┤
│   Panel b      │    Panel c      │
│   Result 1     │    Result 2     │
└────────────────┴─────────────────┘
```

Use when: a top-row workflow diagram establishes the context and two bottom panels show results.

```python
fig = plt.figure(figsize=(12, 8))
gs = fig.add_gridspec(2, 2, height_ratios=[0.8, 1.5])
ax_workflow = fig.add_subplot(gs[0, :])   # full width
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1])
```

## Spacing and Alignment

### Spacing rules

```python
fig.subplots_adjust(
    hspace=0.35,   # vertical space between rows
    wspace=0.30,   # horizontal space between columns
)
```

- Increase `hspace` if row titles overlap with the row above.
- Increase `wspace` if y-axis labels of left panel overlap with right panel.
- Use `tight_layout(pad=2)` at the end, which usually overrides `subplots_adjust`.

### Alignment rules

- When panels show the same metric, use `sharey=True` or manually set the same y-limits.
- When panels show different metrics, each gets its own y-axis with appropriate limits.
- X-axis labels should be horizontal or minimally rotated. Avoid vertical text.
- Tick label font sizes should be 1-2pt smaller than the base font size.
- Legend placement: inside the panel (preferred) or below. Avoid legends to the right for multi-panel figures (wastes horizontal space).

## Redundancy Checklist

Before finalizing a multi-panel figure, check:

- [ ] Panel `a` and panel `b` answer different questions.
- [ ] No two panels show the same data in different chart types (e.g., don't show the same ranking as both a bar chart AND a table).
- [ ] Each panel's title/label indicates what unique information it provides.
- [ ] Removing any panel would weaken the overall argument.
- [ ] Comparison panels compare on different criteria if there are multiple.
- [ ] Sensitivity panels each cover a different parameter.

## Common Layout Mistakes

| Mistake | Fix |
|---------|-----|
| All 4 panels show the same data from different angles | Keep 1-2, replace others with complementary evidence |
| Hero panel is the same size as supporting panels | Increase hero panel width (use `width_ratios`) |
| Panels with different y-axis scales invite false comparison | Either align scales or add visual separators |
| Legend takes up 30% of the figure | Use direct labels or move legend below the figure |
| Dense information in small panels → unreadable | Fewer panels with more space each |
| Empty space > 20% of the figure | Tighten with `bbox_inches='tight'` or adjust `figsize` |
