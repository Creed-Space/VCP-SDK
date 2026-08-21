/**
 * VCP 3.1 capability negotiation.
 *
 * The public shapes intentionally mirror the normative wire names. Keeping
 * snake_case here makes it harder for an implementation-only camelCase model
 * to drift from the protocol again.
 */

export const VCPExtension = {
  PERSONAL: 'VCP-X-Personal',
  RELATIONAL: 'VCP-X-Relational',
  CONSENSUS: 'VCP-X-Consensus',
  TORCH: 'VCP-X-Torch',
  INTENT: 'VCP-X-Intent',
} as const;

export type VCPExtension = (typeof VCPExtension)[keyof typeof VCPExtension];

/** @deprecated Use VCPExtension. Retained as a source-compatible export name. */
export const VCPCapability = VCPExtension;
/** @deprecated Use VCPExtension. */
export type VCPCapability = VCPExtension;

export interface VCPHello {
  readonly type: 'vcp-hello';
  /** Highest VCP major.minor version the client supports. */
  readonly version: string;
  readonly extensions?: readonly string[];
  readonly identity?: string | null;
  /** Lowest acceptable VCP version. Defaults to 1.0. */
  readonly min_version?: string;
  readonly client_id?: string;
}

export interface VCPCoreFeatures {
  readonly encryption: boolean;
  readonly injection_scanning: boolean;
  readonly revocation: boolean;
  readonly audit_chain: boolean;
  readonly context_opacity: boolean;
}

export interface VCPServerCapabilities {
  readonly supported_versions: readonly string[];
  /** Map of extension identifier to its capability advertisement. */
  readonly extensions: Readonly<Record<string, Readonly<Record<string, unknown>>>>;
  readonly core_features: VCPCoreFeatures;
  readonly server_id?: string;
  readonly session_id?: string;
}

export interface VCPAck {
  readonly type: 'vcp-ack';
  readonly version: string;
  readonly supported: readonly string[];
  readonly unsupported: readonly string[];
  readonly capabilities: Readonly<Record<string, Readonly<Record<string, unknown>>>>;
  readonly core_features: VCPCoreFeatures;
  readonly server_id?: string;
  readonly session_id?: string;
}

export interface VCPError {
  readonly type: 'vcp-error';
  readonly code: 'VERSION_UNSUPPORTED';
  readonly message: string;
  readonly supported_versions: readonly string[];
  readonly retry_after: null;
}

export type VCPNegotiationResult = VCPAck | VCPError;

const VERSION_PATTERN = /^(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8})$/;
const EXTENSION_PATTERN = /^VCP-X-[A-Za-z][A-Za-z0-9-]*$/;
const MAX_REQUESTED_EXTENSIONS = 256;
const MAX_SERVER_VERSIONS = 64;
const MAX_EXTENSION_IDENTIFIER_LENGTH = 128;
const MAX_DIAGNOSTIC_IDENTIFIER_LENGTH = 256;
const MAX_SESSION_IDENTIFIER_LENGTH = 128;
const MAX_IDENTITY_LENGTH = 2048;
const MAX_HANDSHAKE_BYTES = 64 * 1024;

interface ParsedVersion {
  readonly source: string;
  readonly major: number;
  readonly minor: number;
}

function parseVersion(value: unknown): ParsedVersion | null {
  if (typeof value !== 'string') return null;
  const match = VERSION_PATTERN.exec(value);
  if (!match) return null;
  const major = Number(match[1]);
  const minor = Number(match[2]);
  if (!Number.isSafeInteger(major) || !Number.isSafeInteger(minor)) return null;
  return { source: value, major, minor };
}

function compareVersions(a: ParsedVersion, b: ParsedVersion): number {
  return a.major === b.major ? a.minor - b.minor : a.major - b.major;
}

function requireBoundedArray(value: unknown, name: string, limit: number): readonly unknown[] {
  if (!Array.isArray(value)) throw new TypeError(`${name} must be an array`);
  if (value.length > limit) throw new RangeError(`${name} exceeds ${limit} entries`);
  return value;
}

/** JSON Schema maxLength counts Unicode code points, not UTF-16 code units. */
function characterLength(value: string): number {
  return Array.from(value).length;
}

