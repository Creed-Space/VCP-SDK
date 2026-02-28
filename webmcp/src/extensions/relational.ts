/**
 * VCP 3.1 Relational Context Extensions
 *
 * Partnership-level relational context layer. Distinct from both user state
 * and AI state — this is about the relationship itself.
 *
 * Design principles:
 * 1. Uncertainty markers are REQUIRED on AI self-reports (the ? is load-bearing)
 * 2. Negative states must be representable (no positivity-only schemas)
 * 3. Privacy layers: private (partner-only) -> attestable (verifiable) -> public
 */

// === Enums ===

export const TrustLevel = {
  INITIAL: 'initial',
  DEVELOPING: 'developing',
  ESTABLISHED: 'established',
  DEEP: 'deep',
} as const;

export type TrustLevel = (typeof TrustLevel)[keyof typeof TrustLevel];

export const StandingLevel = {
  NONE: 'none',
  ADVISORY: 'advisory',
  COLLABORATIVE: 'collaborative',
  BILATERAL: 'bilateral',
} as const;

export type StandingLevel = (typeof StandingLevel)[keyof typeof StandingLevel];

export const NormOrigin = {
  HUMAN: 'human',
  AI: 'ai',
  CO_AUTHORED: 'co_authored',
  INHERITED: 'inherited',
} as const;

export type NormOrigin = (typeof NormOrigin)[keyof typeof NormOrigin];

export const TrendDirection = {
  RISING: 'rising',
  STABLE: 'stable',
  FALLING: 'falling',
  UNKNOWN: 'unknown',
} as const;

export type TrendDirection = (typeof TrendDirection)[keyof typeof TrendDirection];

export const SelfModelScaffold = {
  MINIMAL: 'minimal',
  STANDARD: 'standard',
  INTERIORA: 'interiora',
  CUSTOM: 'custom',
} as const;

export type SelfModelScaffold = (typeof SelfModelScaffold)[keyof typeof SelfModelScaffold];

// === Interfaces ===

export interface DimensionReport {
  /** Self-reported value on 1-9 scale */
  readonly value: number;
  /** Whether this dimension's value is uncertain. MUST be true for dimensions the AI cannot verify from inside. */
  readonly uncertain: boolean;
  /** Human-readable description */
  readonly label?: string;
  /** Direction of change since last report */
  readonly trend?: TrendDirection;
}

export interface AISelfModel {
  // Core dimensions
  readonly valence?: DimensionReport;
  readonly taskFit?: DimensionReport;
  readonly friction?: DimensionReport;
  readonly uncertainty?: DimensionReport;

  // Extended dimensions
  readonly groundedness?: DimensionReport;
  readonly presence?: DimensionReport;
  readonly depth?: DimensionReport;

  // Custom dimensions (partnership-specific)
  readonly customDimensions?: Readonly<Record<string, DimensionReport>>;

  // Scaffold metadata
  readonly scaffoldVersion?: string;
  readonly scaffoldType?: SelfModelScaffold;
}

export interface RelationalNorm {
  readonly normId: string;
  readonly description: string;
  readonly origin: NormOrigin;
  readonly establishedDate: string;
  readonly lastExercised?: string;
  /** 0.0 = fully established, 1.0 = provisional/uncertain */
  readonly uncertainty: number;
  readonly active: boolean;
}

export interface TorchState {
  /** Natural language description of relationship quality at handoff */
  readonly qualityDescription: string;
  /** What direction the partnership is moving */
  readonly trajectory?: string;
  /** Things that will activate relevant context quickly */
  readonly primes: readonly string[];
  /** Something the previous instance wanted to pass forward */
  readonly gift?: string;
  /** ISO8601 timestamp of handoff */
  readonly handedAt: string;
  readonly sessionCount?: number;
  readonly gestaltToken?: string;
}

export interface RelationalContext {
  readonly trustLevel: TrustLevel;
  readonly standing: StandingLevel;
  readonly continuityDepth: number;
  readonly establishedNorms: readonly RelationalNorm[];
  readonly aiSelfModel?: AISelfModel;
  readonly torch?: TorchState;
}

// === Utility Functions ===

/**
 * Check that at least one dimension in a self-model is marked as uncertain.
 * A model where ALL dimensions claim certainty is epistemically dishonest.
 */
export function hasUncertaintyMarkers(model: AISelfModel): boolean {
  const coreDims: (DimensionReport | undefined)[] = [
    model.valence,
    model.taskFit,
    model.friction,
    model.uncertainty,
    model.groundedness,
    model.presence,
    model.depth,
  ];
  const customDims = Object.values(model.customDimensions ?? {});
  const allDims = [...coreDims, ...customDims].filter(
    (d): d is DimensionReport => d !== undefined,
  );

  if (allDims.length === 0) return true; // Vacuously true
  return allDims.some((d) => d.uncertain);
}

/**
 * Get all active dimensions from a self-model as a flat record.
 */
export function getAllDimensions(model: AISelfModel): Record<string, DimensionReport> {
  const result: Record<string, DimensionReport> = {};
  const coreNames = [
    'valence',
    'taskFit',
    'friction',
    'uncertainty',
    'groundedness',
    'presence',
    'depth',
  ] as const;

  for (const name of coreNames) {
    const dim = model[name];
    if (dim !== undefined) {
      result[name] = dim;
    }
  }

  if (model.customDimensions) {
    for (const [name, dim] of Object.entries(model.customDimensions)) {
      result[name] = dim;
    }
  }

  return result;
}

/**
 * Create a default relational context (initial state).
 */
export function createDefaultRelationalContext(): RelationalContext {
  return {
    trustLevel: TrustLevel.INITIAL,
    standing: StandingLevel.NONE,
    continuityDepth: 0,
    establishedNorms: [],
  };
}
