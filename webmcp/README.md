# @creed-space/vcp-sdk

Register VCP capabilities as discoverable tools through the experimental
[WebMCP imperative API](https://developer.chrome.com/docs/ai/webmcp/imperative-api)
(`document.modelContext`).

**Publication state:** source-only candidate, version 4.2.0. No npm release is
currently claimed. Browser behavior remains experimental and must be checked
against the compatibility table below.

## Quick Start

```typescript
// From a local VCP-SDK source checkout after `npm --prefix webmcp run build`.
import { registerVCPTools } from '@creed-space/vcp-sdk';

const { registered, failed, api, cleanup } = await registerVCPTools({
  chatEndpoint: '/api/chat',
});

// registered = ['vcp_chat', 'vcp_list_personas']
// failed identifies any browser-rejected registrations.
// cleanup() aborts all accepted registrations and is safe to call repeatedly.
```

To consume the source-only candidate from another local project:

```bash
git clone https://github.com/Creed-Space/VCP-SDK.git
cd VCP-SDK
npm --prefix webmcp ci
npm --prefix webmcp test
npm --prefix webmcp run build
npm install ./webmcp
```

Bind the checkout to an immutable commit recorded in the coordinated candidate
manifest before using it as release evidence.

## Tools Registered

| Tool | Description | Requires |
|------|-------------|----------|
| `vcp_chat` | Chat with a VCP-aware AI assistant | `chatEndpoint` |
| `vcp_build_token` | Encode VCP context to CSM-1 token | `tokenEncoder` |
| `vcp_parse_token` | Parse CSM-1 token back to structured data | `tokenParser` or `wasmParser` |
| `vcp_transmission_summary` | Privacy analysis — what's shared, withheld, influencing | `transmissionSummary` |
| `vcp_list_personas` | List available VCP personas | (always available) |

Tools are only registered when their dependencies are provided. The chat and personas tools are always available.

## Configuration

```typescript
interface VCPWebMCPConfig {
  chatEndpoint?: string;           // Default: '/api/chat'
  personas?: PersonaInfo[];        // Default: 7 standard VCP personas
  enableChat?: boolean;            // Default: true
  enableTokenBuilder?: boolean;    // Default: true
  enableTokenParser?: boolean;     // Default: true
  enableSummary?: boolean;         // Default: true
  enablePersonas?: boolean;        // Default: true
  tokenEncoder?: (ctx: Record<string, unknown>) => string;
  tokenParser?: (token: string) => unknown;
  wasmParser?: (token: string) => unknown;
  transmissionSummary?: (ctx: Record<string, unknown>) => TransmissionSummary;
  onToolCall?: (toolName: string) => void;
  onRegistrationError?: (failure: WebMCPRegistrationFailure) => void;
}
```

## Agent Activity Indicator

Every tool call emits a `webmcp:tool-call` CustomEvent on `window`:

```typescript
window.addEventListener('webmcp:tool-call', (e) => {
  console.log('Agent used:', e.detail.tool); // e.g. 'vcp_chat'
});
```

Use this to show "Agent Active" indicators in your UI.

## MCP-B Polyfill

For browsers without native WebMCP support, provide an application-owned,
bundled polyfill loader. The SDK deliberately does not inject remote scripts:

```typescript
import { loadPolyfillIfRequested } from '@creed-space/vcp-sdk/polyfill';

// Your build owns and pins this dependency.
await loadPolyfillIfRequested({
  loader: async () => { await import('@mcp-b/global'); },
  onError: (error) => reportPrivately(error),
});
```

The loader succeeds only when it exposes a usable `document.modelContext`
contract or the isolated legacy Navigator contract. The SDK does not inject
remote scripts and does not log loader errors by default.

## Browser Support

| Surface | Support statement |
|---|---|
| Generic JavaScript SDK | Modern browsers implementing ES2022 and required Web APIs |
| Native WebMCP | Experimental Chrome preview or origin-trial surface; current API is `document.modelContext` |
| Legacy preview | `navigator.modelContext` remains an isolated compatibility fallback |
| Other browsers | No native claim; an application-owned bundled polyfill may be used behind explicit opt-in |
| SSR | Safe; returns `{ api: 'unavailable', registered: [], failed: [] }` |

Last reviewed: 2026-08-17. WebMCP remains under active development, so version
numbers alone never establish browser support.

### Upstream contract monitoring

`upstream-contract.json` records the reviewed W3C Community Group source
commit, byte digest, size ceiling, and API fragments on which this adapter
depends. Run `python3 ../scripts/check_webmcp_upstream.py` from this directory
to compare that record with the bounded upstream source. The weekly
`WebMCP upstream contract` workflow retains JSON evidence and opens at most one
review issue when the source or required fragments change. It never updates
types, compatibility copy, package metadata, or release claims automatically.

## License

MIT
