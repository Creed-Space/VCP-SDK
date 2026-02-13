# @vcp/webmcp

Register VCP capabilities as discoverable tools for AI agents via the [WebMCP API](https://webmcp.org) (`navigator.modelContext`).

**Status**: 0.1.0 — Used in production on [VCP Demo](https://vcp-demo.onrender.com) and [Creed Space](https://creed.space).

## Quick Start

```typescript
import { registerVCPTools } from '@vcp/webmcp';

const { registered, cleanup } = await registerVCPTools({
  chatEndpoint: '/api/chat',
});

// registered = ['vcp_chat', 'vcp_list_personas']
// cleanup() to unregister all tools
```

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

For browsers without native WebMCP support, use the MCP-B polyfill:

```typescript
import { loadPolyfillIfRequested } from '@vcp/webmcp/polyfill';

// Loads @mcp-b/global from CDN when ?webmcp=polyfill is in the URL
await loadPolyfillIfRequested();
```

## Browser Support

- **Chrome 145+**: Native `navigator.modelContext` API
- **Other browsers**: Use MCP-B polyfill (`?webmcp=polyfill`)
- **SSR**: Safe to call — returns empty result immediately

## License

MIT
