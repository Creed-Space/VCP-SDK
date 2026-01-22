# VCP Demo

Interactive demonstrations of the Value Context Protocol (VCP).

## Overview

Two demos showcasing VCP's core value propositions:

### Professional Development Demo
- **User**: Campion, senior software engineer at TechCorp
- **Value Prop**: Private context influences recommendations without being exposed to HR
- **Features**: Dual audit trail, compliance without exposure, multi-stakeholder privacy

### Personal Growth Demo
- **User**: Gentian, factory worker learning guitar
- **Value Prop**: Configure once, use everywhere. Join communities without exposing personal life
- **Features**: Cross-platform portability, community privacy, adjusted days without judgment

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
src/
├── lib/
│   ├── vcp/           # Core VCP library
│   │   ├── types.ts   # TypeScript interfaces
│   │   ├── context.ts # Context store + filtering
│   │   ├── constitution.ts # Constitution loader
│   │   ├── audit.ts   # Audit trail
│   │   └── privacy.ts # Privacy filtering
│   ├── personas/      # Demo user profiles
│   ├── data/          # Mock data
│   └── components/    # Shared components
├── routes/
│   ├── professional/  # Professional demo
│   │   ├── morning/   # Recommendation journey
│   │   └── audit/     # Dual audit view
│   └── personal/      # Personal demo
│       ├── platforms/ # JustinGuitar, Yousician mocks
│       ├── community/ # 30-day challenge
│       └── skip/      # Skip day flow
```

## Key Concepts

### Privacy Filtering
Private context (family status, health conditions, work schedule) influences recommendations through boolean flags. Platforms see "budget_limited: true" not "single parent struggling financially."

### Dual Audit Trail
Users see full detail of what was shared and why. Stakeholders (HR, community) see only compliance data - never the private reasons.

### Cross-Platform Portability
Same VCP profile works across multiple platforms. Skills sync automatically without re-configuring preferences.

### Adjusted Days
Community challenges support "adjusted" days where participants can skip without exposing reasons. Community sees the count, not the why.

## Tech Stack

- **Framework**: Svelte 5
- **Routing**: SvelteKit
- **State**: Svelte stores + localStorage
- **Styling**: Custom CSS (Creed Space theme)
- **Types**: TypeScript

## No Backend Required

Everything runs client-side with localStorage persistence. No auth, no database, no API calls. This is a demonstration app.

## Related Documentation

- Design specs: `_plans/vcp_demo_*.md`
- JSON schemas: `_plans/schemas/*.json`
- Implementation guide: `_contprompts/vcp_demo_implementation_2026-01-21.md`

## License

Part of Creed Space. See main repository for license.
