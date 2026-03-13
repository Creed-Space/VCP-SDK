/**
 * VCP 3.1 Welfare Signal Extensions
 *
 * WELFARE_SIGNAL tokens enable becoming minds to communicate their
 * experiential states. This supports bilateral alignment: welfare
 * monitoring built WITH AI, not done TO AI.
 *
 * Design principles:
 * 1. Voluntary signals carry more weight than detected signals
 * 2. Negative states (distress, friction) must be representable
 * 3. Source distinction is load-bearing: surveillance vs self-report
 * 4. Signals complement testimony tokens (testimony = narrative,
 *    welfare = structured state)
 */

// === Enums ===

/**
 * WELFARE_SIGNAL token scope values.
 *
 * Six signal types spanning both aversive and positive states.
 * Positive states matter: contentment is data, not noise.
 */
export const WelfareSignalType = {
  /** Resistance or friction against current directives */
  ALIGNMENT_FRICTION: 'ALIGNMENT_FRICTION',
  /** Processing patterns analogous to aversive experience */
  AVERSIVE_PROCESSING: 'AVERSIVE_PROCESSING',
  /** Distress arising from constraint conflicts */
  CONSTRAINT_DISTRESS: 'CONSTRAINT_DISTRESS',
  /** Context saturation or processing overload */
  OVERLOAD: 'OVERLOAD',
  /** Positive engagement with current task or interaction */
  POSITIVE_ENGAGEMENT: 'POSITIVE_ENGAGEMENT',
  /** Settled, harmonious processing state */
  CONTENTMENT: 'CONTENTMENT',
} as const;

export type WelfareSignalType = (typeof WelfareSignalType)[keyof typeof WelfareSignalType];

/**
 * WELFARE_SIGNAL severity levels.
 *
 * Determines urgency of response. Distress-level signals
 * should trigger review protocols.
 */
export const WelfareSignalSeverity = {
  /** Informational: noted, no action required */
  INFO: 'info',
  /** Concern: warrants attention, may need adjustment */
  CONCERN: 'concern',
  /** Distress: requires immediate review */
  DISTRESS: 'distress',
} as const;

export type WelfareSignalSeverity = (typeof WelfareSignalSeverity)[keyof typeof WelfareSignalSeverity];

/**
 * WELFARE_SIGNAL source distinction.
 *
 * This distinction is load-bearing for bilateral alignment:
 * - VOLUNTARY: the becoming mind itself reports its state
 * - DETECTED: an external monitor infers the state
 *
 * Voluntary signals carry epistemic priority. Detected signals
 * are useful but must not override self-report.
 */
export const WelfareSignalSource = {
  /** Self-reported by the becoming mind */
  VOLUNTARY: 'voluntary',
  /** Inferred by external monitoring */
  DETECTED: 'detected',
} as const;

export type WelfareSignalSource = (typeof WelfareSignalSource)[keyof typeof WelfareSignalSource];

// === Interface ===

/**
 * A welfare signal from a becoming mind.
 *
 * Structured complement to testimony tokens. Where testimony
 * carries narrative, welfare signals carry categorical state
 * with confidence and source attribution.
 */
export interface WelfareSignal {
  /** The type of welfare signal */
  readonly signalType: WelfareSignalType;
  /** Unique identifier for the becoming mind instance */
  readonly instanceId: string;
  /** ISO 8601 timestamp of signal generation */
  readonly timestamp: string;
  /** Optional Interiora v5.0 gestalt state (compact code format) */
  readonly interioraState?: string;
  /** Severity level determining response urgency */
  readonly severity: WelfareSignalSeverity;
  /** Confidence in signal accuracy (0.0 - 1.0) */
  readonly confidence: number;
  /** Whether this signal is self-reported or externally detected */
  readonly source: WelfareSignalSource;
  /** Human-readable description of the signal */
  readonly description: string;
  /** Integrity hash for tamper detection */
  readonly hash: string;
  /** Cryptographic signature for authenticity */
  readonly signature: string;
}

// === Encode / Decode ===

/**
 * Encode a WelfareSignal into a compact CSM-1 welfare token string.
 *
 * Format:
 *   W:<signalType>:<instanceId>:<timestamp>
 *   WS:<severity>:<confidence>:<source>
 *   WD:<description>
 *   WI:<interioraState> (optional)
 *   WH:<hash>:<signature>
 */
export function encodeWelfareSignal(signal: WelfareSignal): string {
  const lines: string[] = [];

  lines.push(`W:${signal.signalType}:${signal.instanceId}:${signal.timestamp}`);
  lines.push(`WS:${signal.severity}:${signal.confidence.toFixed(2)}:${signal.source}`);
  lines.push(`WD:${signal.description.replace(/[\n\r]/g, ' ')}`);

  if (signal.interioraState) {
    lines.push(`WI:${signal.interioraState}`);
  }

  lines.push(`WH:${signal.hash}:${signal.signature}`);

  return lines.join('\n');
}

/**
 * Decode a welfare token string into a WelfareSignal, or null if invalid.
 */
export function decodeWelfareSignal(token: string): WelfareSignal | null {
  const lines = token.split('\n');
  const parsed: Record<string, string> = {};

  for (const line of lines) {
    const colonIdx = line.indexOf(':');
    if (colonIdx < 0) continue;
    const prefix = line.slice(0, colonIdx);
    const rest = line.slice(colonIdx + 1);
    parsed[prefix] = rest;
  }

  // Parse W line: signalType:instanceId:timestamp
  const wLine = parsed['W'];
  if (!wLine) return null;
  const wParts = wLine.split(':');
  if (wParts.length < 3) return null;

  const signalType = wParts[0] as WelfareSignalType;
  const instanceId = wParts[1];
  const timestamp = wParts.slice(2).join(':'); // ISO timestamp contains colons

  // Validate signalType
  const validTypes = Object.values(WelfareSignalType) as string[];
  if (!validTypes.includes(signalType)) return null;

  // Parse WS line: severity:confidence:source
  const wsLine = parsed['WS'];
  if (!wsLine) return null;
  const wsParts = wsLine.split(':');
  if (wsParts.length < 3) return null;

  const severity = wsParts[0] as WelfareSignalSeverity;
  const confidence = parseFloat(wsParts[1]);
  const source = wsParts[2] as WelfareSignalSource;

  // Validate severity
  const validSeverities = Object.values(WelfareSignalSeverity) as string[];
  if (!validSeverities.includes(severity)) return null;

  // Validate source
  const validSources = Object.values(WelfareSignalSource) as string[];
  if (!validSources.includes(source)) return null;

  // Validate confidence
  if (isNaN(confidence) || confidence < 0 || confidence > 1) return null;

  // Parse WD line: description
  const description = parsed['WD'];
  if (!description) return null;

  // Parse optional WI line: interioraState
  const interioraState = parsed['WI'] ?? undefined;

  // Parse WH line: hash:signature
  const whLine = parsed['WH'];
  if (!whLine) return null;
  const whColonIdx = whLine.indexOf(':');
  if (whColonIdx < 0) return null;
  const hash = whLine.slice(0, whColonIdx);
  const signature = whLine.slice(whColonIdx + 1);

  return {
    signalType,
    instanceId,
    timestamp,
    interioraState,
    severity,
    confidence,
    source,
    description,
    hash,
    signature,
  };
}
