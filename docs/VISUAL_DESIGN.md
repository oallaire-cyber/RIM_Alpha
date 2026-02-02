# 🎨 RIM Visual Design Guide

Complete reference for visual semantics in the Risk Influence Map.

---

## Design Philosophy

### Core Principles

1. **Instant Recognition**: Shape and color convey meaning without reading labels
2. **Semantic Consistency**: Similar things look similar, different things look different
3. **Progressive Disclosure**: Essential info first, details on demand
4. **Accessibility**: Works in grayscale, distinguishable for color blindness

### Visual Hierarchy

```
    MOST PROMINENT                               LEAST PROMINENT
    ◀────────────────────────────────────────────────────────▶
    
    ⬡ TPO       ◆ Strategic      ● Operational      🛡️ Mitigation
    (Gold)       (Purple)          (Blue)            (Green/Teal)
    (Largest)    (Large)           (Medium)          (Medium)
```

---

## Node Shapes

### Shape Grammar

| Shape | Entity | Rationale |
|-------|--------|-----------|
| **◆ Diamond** | Strategic Risk | Pointed shape = danger, warning (road sign psychology) |
| **● Circle** | Operational Risk | Foundation, building block, cause-oriented |
| **🛡️ Rounded Box** | Mitigation | Shield-like, protective, softer edges |
| **⬡ Hexagon** | TPO | Distinctive goal shape, structural stability |

### Why These Shapes?

**Diamond for Strategic Risks**:
- Universal danger symbol (road signs, warnings)
- Points create tension, draw attention
- Prominent in visual field

**Circle for Operational Risks**:
- Foundation shape, building blocks
- Less aggressive than pointed shapes
- Good for showing cause-effect flow

**Rounded Box for Mitigations**:
- Soft edges = protection, safety
- Shield metaphor (defense)
- Clearly different from risks

**Hexagon for TPOs**:
- Unique shape, stands out
- Structural stability (engineering metaphor)
- Goal-oriented, target-like

---

## Color Palette

### Primary Colors by Entity

| Entity | Color | Hex | RGB |
|--------|-------|-----|-----|
| Strategic Risk | Purple | `#8E44AD` | 142, 68, 173 |
| Operational Risk | Blue | `#2980B9` | 41, 128, 185 |
| TPO | Gold | `#F1C40F` | 241, 196, 15 |
| Mitigation (Dedicated) | Teal | `#1ABC9C` | 26, 188, 156 |
| Mitigation (Inherited) | Blue | `#3498DB` | 52, 152, 219 |
| Mitigation (Baseline) | Purple | `#9B59B6` | 155, 89, 182 |

### Exposure Heat Map Gradient

| Exposure Level | Color | Hex | Description |
|----------------|-------|-----|-------------|
| Critical (≥70) | Dark Red | `#C0392B` | Immediate attention |
| High (≥40) | Red | `#E74C3C` | Significant concern |
| Medium (≥20) | Orange | `#F39C12` | Monitor closely |
| Low (<20) | Yellow | `#F1C40F` | Manageable |

### Color Psychology

| Color Family | Meaning | Used For |
|--------------|---------|----------|
| **Red/Orange** | Danger, urgency, heat | High exposure risks |
| **Purple** | Authority, strategy | Strategic risks |
| **Blue** | Stability, trust, operations | Operational risks |
| **Green/Teal** | Safety, protection, health | Mitigations |
| **Gold** | Value, goals, achievement | TPOs |
| **Gray** | Neutral, legacy, inactive | Archived, legacy items |

---

## Border Styles

### Risk Status

| Status | Border Style | Visual |
|--------|--------------|--------|
| **Active** | Solid, 2px | ─────────── |
| **Contingent** | Dashed, 3px | ─ ─ ─ ─ ─ ─ |
| **Archived** | Dotted, 2px | ∙∙∙∙∙∙∙∙∙∙∙ |

### Risk Origin

| Origin | Border Treatment |
|--------|------------------|
| **New** | Standard border (level color) |
| **Legacy** | Gray thick border (4px), `#7F8C8D` |

### Mitigation Status

| Status | Border Style | Visual |
|--------|--------------|--------|
| **Implemented** | Solid | ─────────── |
| **In Progress** | Dash-dot | ─ ∙ ─ ∙ ─ ∙ |
| **Proposed** | Dashed | ─ ─ ─ ─ ─ ─ |
| **Deferred** | Dotted | ∙∙∙∙∙∙∙∙∙∙∙ |

### Mitigation Type Borders

| Type | Border Width | Style |
|------|--------------|-------|
| **Dedicated** | 3px | Solid |
| **Inherited** | 2px | Dotted |
| **Baseline** | 5px | Solid (thick) |

---

## Edge Styles

### Edge Types

| Relationship | Arrow Type | Meaning |
|--------------|------------|---------|
| Influence (Risk→Risk) | → Standard | "Causes" or "amplifies" |
| Mitigation (Mit→Risk) | ⊣ Bar end | "Blocks" or "reduces" |
| TPO Impact (Risk→TPO) | ▷ Vee | "Threatens" or "targets" |

### Influence Edge Colors

