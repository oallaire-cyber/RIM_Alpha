### 🖼️ Graph Visual Behaviour Panel

The **Graph Visual Behaviour** panel (F32) consolidates all canvas visual settings into one place. It is available in **Advanced mode** in the left filter column of the Visualization tab, below the Layout Management section.

---

#### Presets

Four named presets apply a coherent combination of visual effects with a single click:

| Preset | Exposure Opacity | Lifecycle Opacity | Quadrant Borders | Best for |
|--------|-----------------|-------------------|-----------------|----------|
| ✨ Clean | Off | Off | Off | Clean topology view — presentations |
| 🔬 Analysis | On | Off | On | Risk deep-dive — exposure + quadrant focus |
| 🔄 Lifecycle Audit | Off | On | On | Lifecycle review — status visibility |
| 🏖️ Sandbox Edit | Off | On | Off | Scope sandbox editing (F29) |

The active preset is highlighted. Switching presets updates all toggles immediately.

---

#### Exposure Opacity

When enabled, risk nodes are faded proportionally to their exposure score:

- Risks **at or above** the threshold are fully opaque (100%).
- Risks **below** the threshold are scaled from 20% to 100% opacity.
- The **High Exposure Threshold** slider sets the cutoff (10–100).

> Use this to visually de-emphasise low-risk nodes and draw attention to the high-exposure portion of your portfolio.

---

#### Lifecycle Opacity

When enabled, risk nodes are faded based on their lifecycle status. Each status has an independent opacity slider (0.05–1.0):

| Status | Default Opacity | Meaning |
|--------|----------------|---------|
| Watching | 0.35 | Under observation — present but dimmed |
| Suppressed | 0.15 | Deliberately ignored — heavily faded |
| Accepted | 0.40 | Risk accepted — visible but de-prioritised |
| Closed / Archived | 0.20 | Resolved — nearly invisible |

Active risks are always fully opaque and unaffected by this setting.

> Use **Lifecycle Audit** preset to immediately see which risks are in non-active states without filtering them from the canvas.

---

#### Quadrant Border Encoding

When enabled, risk nodes receive a coloured border indicating their **risk quadrant** (computed from likelihood × severity):

| Border colour | Quadrant | Condition |
|--------------|----------|-----------|
| 🟥 Dark red | Critical | High likelihood AND high severity |
| 🟠 Orange | Frequency | High likelihood, lower severity |
| 🟡 Gold | Severity | Lower likelihood, high severity |
| 🟢 Forest green | Marginal | Low likelihood AND low severity |

Quadrant borders require that **Exposure has been calculated** first — the quadrant classification is derived from the exposure computation results.

> Combine with exposure opacity to create a powerful two-signal view: opacity shows how much the risk is currently costing; border colour shows why.

---

#### Save as Schema Default

The **💾 Save as Schema Default** button persists your current visual settings to `graph_visual_config` in the active schema YAML. These become the defaults that are applied the next time the application loads.

The saved settings include:
- `lifecycle_opacity` map (per-status values)
- `quadrant_border_encoding` (on/off)
- `default_preset` (the currently active preset name)

> Schema defaults can also be edited directly in `schemas/<domain>/schema.yaml` under the `graph_visual_config:` key.
