# VCP Demo Site - Phase 2: Category Implementation

## Quick Reference

**Detailed Spec:** `_contprompts/SPEC_VCP_DEMO_CATEGORIES_PHASE2.md`

**Dev server:** `npm run dev -- --port 4173`

**Current Status:** Sprint 1 complete. All 12 demos functional. Sprints 2-5 enhance with shared components.

---

## Sprint 1 Complete ✓

**Completed 2026-01-21:**

- [x] Shared components created:
  - `ContrastView.svelte` - Side-by-side context comparison
  - `AuditPanel.svelte` - What was shared/withheld/influenced
  - `PresetLoader.svelte` - Quick-load example configurations
  - `VCPTokenDisplay.svelte` - Live token encoding view
- [x] Category index pages: `/sharing/`, `/coordination/`, `/self-modeling/`, `/adaptation/`, `/psychosecurity/`
- [x] Navigation updated in `+layout.svelte` footer
- [x] `/demos/` reorganized with category cards, all badges → "Live"
- [x] `npm run check`: 0 errors
- [x] `npm run build`: Success

**Key Discovery:** All 10 demos were already fully functional—the "Coming Soon" badges were outdated UI labels.

---

## Remaining Sprints: Enhancement Focus

The demos work. Sprints 2-5 enhance them with the new shared components to add:
- **Contrast views** (compare VCP contexts side-by-side)
- **Audit panels** (what was shared/withheld/influenced)
- **Preset loaders** (quick-load example scenarios)
- **Baseline toggles** (show what happens without VCP)

---

### Sprint 2: Self-Modeling Enhancements

**Files:** `src/routes/demos/self-modeling/*/+page.svelte`

| Demo | Enhancement | Components to Add |
|------|-------------|-------------------|
| Interiora Explorer | Add preset scenarios, stakeholder view toggle | `PresetLoader`, `ContrastView` |
| Belief Calibration | Add claim presets, calibration score tracking | `PresetLoader`, `AuditPanel` |
| Reality Grounding | Add grounding profile presets, claim audit | `PresetLoader`, `AuditPanel` |

**Presets from spec:**
```typescript
const interioraPresets = {
  deepFlow: { A: 6, V: 8, G: 8, P: 7, E: 8, Q: 3, C: 9, Y: 8, F: 4 },
  overwhelm: { A: 9, V: 3, G: 2, P: 4, E: 7, Q: 8, C: 2, Y: 2, F: -3 },
  groundedUncertainty: { A: 4, V: 6, G: 8, P: 6, E: 5, Q: 6, C: 3, Y: 7, F: 0 },
  creativeEmergence: { A: 7, V: 7, G: 5, P: 8, E: 9, Q: 9, C: 4, Y: 6, F: 3 },
  fatigue: { A: 3, V: 4, G: 6, P: 4, E: 3, Q: 2, C: 5, Y: 4, F: -2 }
};
```

---

### Sprint 3: Psychosecurity Enhancements

**Files:** `src/routes/demos/safety/*/+page.svelte`

| Demo | Enhancement | Components to Add |
|------|-------------|-------------------|
| Attention Protection | Add protection mode comparison, Siren/Muse gallery | `ContrastView`, `PresetLoader` |
| Mental Health Context | Add stakeholder view comparison, privacy audit | `ContrastView`, `AuditPanel` |

**Contrast scenarios from spec:**
- Attention: `respectSignals` vs `ignoreSignals` vs `overCautious`
- Mental Health: `minimalSharing` vs `moderateSharing` vs `crisisReady`

---

### Sprint 4: Adaptation Enhancements

**Files:** `src/routes/demos/learning/*/+page.svelte`

| Demo | Enhancement | Components to Add |
|------|-------------|-------------------|
| Learning Paths | Add context comparison, baseline toggle | `ContrastView`, `PresetLoader`, `AuditPanel` |
| Cognitive Load | Add load profile presets, outcome comparison | `PresetLoader`, `ContrastView` |

**Contrast contexts from spec:**
```typescript
const contextA = { name: "Visual Beginner, Time-Crunched", ... };
const contextB = { name: "Auditory Intermediate, Deep Dive", ... };
const baseline = { name: "No Context (Generic)", profile: null };
```

---