| Influence Level | Color | Hex |
|-----------------|-------|-----|
| Level 1 (Op→Strat) | Red | `#E74C3C` |
| Level 2 (Strat→Strat) | Purple | `#8E44AD` |
| Level 3 (Op→Op) | Blue | `#2980B9` |

### Influence Edge Thickness (by Strength)

| Strength | Width |
|----------|-------|
| Critical | 5px |
| Strong | 4px |
| Moderate | 3px |
| Weak | 2px |

### Influence Edge Line Style

| Level | Style |
|-------|-------|
| Level 1 | Thick solid |
| Level 2 | Medium solid |
| Level 3 | Thin dashed |

### Mitigation Edge Colors

All mitigates edges use: **Green** (`#1ABC9C`)

### Mitigation Edge Thickness (by Effectiveness)

| Effectiveness | Width |
|---------------|-------|
| Critical | 5px |
| High | 4px |
| Medium | 3px |
| Low | 2px |

### TPO Impact Edge

| Property | Value |
|----------|-------|
| Color | Orange (`#E67E22`) |
| Style | Dash-dot |
| Arrow | Vee (▷) |

---

## Size Encoding

### Node Sizes

| Entity | Base Size | Variation |
|--------|-----------|-----------|
| TPO | 40px | Fixed |
| Strategic Risk | 35px | +5px if high exposure |
| Operational Risk | 28px | +5px if high exposure |
| Mitigation | 32px | Fixed |

### Exposure-Based Size

When coloring by exposure, nodes scale:

```
Node Size = Base Size × (1 + Exposure/100 × 0.2)
```

Maximum 20% size increase for highest exposure.

---

## Labels

### Label Format

| Entity | Label Format | Example |
|--------|--------------|---------|
| Risk (New) | `{Reference}: {Name}` | `SR-001: Supply Disruption` |
| Risk (Legacy) | `[L] {Reference}: {Name}` | `[L] SR-005: Legacy Cost Risk` |
| Mitigation | `🛡️ {Reference}: {Name}` | `🛡️ MIT-001: Dual Sourcing` |
| TPO | `{Reference}` | `TPO-01` |

### Label Wrapping

Long names wrap at 20 characters:

```
SR-001: Supply Chain
Disruption Due to
Vendor Bankruptcy
```

### Label Positioning

- **Risks**: Below node
- **TPOs**: Below node
- **Mitigations**: Below node

---

## Interactive States

### Selection

| State | Visual Change |
|-------|---------------|
| Hover | Border width +2px, slight glow |
| Selected | Border width +4px, bright border color |
| Highlighted | Gold border, pulsing effect |

### Neighborhood Highlighting

When using "Explore in Graph":
- Selected node: Gold highlight
- Direct neighbors: Visible
- Non-neighbors: Faded (50% opacity)

---

## Legend Reference

### Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│                    NODE SHAPES                       │
├─────────────────────────────────────────────────────┤
│  ◆  Strategic Risk (Purple)    ◇  Contingent Risk   │
│  ●  Operational Risk (Blue)    🛡️  Mitigation       │
│  ⬡  TPO (Gold)                                      │
├─────────────────────────────────────────────────────┤
│                    EDGE TYPES                        │
├─────────────────────────────────────────────────────┤
│  ━━━━━━━━→  Level 1 (Red)      ───▷  TPO Impact     │
│  ─────→    Level 2 (Purple)    ───⊣  Mitigates      │
│  - - - →   Level 3 (Blue)                           │
├─────────────────────────────────────────────────────┤
│                    BORDER STYLES                     │
├─────────────────────────────────────────────────────┤
│  ─────  Solid = Active/Implemented                  │
│  ─ ─ ─  Dashed = Contingent/Proposed                │
│  ∙∙∙∙∙  Dotted = Archived/Deferred                  │
│  ████   Thick gray = Legacy risk                    │
└─────────────────────────────────────────────────────┘
```

---

## Accessibility

### Color Blindness Considerations

The palette is designed to be distinguishable for:
- **Deuteranopia** (red-green): Purple/Blue still distinguishable
- **Protanopia** (red-blind): Yellow/Blue contrast maintained
- **Tritanopia** (blue-yellow): Shapes differentiate

### Grayscale Fallback

When printed in grayscale:
- Shapes remain the primary differentiator
- Border styles distinguish status
- Labels provide confirmation

### Contrast Ratios

All text meets WCAG AA standards:
- White text on colored backgrounds: ≥4.5:1
- Dark text on light backgrounds: ≥4.5:1

---

## Implementation Notes

### PyVis Shape Mapping

```python
# PyVis shape names
SHAPE_MAP = {
    "strategic_risk": "diamond",
    "operational_risk": "dot",      # Circle
    "mitigation": "box",            # Rounded via CSS
    "tpo": "hexagon"
}
```

### CSS Customization

Rounded corners for mitigation boxes:

```css
.mitigation-node {
    border-radius: 12px;
}
```

### Border Dash Arrays

```python
BORDER_DASHES = {
    "solid": False,
    "dashed": [8, 4],
    "dotted": [2, 2],
    "dash_dot": [8, 2, 2, 2]
}
```

---

*Last updated: February 2026 | Version 2.2.0*
