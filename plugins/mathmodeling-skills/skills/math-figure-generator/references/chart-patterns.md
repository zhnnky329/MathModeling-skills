# Extended Chart Pattern Gallery

Complete, runnable code patterns for every chart type in mathematical modeling contests.

## 1. Evaluation & Ranking

### Simple ranking bar (horizontal)

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'

PALETTE = {
    'primary': '#1A6FC4', 'baseline': '#767676',
    'positive': '#2E9E44', 'negative': '#E53935',
}

def plot_ranking(ax, names, scores, title='', highlight_n=3):
    """Sorted horizontal bar showing ranking. Top-N highlighted in primary color."""
    sorted_idx = np.argsort(scores)[::-1]
    names = [names[i] for i in sorted_idx]
    scores = [scores[i] for i in sorted_idx]
    colors = [PALETTE['primary'] if i < highlight_n else PALETTE['baseline']
              for i in range(len(names))]
    y = range(len(names))
    ax.barh(y, scores, color=colors, edgecolor='white', linewidth=0.5, height=0.65)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel('Score')
    ax.set_title(title)
    # Annotate top-N
    for i in range(min(highlight_n, len(scores))):
        ax.text(scores[i] + 0.01, i, f'{scores[i]:.4f}', va='center', fontsize=8)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

### TOPSIS score distribution

```python
def plot_topsis_distribution(ax, names, scores, threshold=None):
    """Scatter + horizontal line showing closeness scores."""
    sorted_idx = np.argsort(scores)[::-1]
    names_sorted = [names[i] for i in sorted_idx]
    scores_sorted = [scores[i] for i in sorted_idx]
    x = range(len(names_sorted))
    colors = [PALETTE['primary'] if s > (threshold or np.median(scores_sorted))
              else PALETTE['baseline'] for s in scores_sorted]
    ax.scatter(x, scores_sorted, c=colors, s=40, zorder=5, edgecolors='white', linewidth=0.5)
    for i, name in enumerate(names_sorted):
        ax.annotate(name, (i, scores_sorted[i]), textcoords="offset points",
                    xytext=(0, 8), ha='center', fontsize=6, rotation=45)
    if threshold:
        ax.axhline(y=threshold, color=PALETTE['negative'], linestyle='--',
                   linewidth=1, alpha=0.6, label=f'Threshold = {threshold:.2f}')
        ax.legend()
    ax.set_ylabel('Closeness Score')
    ax.set_xticks([])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

## 2. Prediction

### Multi-step forecast with confidence band

```python
def plot_forecast(ax, hist_time, hist_values, forecast_time, forecast_mean,
                  forecast_lower=None, forecast_upper=None,
                  hist_label='Historical', forecast_label='Forecast'):
    """Historical data + forecast with optional confidence band."""
    ax.plot(hist_time, hist_values, color=PALETTE['primary'], linewidth=2,
            marker='o', markersize=4, label=hist_label)
    ax.plot(forecast_time, forecast_mean, color=PALETTE['positive'], linewidth=2,
            marker='s', markersize=4, label=forecast_label)
    if forecast_lower is not None and forecast_upper is not None:
        ax.fill_between(forecast_time, forecast_lower, forecast_upper,
                        color=PALETTE['positive'], alpha=0.15)
    # Vertical separator between history and forecast
    sep_x = (hist_time[-1] + forecast_time[0]) / 2 if len(hist_time) > 0 else forecast_time[0]
    ax.axvline(x=sep_x, color=PALETTE['baseline'], linestyle=':', linewidth=1, alpha=0.7)
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

### Residual diagnostic plot

```python
def plot_residuals(ax, predicted, actual):
    """Residuals vs predicted values for model diagnostics. Type 1 diagnostic figure."""
    residuals = actual - predicted
    ax.scatter(predicted, residuals, c=PALETTE['primary'], s=25, alpha=0.6,
               edgecolors='white', linewidth=0.5)
    ax.axhline(y=0, color=PALETTE['baseline_dark'], linestyle='--', linewidth=1)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Residual')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

## 3. Optimization

### Resource allocation stacked bar

```python
def plot_allocation_stacked(ax, regions, allocations_dict, xlabel='Region', ylabel='Allocation'):
    """Stacked bar chart for resource allocation across regions."""
    bottom = np.zeros(len(regions))
    colors = ['#1A6FC4', '#5B9BD5', '#B4D4F0', '#E28E2C', '#F0B860']
    for i, (label, values) in enumerate(allocations_dict.items()):
        ax.bar(regions, values, bottom=bottom, label=label,
               color=colors[i % len(colors)], edgecolor='white', linewidth=0.5)
        bottom += np.array(values)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

