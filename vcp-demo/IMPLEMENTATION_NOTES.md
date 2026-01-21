# VCP Demo Implementation Notes

**Implemented**: 2026-01-21
**Status**: MVP Complete

## What Was Built

### Core VCP Library (`src/lib/vcp/`)

| File | Lines | Purpose |
|------|-------|---------|
| `types.ts` | ~400 | TypeScript interfaces from JSON schemas |
| `context.ts` | ~180 | Context store, localStorage, consent management |
| `constitution.ts` | ~250 | Constitution loader, rule resolution, persona tones |
| `audit.ts` | ~200 | Audit trail, dual-view generation |
| `privacy.ts` | ~200 | Field classification, constraint extraction |
| `index.ts` | ~40 | Re-exports |

### Personas (`src/lib/personas/`)

| File | User | Demo |
|------|------|------|
| `campion.ts` | Senior engineer, single parent, health constraints | Professional |
| `gentian.ts` | Factory worker, shift work, apartment living | Personal |

### Mock Data (`src/lib/data/`)

| File | Content |
|------|---------|
| `courses.json` | 5 courses for professional demo |
| `lessons.json` | JustinGuitar + Yousician lessons |
| `challenge.json` | 30-day challenge with leaderboard |

### Routes

```
routes/
├── +page.svelte           # Demo selector landing
├── professional/
│   ├── +page.svelte       # Campion profile
│   ├── morning/+page.svelte    # Course recommendations
│   └── audit/+page.svelte      # Dual audit view
└── personal/
    ├── +page.svelte       # Gentian profile
    ├── platforms/
    │   ├── justinguitar/+page.svelte
    │   └── yousician/+page.svelte
    ├── community/+page.svelte   # 30-day challenge
    └── skip/+page.svelte        # Skip day flow
```

## Key Patterns Implemented

### Privacy Filtering
```typescript
// Private details → boolean flags
constraints: {
  time_limited: true,      // Community sees this
  // They don't see: "single parent, childcare 8-3"
}
```

### Dual Audit Views
```typescript
// Employee sees full detail
{ data_shared: ['career_goal', 'budget'],
  data_withheld: ['family_status', 'health'] }

// HR sees compliance only
{ private_context_used: true,
  private_context_exposed: false }  // Always false
```

### Cross-Platform Sync
```typescript
// JustinGuitar → VCP → Yousician
skills_acquired: ['G_major', 'C_major', 'D_major']
// Yousician shows "Skills synced from JustinGuitar!"
```

### Adjusted Days
```typescript
// User sees: "Jan 18: Adjusted (night shift recovery)"
// Community sees: "18/21 (3 adjusted)"
// Reason never exposed
```

## Build Stats

- **Type check**: 0 errors, 0 warnings
- **Bundle size**: ~27KB gzipped (main chunk)
- **Build time**: ~6 seconds
- **Dependencies**: Svelte 5, SvelteKit, qrcode

## What's Not Implemented (v0.2+)

- Evening personal mode journey (Professional)
- Conflict resolution journey (Professional)
- Music shop kiosk (Personal)
- Coach tier view (Personal)
- Profile editor (Both)
- Real crypto signatures
- Cloud sync

## Running the Demo

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # Production build
npm run preview  # Preview production build
```

## Design Documents

- [`_plans/vcp_demo_overview.md`](../_plans/vcp_demo_overview.md)
- [`_plans/vcp_demo_mvp_scope.md`](../_plans/vcp_demo_mvp_scope.md)
- [`_contprompts/vcp_demo_implementation_2026-01-21.md`](../_contprompts/vcp_demo_implementation_2026-01-21.md)