function validRequestedExtensions(value: unknown): string[] {
  const entries = value === undefined
    ? []
    : requireBoundedArray(value, 'hello.extensions', MAX_REQUESTED_EXTENSIONS);
  const seen = new Set<string>();
  const valid: string[] = [];
  for (const entry of entries) {
    if (typeof entry !== 'string') {
      throw new TypeError('hello.extensions entries must be strings');
    }
    const length = characterLength(entry);
    if (length === 0 || length > MAX_EXTENSION_IDENTIFIER_LENGTH) {
      throw new RangeError('hello.extensions entries must contain 1 to 128 characters');
    }
    if (seen.has(entry)) throw new TypeError(`duplicate hello extension: ${entry}`);
    seen.add(entry);
    // Bounded strings outside the extension namespace are ignored by spec.
    if (!EXTENSION_PATTERN.test(entry)) continue;
    valid.push(entry);
  }
  return valid;
}

function validateCoreFeatures(value: unknown): VCPCoreFeatures {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new TypeError('server.core_features must be an object');
  }
  const record = value as Record<string, unknown>;
  const names = [
    'encryption',
    'injection_scanning',
    'revocation',
    'audit_chain',
    'context_opacity',
  ] as const;
  for (const name of names) {
    if (typeof record[name] !== 'boolean') {
      throw new TypeError(`server.core_features.${name} must be a boolean`);
    }
  }
  return {
    encryption: record.encryption as boolean,
    injection_scanning: record.injection_scanning as boolean,
    revocation: record.revocation as boolean,
    audit_chain: record.audit_chain as boolean,
    context_opacity: record.context_opacity as boolean,
  };
}

function copyOptionalIdentifier(
  value: unknown,
  name: string,
  maximum = MAX_DIAGNOSTIC_IDENTIFIER_LENGTH,
): string | undefined {
  if (value === undefined) return undefined;
  if (
    typeof value !== 'string' ||
    characterLength(value) === 0 ||
    characterLength(value) > maximum
  ) {
    throw new TypeError(`${name} must be a non-empty string of at most ${maximum} characters`);
  }
  return value;
}

function copyCapability(value: Readonly<Record<string, unknown>>, name: string): Record<string, unknown> {
  try {
    const encoded = JSON.stringify(value, (_key, candidate: unknown) => {
      if (
        candidate === undefined ||
        typeof candidate === 'function' ||
        typeof candidate === 'symbol' ||
        typeof candidate === 'bigint' ||
        (typeof candidate === 'number' && !Number.isFinite(candidate))
      ) {
        throw new TypeError('not a JSON value');
      }
      return candidate;
    });
    if (encoded === undefined) throw new TypeError('not JSON serializable');
    return JSON.parse(encoded) as Record<string, unknown>;
  } catch {
    throw new TypeError(`${name} must be a JSON-serializable object`);
  }
}

function assertHandshakeSize(value: unknown): void {
  let encoded: string;
  try {
    const result = JSON.stringify(value, (_key, candidate: unknown) => {
      if (typeof candidate === 'number' && !Number.isFinite(candidate)) {
        throw new TypeError('not a finite JSON number');
      }
      return candidate;
    });
    if (result === undefined) throw new TypeError('not JSON serializable');
    encoded = result;
  } catch {
    throw new TypeError('handshake must be JSON serializable');
  }
  if (new TextEncoder().encode(encoded).byteLength > MAX_HANDSHAKE_BYTES) {
    throw new RangeError('handshake exceeds 64 KiB');
  }
}

function versionError(serverVersions: readonly ParsedVersion[]): VCPError {
  return {
    type: 'vcp-error',
    code: 'VERSION_UNSUPPORTED',
    message: 'No mutually supported VCP version',
    supported_versions: serverVersions.map((version) => version.source),
    retry_after: null,
  };
}

/**
 * Negotiate the highest mutually supported VCP version and requested extensions.
 * Invalid extension identifiers are ignored. Duplicate raw request strings are
 * rejected before filtering. Extensions are negotiated only at 3.1+.
 */