### Cost vs constraint sensitivity

```python
def plot_constraint_sensitivity(ax, constraint_values, objective_values,
                                 constraint_name='Constraint', objective_name='Objective'):
    """How the objective changes as a constraint is varied."""
    ax.plot(constraint_values, objective_values, color=PALETTE['primary'],
            linewidth=2, marker='o', markersize=5)
    ax.set_xlabel(constraint_name)
    ax.set_ylabel(objective_name)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

## 4. Comparison & Robustness

### Baseline vs main model side-by-side

```python
def plot_baseline_comparison(ax, metrics, baseline_values, main_values,
                              metric_labels=None, ylabel='Value'):
    """Paired bar chart comparing baseline and main model across metrics."""
    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(x - width/2, baseline_values, width, label='Baseline',
           color=PALETTE['baseline'], edgecolor='white', linewidth=0.5)
    ax.bar(x + width/2, main_values, width, label='Main Model',
           color=PALETTE['primary'], edgecolor='white', linewidth=0.5)
    # Improvement annotation
    for i, (b, m) in enumerate(zip(baseline_values, main_values)):
        if m != b:
            pct = (m - b) / abs(b) * 100 if b != 0 else 0
            color = PALETTE['positive'] if pct > 0 else PALETTE['negative']
            arrow = '↑' if pct > 0 else '↓'
            ax.annotate(f'{arrow}{abs(pct):.0f}%', (x[i], max(b, m)),
                        textcoords="offset points", xytext=(0, 4),
                        ha='center', fontsize=7, color=color)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics if metric_labels is None else metric_labels)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

### Weight sensitivity line plot

