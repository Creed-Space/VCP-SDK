# Contprompt: VCP Demo Sharing Category Enhancement

**Created**: 2026-01-22
**Status**: Ready for execution
**Scope**: Add AuditPanel visibility to Professional and Personal journey demos

---

## Context

Phase 2 enhanced 9 demos across 4 categories (Self-Modeling, Psychosecurity, Adaptation, Coordination) with PresetLoader and AuditPanel shared components. The **Sharing** category was not included because its demos use a different paradigm:

| Category | Pattern | Demos |
|----------|---------|-------|
| Sharing | Narrative journeys with personas | Professional (Campion), Personal (guitarist) |
| Others | Interactive configuration sandboxes | Interiora, Auction, etc. |

**Decision**: Add AuditPanel to Sharing demos while preserving their narrative journey format. PresetLoader is not applicable (the persona IS the preset).

---

## Objective

Enhance Professional and Personal demos with real-time AuditPanel visibility showing what VCP shares vs withholds at each journey step.

---

## Demo Structure Analysis

### Professional Demo (`/professional`)
- **Persona**: Campion - Senior Software Engineer → Tech Lead
- **Journey**: Morning routine showing VCP protecting private context (eldercare, medical) while sharing professional data
- **Routes**:
  - `/professional` - Landing with Campion's profile
  - `/professional/morning` - Morning journey with platform interactions
  - `/professional/audit` - Existing audit view (may need enhancement)

### Personal Demo (`/personal`)
- **Persona**: Guitar learner
- **Journey**: Learning across platforms (JustinGuitar, Yousician) with VCP carrying preferences
- **Routes**:
  - `/personal` - Landing with learner profile
  - `/personal/platforms/justinguitar` - JustinGuitar interaction
  - `/personal/platforms/yousician` - Yousician interaction
  - `/personal/community` - Community interaction
  - `/personal/skip` - Skip intro option

---

## Implementation Plan

### Sprint 1: Professional Demo Enhancement

1. **Read existing files**:
   - `/professional/+page.svelte` (landing)
   - `/professional/morning/+page.svelte` (journey)
   - `/professional/audit/+page.svelte` (existing audit)
   - Check for shared VCP context/state

2. **Add AuditPanel integration**:
   - Import AuditPanel component
   - Create derived audit entries from `vcpContext` showing:
     - **Shared**: Public profile, career goals, learning style, budget
     - **Influenced**: Platform recommendations, scheduling suggestions
     - **Withheld**: Eldercare responsibilities, medical appointments, family constraints
   - Add collapsible/sidebar AuditPanel to journey steps
   - Style to not disrupt narrative flow

3. **Enhance morning journey**:
   - Each platform interaction should update audit entries
   - Show in real-time what each platform sees vs doesn't see

### Sprint 2: Personal Demo Enhancement

1. **Read existing files**:
   - `/personal/+page.svelte` (landing)
   - `/personal/platforms/justinguitar/+page.svelte`
   - `/personal/platforms/yousician/+page.svelte`
   - `/personal/community/+page.svelte`
   - Check for shared VCP context/state

2. **Add AuditPanel integration**:
   - Import AuditPanel component
   - Create derived audit entries showing:
     - **Shared**: Learning preferences, skill level, goals
     - **Influenced**: Content recommendations, difficulty adjustments
     - **Withheld**: Practice time constraints, frustration triggers, personal motivations
   - Add AuditPanel to each platform page

3. **Cross-platform continuity**:
   - Show how VCP context carries across platforms
   - Highlight what's new vs what was already known

### Sprint 3: Validation & Polish

1. Run `npm run check` and `npm run build`
2. Test journey flow with AuditPanel visible
3. Ensure AuditPanel doesn't disrupt mobile responsiveness
4. Verify narrative remains primary focus

---

## Success Criteria

- [ ] Professional demo shows AuditPanel during journey
- [ ] Personal demo shows AuditPanel on each platform page
- [ ] Audit entries accurately reflect VCP context at each step
- [ ] Narrative flow preserved (AuditPanel is supplementary, not primary)
- [ ] Mobile responsive
- [ ] `npm run check` passes
- [ ] `npm run build` succeeds

---

## Technical Notes

### AuditPanel Interface (from existing component)
```typescript
interface AuditEntry {
  field: string;
  category: 'shared' | 'withheld' | 'influenced';
  value?: string | number | boolean;
  reason?: string;
  stakeholder?: string;
  timestamp?: string;
}
```

### Existing VCP Context Pattern
```typescript
import { vcpContext } from '$lib/vcp';
const ctx = $derived($vcpContext);
```

### Styling Approach
- Use `compact={true}` prop on AuditPanel for journey pages
- Consider collapsible wrapper or fixed sidebar
- Muted styling to not compete with narrative

---

## Files to Modify

**Professional**:
- `src/routes/professional/+page.svelte`
- `src/routes/professional/morning/+page.svelte`
- `src/routes/professional/audit/+page.svelte` (if needed)

**Personal**:
- `src/routes/personal/+page.svelte`
- `src/routes/personal/platforms/justinguitar/+page.svelte`
- `src/routes/personal/platforms/yousician/+page.svelte`
- `src/routes/personal/community/+page.svelte`

---

## Execution Command

```
Execute the contprompt at:
/Users/nellwatson/Documents/GitHub/Rewind/vcp-demo/_contprompts/CONTPROMPT_VCP_DEMO_SHARING_ENHANCEMENT.md
```