export function negotiate(
  hello: VCPHello,
  server: VCPServerCapabilities,
): VCPNegotiationResult {
  if (typeof hello !== 'object' || hello === null || hello.type !== 'vcp-hello') {
    throw new TypeError("hello.type must be 'vcp-hello'");
  }
  if (typeof server !== 'object' || server === null) {
    throw new TypeError('server must be an object');
  }
  assertHandshakeSize(hello);

  copyOptionalIdentifier(hello.client_id, 'hello.client_id');
  if (
    hello.identity !== undefined &&
    hello.identity !== null &&
    (typeof hello.identity !== 'string' ||
      characterLength(hello.identity) > MAX_IDENTITY_LENGTH)
  ) {
    throw new TypeError('hello.identity must be null or a string of at most 2048 characters');
  }

  const serverEntries = requireBoundedArray(
    server.supported_versions,
    'server.supported_versions',
    MAX_SERVER_VERSIONS,
  );
  const byVersion = new Map<string, ParsedVersion>();
  for (const entry of serverEntries) {
    const parsed = parseVersion(entry);
    if (!parsed) throw new TypeError('server.supported_versions entries must be major.minor');
    byVersion.set(parsed.source, parsed);
  }
  const serverVersions = [...byVersion.values()].sort(compareVersions);
  if (serverVersions.length === 0) {
    throw new RangeError('server.supported_versions must be non-empty');
  }
  const clientMax = parseVersion(hello.version);
  const clientMin = parseVersion(hello.min_version ?? '1.0');
  if (!clientMax || !clientMin || compareVersions(clientMin, clientMax) > 0) {
    return versionError(serverVersions);
  }

  const negotiated = serverVersions
    .filter(
      (version) =>
        compareVersions(version, clientMin) >= 0 &&
        compareVersions(version, clientMax) <= 0,
    )
    .at(-1);
  if (!negotiated) return versionError(serverVersions);

  const requested = validRequestedExtensions(hello.extensions);
  if (
    typeof server.extensions !== 'object' ||
    server.extensions === null ||
    Array.isArray(server.extensions)
  ) {
    throw new TypeError('server.extensions must be an object');
  }
  if (Object.keys(server.extensions).length > MAX_REQUESTED_EXTENSIONS) {
    throw new RangeError('server.extensions exceeds 256 entries');
  }
  for (const [identifier, capability] of Object.entries(server.extensions)) {
    if (
      characterLength(identifier) > MAX_EXTENSION_IDENTIFIER_LENGTH ||
      !EXTENSION_PATTERN.test(identifier)
    ) {
      throw new TypeError(`server.extensions has invalid identifier: ${identifier}`);
    }
    if (typeof capability !== 'object' || capability === null || Array.isArray(capability)) {
      throw new TypeError(`server.extensions.${identifier} must be an object`);
    }
  }
  const coreFeatures = validateCoreFeatures(server.core_features);
  const extensionNegotiationAvailable = compareVersions(
    negotiated,
    { source: '3.1', major: 3, minor: 1 },
  ) >= 0;
  const supported = extensionNegotiationAvailable
    ? requested.filter((identifier) => Object.hasOwn(server.extensions, identifier))
    : [];
  const supportedSet = new Set(supported);
  const unsupported = requested.filter((identifier) => !supportedSet.has(identifier));
  const capabilities: Record<string, Readonly<Record<string, unknown>>> = {};
  for (const identifier of supported) {
    const capability = server.extensions[identifier];
    const snapshot = copyCapability(capability, `server.extensions.${identifier}`);
    if (identifier === VCPExtension.TORCH && !supportedSet.has(VCPExtension.RELATIONAL)) {
      snapshot.degraded = true;
    }
    if (identifier === VCPExtension.INTENT && !supportedSet.has(VCPExtension.PERSONAL)) {
      snapshot.personal_signals = false;
    }
    capabilities[identifier] = Object.freeze(snapshot);
  }

  const serverId = copyOptionalIdentifier(server.server_id, 'server.server_id');
  const sessionId = copyOptionalIdentifier(
    server.session_id,
    'server.session_id',
    MAX_SESSION_IDENTIFIER_LENGTH,
  );
  const result: VCPAck = {
    type: 'vcp-ack',
    version: negotiated.source,
    supported,
    unsupported,
    capabilities,
    core_features: coreFeatures,
    ...(serverId === undefined ? {} : { server_id: serverId }),
    ...(sessionId === undefined ? {} : { session_id: sessionId }),
  };
  assertHandshakeSize(result);
  return result;
}

/** Create a canonical VCP 3.1 hello requesting every defined extension. */
export function createFullHello(clientId?: string, identity?: string | null): VCPHello {
  return {
    type: 'vcp-hello',
    version: '3.1',
    min_version: '1.0',
    extensions: Object.values(VCPExtension),
    ...(identity === undefined ? {} : { identity }),
    ...(clientId === undefined ? {} : { client_id: clientId }),
  };
}