```python
def plot_weight_sensitivity(ax, perturbation_levels, rankings_matrix, top_n=5,
                             labels=None):
    """Track ranking changes as weights are perturbed. One line per alternative."""
    colors = ['#1A6FC4', '#E28E2C', '#2E9E44', '#7B5FD6', '#33B5A5']
    for i in range(min(top_n, rankings_matrix.shape[1])):
        label = labels[i] if labels else f'Rank {i+1}'
        ax.plot(perturbation_levels, rankings_matrix[:, i], color=colors[i],
                linewidth=2, marker='o', markersize=5, label=label)
    ax.set_xlabel('Weight Perturbation')
    ax.set_ylabel('Rank')
    ax.invert_yaxis()
    ax.legend()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

### Error metric comparison (grouped bar)

```python
def plot_error_comparison(ax, model_names, metrics_dict, ylabel='Error Value'):
    """Grouped bar showing multiple error metrics across models. Lower is better."""
    n_models = len(model_names)
    n_metrics = len(metrics_dict)
    x = np.arange(n_models)
    width = 0.8 / n_metrics
    colors = ['#1A6FC4', '#E28E2C', '#2E9E44', '#7B5FD6']
    for i, (metric_name, values) in enumerate(metrics_dict.items()):
        offset = (i - (n_metrics - 1) / 2) * width
        ax.bar(x + offset, values, width, label=metric_name,
               color=colors[i % len(colors)], edgecolor='white', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

## 5. Data Exploration

### Correlation heatmap

```python
def plot_correlation_heatmap(ax, corr_matrix, feature_names, cmap='RdBu_r'):
    """Diverging correlation heatmap: red=positive, blue=negative."""
    im = ax.imshow(corr_matrix, cmap=cmap, aspect='auto', vmin=-1, vmax=1)
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Correlation')
    n = len(feature_names)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(feature_names, rotation=45, ha='right', fontsize=7)
    ax.set_yticklabels(feature_names, fontsize=7)
    # Annotate with correlation values
    for i in range(n):
        for j in range(n):
            val = corr_matrix[i, j]
            text_color = 'white' if abs(val) > 0.5 else '#333333'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                    fontsize=6, color=text_color)
    ax.set_frame_on(False)
```

## 6. Workflow & Mechanism

### Simple workflow diagram

```python
def plot_workflow_diagram(ax):
    """Box-and-arrow workflow diagram using matplotlib patches."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    steps = ['Data\nCleaning', 'Indicator\nNormalization', 'Entropy\nWeighting',
             'TOPSIS\nScoring', 'Ranking', 'Robustness\nCheck']
    colors = ['#D8D8D8', '#B4D4F0', '#B4D4F0', '#5B9BD5', '#1A6FC4', '#B4D4F0']
    n = len(steps)
    box_w, box_h = 1.6, 1.0
    spacing = 2.2

    for i, (step, color) in enumerate(zip(steps, colors)):
        x = i * spacing
        box = FancyBboxPatch((x, 0), box_w, box_h, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor=PALETTE['baseline_dark'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + box_w/2, box_h/2, step, ha='center', va='center', fontsize=8)
        if i < n - 1:
            arrow = FancyArrowPatch((x + box_w, box_h/2),
                                     (x + spacing, box_h/2),
                                     arrowstyle='->', mutation_scale=20,
                                     color=PALETTE['baseline_dark'], linewidth=1.5)
            ax.add_patch(arrow)

    ax.set_xlim(-0.5, (n-1) * spacing + box_w + 0.5)
    ax.set_ylim(-0.5, box_h + 0.5)
    ax.set_aspect('equal')
    ax.axis('off')
```

## 7. Multi-Panel Layouts

### 2×2 grid with GridSpec

```python
def make_2x2_figure(figsize=(12, 10)):
    """Create a 2x2 GridSpec figure with pre-styled axes."""
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
    axes = {
        'a': fig.add_subplot(gs[0, 0]),
        'b': fig.add_subplot(gs[0, 1]),
        'c': fig.add_subplot(gs[1, 0]),
        'd': fig.add_subplot(gs[1, 1]),
    }
    for label, ax in axes.items():
        add_panel_label(ax, label)
    return fig, axes

def add_panel_label(ax, label, x=-0.08, y=1.03, fontsize=13, fontweight='bold'):
    ax.text(x, y, label, transform=ax.transAxes, fontsize=fontsize,
            fontweight=fontweight, va='bottom', ha='left')
```

### Hero panel + subordinates (1 hero, 2 small)

```python
def make_hero_layout(figsize=(12, 8)):
    """Left: large hero panel (a). Right: two smaller validation panels (b, c)."""
    from matplotlib.gridspec import GridSpec
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(2, 2, width_ratios=[1.5, 1], height_ratios=[1, 1],
                  hspace=0.4, wspace=0.35)
    ax_hero = fig.add_subplot(gs[:, 0])     # spans both rows
    ax_top = fig.add_subplot(gs[0, 1])
    ax_bot = fig.add_subplot(gs[1, 1])
    add_panel_label(ax_hero, 'a', fontsize=14)
    add_panel_label(ax_top, 'b', fontsize=12)
    add_panel_label(ax_bot, 'c', fontsize=12)
    return fig, {'hero': ax_hero, 'b': ax_top, 'c': ax_bot}
```

### 1-row comparison (3 panels side by side)

```python
def make_comparison_row(figsize=(16, 5)):
    """Three equal-width panels for method comparison."""
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    for i, (ax, label) in enumerate(zip(axes, ['a', 'b', 'c'])):
        add_panel_label(ax, label)
    plt.subplots_adjust(wspace=0.3)
    return fig, axes
```

## Complete end-to-end example

```python
# Example: complete evaluation figure for Q1
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'

# ── Data ────────────────────────────────────────────────────────────────
cities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
entropy_scores = [0.88, 0.82, 0.79, 0.65, 0.61, 0.55, 0.48, 0.42]
equal_scores = [0.75, 0.73, 0.72, 0.68, 0.67, 0.65, 0.62, 0.60]
weights = [0.31, 0.28, 0.23, 0.18]
indicator_names = ['Population', 'GDP', 'Green Area', 'Transport']
perturbation = [-0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15]
rank_stability = np.array([
    [1, 2, 3, 4, 5, 6, 7, 8],
    [1, 2, 3, 4, 5, 6, 7, 8],
    [1, 2, 3, 4, 6, 5, 7, 8],
    [1, 2, 3, 4, 6, 5, 7, 8],
    [1, 2, 3, 5, 4, 6, 8, 7],
    [1, 3, 2, 5, 4, 7, 6, 8],
    [2, 1, 3, 5, 4, 7, 6, 8],
])

# ── Figure layout ────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.35)

ax_a = fig.add_subplot(gs[0, 0])  # ranking bar
ax_b = fig.add_subplot(gs[0, 1])  # weight distribution
ax_c = fig.add_subplot(gs[1, 0])  # ranking comparison
ax_d = fig.add_subplot(gs[1, 1])  # sensitivity

# ── Panel a: Final ranking ──────────────────────────────────────────────
sorted_idx = np.argsort(entropy_scores)[::-1]
sorted_names = [cities[i] for i in sorted_idx]
sorted_scores = [entropy_scores[i] for i in sorted_idx]
colors_a = ['#1A6FC4' if i < 3 else '#767676' for i in range(len(sorted_names))]
ax_a.barh(range(len(sorted_names)), sorted_scores, color=colors_a,
          edgecolor='white', linewidth=0.5, height=0.65)
ax_a.set_yticks(range(len(sorted_names)))
ax_a.set_yticklabels(sorted_names)
ax_a.invert_yaxis()
ax_a.set_xlabel('Closeness Score')
ax_a.spines['right'].set_visible(False)
ax_a.spines['top'].set_visible(False)
add_panel_label(ax_a, 'a')

# ── Panel b: Weights ────────────────────────────────────────────────────
colors_b = ['#1A6FC4', '#5B9BD5', '#B4D4F0', '#8FC8F8']
bars_b = ax_b.bar(indicator_names, weights, color=colors_b,
                  edgecolor='white', linewidth=0.5)
for bar, w in zip(bars_b, weights):
    ax_b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
              f'{w:.2f}', ha='center', fontsize=9)
ax_b.set_ylabel('Entropy Weight')
ax_b.spines['right'].set_visible(False)
ax_b.spines['top'].set_visible(False)
ax_b.set_ylim(0, max(weights) * 1.2)
add_panel_label(ax_b, 'b')

# ── Panel c: Baseline vs Main ───────────────────────────────────────────
x = np.arange(len(cities))
w = 0.35
ax_c.bar(x - w/2, equal_scores, w, label='Equal-Weight (Baseline)',
         color='#767676', edgecolor='white', linewidth=0.5)
ax_c.bar(x + w/2, entropy_scores, w, label='Entropy-TOPSIS',
         color='#1A6FC4', edgecolor='white', linewidth=0.5)
ax_c.set_xticks(x)
ax_c.set_xticklabels(cities)
ax_c.set_ylabel('Score')
ax_c.legend(fontsize=7)
ax_c.spines['right'].set_visible(False)
ax_c.spines['top'].set_visible(False)
add_panel_label(ax_c, 'c')

# ── Panel d: Sensitivity ────────────────────────────────────────────────
top3_colors = ['#1A6FC4', '#E28E2C', '#2E9E44']
top3_labels = [cities[i] for i in sorted_idx[:3]]
for i in range(3):
    ax_d.plot(perturbation, rank_stability[:, i], color=top3_colors[i],
              linewidth=2, marker='o', markersize=5, label=f'{top3_labels[i]} (rank {i+1})')
ax_d.set_xlabel('Weight Perturbation')
ax_d.set_ylabel('Rank')
ax_d.invert_yaxis()
ax_d.legend(fontsize=7)
ax_d.spines['right'].set_visible(False)
ax_d.spines['top'].set_visible(False)
add_panel_label(ax_d, 'd')

# ── Save ────────────────────────────────────────────────────────────────
fig.tight_layout(pad=2)
fig.savefig('figure.svg', bbox_inches='tight')
fig.savefig('figure.png', dpi=300, bbox_inches='tight')
plt.close(fig)
```
