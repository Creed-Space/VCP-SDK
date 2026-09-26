# WebMCP TypeScript Bindings

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-09-24 -->
<!-- wiki:status = active -->

## Summary

`webmcp/` is a TypeScript package that registers VCP capabilities as discoverable tools for AI agents via the experimental WebMCP API on `document.modelContext`, falling back to `navigator.modelContext` (webmcp/src/registration.ts). This is the browser-side integration layer — it is NOT a general-purpose TypeScript VCP SDK. It targets web apps that want to expose VCP verification to AI agents visiting the page. (webmcp/package.json; webmcp/src/ listing)

## What WebMCP Is

The WebMCP API (`document.modelContext`; earlier previews used `navigator.modelContext`) is an experimental browser API for exposing tools to AI models. The webmcp package registers VCP capabilities as tools so that when an AI agent visits a VCP-aware webpage, it can discover and invoke VCP operations directly. (webmcp/package.json description: "Register VCP capabilities as discoverable tools for AI agents via the WebMCP API")

This is the browser-analog to the MCP server pattern: MCP server = CLI/server tool exposure; WebMCP = browser tool exposure.

## Module Structure (`webmcp/src/`)

| File | Purpose |
|------|---------|
| `index.ts` | Entry point; tool registration |
| `tools.ts` | Tool definitions (capabilities exposed to AI agents) |
| `types.ts` | TypeScript type definitions |
| `hooks.ts` | Hook implementations |
| `registration.ts` | Registers the tools on `document.modelContext`, falling back to `navigator.modelContext` |
| `polyfill.ts` | Runs a caller-supplied polyfill loader (behind `?webmcp=polyfill`) to populate `document.modelContext` where WebMCP is not native |
| `extensions/` | Extension tool registrations |

(webmcp/src/ directory listing)

## Build and Test

```bash
npm run build    # Compile TypeScript → dist/
npm run check    # Type checking
npm run test     # Test suite
npm run clean    # Clean dist/
```
(webmcp/package.json scripts)

Output: `dist/index.js` (CommonJS/ESM bundle)

## Relationship to Rust WASM

For in-browser VCP verification without a server round-trip, use `vcp-wasm/` (Rust → WASM). WebMCP and vcp-wasm are complementary:
- `vcp-wasm` → performs the computation
- `webmcp` → registers the capability as a discoverable tool

## What This Is NOT

There is no general-purpose TypeScript/JavaScript VCP SDK (comparable to the Python SDK) in this repository. WebMCP is specifically for the `document.modelContext` tool registration pattern (with the `navigator.modelContext` fallback). For Node.js/server-side TypeScript usage of VCP, the Python SDK or Rust crate are the intended paths. (VCP-SDK/ directory listing; this page)

## Provenance

- Sources consulted: `webmcp/package.json` (description, scripts, main); `webmcp/src/` directory listing; `webmcp/src/registration.ts` and `webmcp/src/polyfill.ts` (API target)
- Last verified against sources: 2026-09-24

## See Also

- [[vcp-sdk:systems/rust-implementation]] — Rust/WASM for browser-side computation
- [[vcp-sdk:systems/python-sdk-modules]] — reference implementation
- [[vcp-sdk:systems/testing-approach]] — how conformance and unit tests work
