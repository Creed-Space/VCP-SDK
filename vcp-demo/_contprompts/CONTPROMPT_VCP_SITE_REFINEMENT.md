# Contprompt: VCP Demo Site Refinement

## Context
The VCP demo site is live at https://valuecontextprotocol.org, deployed from Creed-Space/Value-Context-Protocol repo (website/ folder). GitHub Pages with custom domain.

## Repository
```bash
gh repo clone Creed-Space/Value-Context-Protocol /tmp/vcp-site
cd /tmp/vcp-site/website
npm ci && npm run dev
```

## Completed Work (2026-01-22)

### Content
- [x] 8 documentation pages fully written and live
- [x] Removed Muse persona (now 5 personas: Godparent, Sentinel, Ambassador, Anchor, Nanny)
- [x] All doc pages have proper navigation sidebar
- [x] Professional/Personal demo journeys working

### Branding
- [x] VCP logo (vcp-logo.png) in header (96px) and footer (112px)
- [x] PNG favicons (16px, 32px) + Apple touch icon
- [x] "Demo" badge next to logo

### Technical
- [x] ~200 emoji replaced with Font Awesome 6 icons
- [x] Fixed Svelte 5 `state_referenced_locally` warning in ContrastView
- [x] Build passes with no errors
- [x] Mobile responsive layout

## Areas for Continued Refinement

### Visual Polish
- [ ] Review color consistency across all pages
- [ ] Check dark mode contrast ratios (WCAG AA)
- [ ] Ensure consistent spacing/padding throughout
- [ ] Review typography hierarchy (h1-h4 sizing)
- [x] Add subtle hover animations to cards (enhanced lift + glow)
- [x] Add button press feedback (primary buttons)
- [ ] Consider adding gradient accents to hero sections

### Content Quality
- [ ] Proofread all doc pages for typos/grammar
- [ ] Ensure code examples are syntactically correct
- [ ] Add more real-world examples to demos
- [x] Review persona descriptions for accuracy (fixed Muse→Godparent in docs)
- [x] Add "Edit on GitHub" links to doc pages (DocsLayout with editPath prop)

### UX Improvements
- [ ] Add search functionality to docs
- [ ] Add "On this page" table of contents for long docs
- [ ] Improve mobile navigation UX
- [ ] Add breadcrumb navigation
- [ ] Consider adding a "Quick Start" CTA on homepage
- [ ] Add loading states for demo interactions

### Interactive Demos
- [x] Test all demo journeys end-to-end (Professional, Personal - working)
- [x] Verify state transitions work correctly
- [x] Check console for any JS errors (none found)
- [ ] Ensure demos are intuitive without instructions
- [ ] Add reset/restart buttons to demos

### SEO & Meta
- [ ] Review Open Graph tags on all pages
- [x] Add structured data (JSON-LD) - WebSite + SoftwareApplication schemas
- [x] Ensure proper canonical URLs (added to app.html)
- [x] Add sitemap.xml (40+ pages, all routes covered)
- [x] Add robots.txt with sitemap reference
- [ ] Review page titles and descriptions

### Performance
- [x] Optimize logo PNG (443KB → 9KB, 97% reduction)
- [x] Create proper apple-touch-icon.png (180x180, 7KB)
- [x] Remove oversized favicon.png, use SVG instead
- [ ] Lazy load demo components
- [ ] Review bundle size
- [x] Add preconnect hints for Font Awesome CDN

### Accessibility
- [ ] Test with screen reader
- [ ] Verify keyboard navigation works
- [ ] Check focus indicators are visible
- [ ] Ensure all images have alt text
- [ ] Test with reduced motion preference

## Key Files

| File | Purpose |
|------|---------|
| `src/routes/+layout.svelte` | Main layout with header/footer |
| `src/routes/+page.svelte` | Homepage |
| `src/routes/docs/` | Documentation pages |
| `src/routes/demos/` | Interactive demos |
| `src/app.css` | Global styles |
| `src/lib/components/` | Shared components |
| `static/vcp-logo.png` | Logo (9KB - optimized) |

## Build & Deploy
```bash
cd /tmp/vcp-site/website
npm run build      # Build for production
npm run preview    # Preview locally
git add -A && git commit -m "description" && git push origin main
# GitHub Actions auto-deploys to valuecontextprotocol.org
```

## Design Principles
- **Professional but approachable** - This is serious AI safety tech, but accessible
- **Privacy-first messaging** - Always emphasize user control
- **Show don't tell** - Interactive demos over documentation walls
- **Consistent patterns** - Same components, spacing, colors throughout
- **Mobile-first** - Many visitors will be on phones

## Notes
- Site uses SvelteKit with adapter-static for GitHub Pages
- Font Awesome 6 Free loaded via CDN
- Custom domain: valuecontextprotocol.org (CNAME in static/)
- "Siren vs Muse" in attention-protection is a content analysis concept, NOT a persona