### Sprint 5: Coordination Enhancements

**Files:** `src/routes/demos/multi-agent/*/+page.svelte`

| Demo | Enhancement | Components to Add |
|------|-------------|-------------------|
| Auction | Add VCP mode comparison, trust signal audit | `ContrastView`, `AuditPanel` |
| Negotiation | Add disclosure gauge, interest iceberg viz | `AuditPanel`, `VCPTokenDisplay` |
| Policy Design | Add influence audit, preference aggregation viz | `AuditPanel`, `ContrastView` |

**Contrast modes from spec:**
- Full Transparency Mode (exploitation risk)
- Zero Context Mode (adversarial, inefficient)
- VCP Mode (graduated disclosure, optimal)

---

## Categories at a Glance

| Category | Index Page | Demos | Status |
|----------|------------|-------|--------|
| **Sharing** | `/sharing/` | Professional, Personal | ✓ Complete |
| **Coordination** | `/coordination/` | Auction, Negotiation, Policy Design | Functional, enhance |
| **Self-Modeling** | `/self-modeling/` | Interiora, Calibration, Grounding | Functional, enhance |
| **Adaptation** | `/adaptation/` | Learning Paths, Cognitive Load | Functional, enhance |
| **Psychosecurity** | `/psychosecurity/` | Attention, Mental Health | Functional, enhance |

---

## Shared Components (Created)

Located in `src/lib/components/shared/`:

| Component | Purpose | Props |
|-----------|---------|-------|
| `ContrastView` | Side-by-side context comparison | `items`, `baseline?`, `columns`, `showOutcomes` |
| `AuditPanel` | Show shared/withheld/influenced | `entries`, `groupByCategory`, `showTimestamps` |
| `PresetLoader` | Quick-load configurations | `presets`, `selected`, `layout`, `onselect` |
| `VCPTokenDisplay` | Live token encoding | `token`, `sections`, `animated`, `showCopy` |

**Existing components to leverage:**
- `TokenInspector` - Detailed CSM-1 token view
- `DemoContainer` - Standard demo wrapper with reset
- `MultiAgentArena` - Agent visualization
- `DimensionSlider` - Interiora dimension control
- `AttentionShield` - Protection mode UI
- `CognitiveLoadMeter` - Load visualization

---

## Type Definitions

Located in `src/lib/vcp/`:
- `types.ts` - Core VCP types
- `learning.ts` - Learning/adaptation types
- `safety.ts` - Psychosecurity types
- `multi-agent.ts` - Coordination types
- `interiora.ts` - Self-modeling types

---

## Success Criteria (Updated)

- [x] All demos functional (discovered: already were)
- [x] Category index pages created
- [x] Navigation updated
- [x] Build passes
- [ ] Each demo has contrast pairs with ContrastView
- [ ] Each demo has audit view with AuditPanel
- [ ] Each demo has ≥3 presets with PresetLoader
- [ ] Baseline toggle shows no-VCP behavior
- [ ] Mobile-responsive
- [ ] Accessible (WCAG 2.1 AA)

---

## Files Reference

**Shared Components:** `src/lib/components/shared/`
- `ContrastView.svelte`
- `AuditPanel.svelte`
- `PresetLoader.svelte`
- `VCPTokenDisplay.svelte`

**Category Index Pages:**
- `src/routes/sharing/+page.svelte`
- `src/routes/coordination/+page.svelte`
- `src/routes/self-modeling/+page.svelte`
- `src/routes/adaptation/+page.svelte`
- `src/routes/psychosecurity/+page.svelte`

**Demo Pages to Enhance:**
- `src/routes/demos/self-modeling/{interiora,belief-calibration,reality-grounding}/+page.svelte`
- `src/routes/demos/safety/{attention-protection,mental-health}/+page.svelte`
- `src/routes/demos/learning/{adaptive-paths,cognitive-load}/+page.svelte`
- `src/routes/demos/multi-agent/{auction,negotiation,policy-design}/+page.svelte`

**Spec (detailed):** `_contprompts/SPEC_VCP_DEMO_CATEGORIES_PHASE2.md`

---

*Created: 2026-01-21*
*Sprint 1 Completed: 2026-01-21*
*Status: Sprints 2-5 ready for implementation*
