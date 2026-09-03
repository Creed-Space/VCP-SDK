/**
 * VCP 3.1 Personal State Extensions
 *
 * Categorical personal dimensions with intensity (1-5) and exponential decay.
 * Layer 3 reflects self-reported state for adaptation only — not diagnostic.
 */

// === Enums ===

export const PersonalDimension = {
  COGNITIVE_STATE: 'cognitive_state',
  EMOTIONAL_TONE: 'emotional_tone',
  ENERGY_LEVEL: 'energy_level',
  PERCEIVED_URGENCY: 'perceived_urgency',
  BODY_SIGNALS: 'body_signals',
} as const;

export type PersonalDimension = (typeof PersonalDimension)[keyof typeof PersonalDimension];

export const CognitiveStateValue = {
  FOCUSED: 'focused',
  DISTRACTED: 'distracted',
  OVERLOADED: 'overloaded',
  FOGGY: 'foggy',
  REFLECTIVE: 'reflective',
} as const;

export type CognitiveStateValue = (typeof CognitiveStateValue)[keyof typeof CognitiveStateValue];

export const EmotionalToneValue = {
  CALM: 'calm',
  TENSE: 'tense',
  FRUSTRATED: 'frustrated',
  NEUTRAL: 'neutral',
  UPLIFTED: 'uplifted',
} as const;

export type EmotionalToneValue = (typeof EmotionalToneValue)[keyof typeof EmotionalToneValue];

export const EnergyLevelValue = {
  RESTED: 'rested',
  LOW_ENERGY: 'low_energy',
  FATIGUED: 'fatigued',
  WIRED: 'wired',
  DEPLETED: 'depleted',
} as const;

export type EnergyLevelValue = (typeof EnergyLevelValue)[keyof typeof EnergyLevelValue];

export const PerceivedUrgencyValue = {
  UNHURRIED: 'unhurried',
  TIME_AWARE: 'time_aware',
  PRESSURED: 'pressured',
  CRITICAL: 'critical',
} as const;

export type PerceivedUrgencyValue = (typeof PerceivedUrgencyValue)[keyof typeof PerceivedUrgencyValue];

export const BodySignalsValue = {
  NEUTRAL: 'neutral',
  DISCOMFORT: 'discomfort',
  PAIN: 'pain',
  UNWELL: 'unwell',
  RECOVERING: 'recovering',
} as const;

export type BodySignalsValue = (typeof BodySignalsValue)[keyof typeof BodySignalsValue];

export const SignalSource = {
  DECLARED: 'declared',
  INFERRED: 'inferred',
  INFERRED_LOCAL: 'inferred_local',
  PRESET: 'preset',
  DECAYED: 'decayed',
} as const;

export type SignalSource = (typeof SignalSource)[keyof typeof SignalSource];

export const LifecycleState = {
  SET: 'set',
  ACTIVE: 'active',
  DECAYING: 'decaying',
  STALE: 'stale',
  EXPIRED: 'expired',
} as const;

export type LifecycleState = (typeof LifecycleState)[keyof typeof LifecycleState];

// === Interfaces ===

export interface PersonalSignal {
  /** Categorical value (e.g., 'focused', 'calm') */
  readonly category: string;
  /** Signal intensity 1-5 (default 3) */
  readonly intensity: number;
  /** How this signal was obtained */
  readonly source: SignalSource;
  /** Confidence 0.0-1.0 */
  readonly confidence: number;
  /** When signal was declared (ISO8601 string or Date) */
  readonly declaredAt: string | null;
}

export interface PersonalContext {
  readonly cognitiveState: PersonalSignal | null;
  readonly emotionalTone: PersonalSignal | null;
  readonly energyLevel: PersonalSignal | null;
  readonly perceivedUrgency: PersonalSignal | null;
  readonly bodySignals: PersonalSignal | null;
}

export interface DecayConfig {
  readonly halfLifeSeconds: number;
  readonly baseline: number;
  readonly pinned: boolean;
  readonly resetOnEngagement: boolean;
  /** Fraction of the declared range above baseline below which the signal is STALE (default 0.3). */
  readonly staleThreshold?: number;
  /** Seconds after declaration during which the signal stays ACTIVE (default 60). */
  readonly freshWindowSeconds?: number;
}

/** Fallbacks when a DecayConfig omits the lifecycle fields (VCP-X-Personal §3.2). */
export const DEFAULT_STALE_THRESHOLD = 0.3;
export const DEFAULT_FRESH_WINDOW_SECONDS = 60;

// === Default Decay Configs (VCP-X-Personal §3.3) ===

export const DEFAULT_DECAY_CONFIGS: Readonly<Record<string, DecayConfig>> = {
  perceived_urgency: {
    halfLifeSeconds: 900, // 15 min
    baseline: 1,
    pinned: false,
    resetOnEngagement: false,
    staleThreshold: 0.35,
    freshWindowSeconds: 60,
  },
  body_signals: {
    halfLifeSeconds: 14400, // 4 hours
    baseline: 1,
    pinned: false,
    resetOnEngagement: false,
    staleThreshold: 0.15,
    freshWindowSeconds: 600, // 10 min
  },
  cognitive_state: {
    halfLifeSeconds: 720, // 12 min
    baseline: 1,
    pinned: false,
    resetOnEngagement: true,
    staleThreshold: 0.3,
    freshWindowSeconds: 60,
  },
  emotional_tone: {
    halfLifeSeconds: 1800, // 30 min
    baseline: 1,
    pinned: false,
    resetOnEngagement: false,
    staleThreshold: 0.25,
    freshWindowSeconds: 60,
  },
  energy_level: {
    halfLifeSeconds: 7200, // 2 hours
    baseline: 1,
    pinned: false,
    resetOnEngagement: false,
    staleThreshold: 0.2,
    freshWindowSeconds: 300, // 5 min
  },
} as const;

// === Decay Functions ===

/**
 * Compute decayed intensity based on exponential decay.
 *
 * result = max(baseline, floor(baseline + (declared - baseline) * exp(-lambda * t)))
 *
 * Matches the Python SDK's `compute_decayed_intensity` function.
 */
function elapsedSecondsBetween(declaredTime: Date, currentTime: Date): number {
  if (Number.isNaN(declaredTime.getTime())) {
    throw new RangeError('declaredAt must be a valid ISO 8601 timestamp');
  }
  if (Number.isNaN(currentTime.getTime())) {
    throw new RangeError('now must be a valid Date');
  }
  return (currentTime.getTime() - declaredTime.getTime()) / 1000;
}

export function computeDecayedIntensity(
  declaredIntensity: number,
  declaredAt: string | Date,
  config: DecayConfig,
  now?: Date,
): number {
  if (config.pinned) {
    return declaredIntensity;
  }

  const currentTime = now ?? new Date();
  const declaredTime = typeof declaredAt === 'string' ? new Date(declaredAt) : declaredAt;
  const elapsedSeconds = elapsedSecondsBetween(declaredTime, currentTime);

  if (elapsedSeconds <= 0) {
    return declaredIntensity;
  }

  const lambda = Math.LN2 / config.halfLifeSeconds;
  const decayedFloat =
    config.baseline +
    (declaredIntensity - config.baseline) * Math.exp(-lambda * elapsedSeconds);

  return Math.max(config.baseline, Math.floor(decayedFloat));
}

/**
 * Compute lifecycle state for a personal dimension signal.
 *
 * Matches the Python SDK's `compute_lifecycle_state` function.
 * Uses the config's fresh window (ACTIVE before DECAYING) and stale
 * threshold, falling back to 60s / 0.3 when the config omits them.
 */
export function computeLifecycleState(
  declaredIntensity: number,
  declaredAt: string | Date,
  config: DecayConfig,
  now?: Date,
): LifecycleState {
  if (config.pinned) {
    return LifecycleState.ACTIVE;
  }

  const currentTime = now ?? new Date();
  const declaredTime = typeof declaredAt === 'string' ? new Date(declaredAt) : declaredAt;
  const elapsedSeconds = elapsedSecondsBetween(declaredTime, currentTime);

  if (elapsedSeconds <= 0) {
    return LifecycleState.SET;
  }

  const freshWindowSeconds = config.freshWindowSeconds ?? DEFAULT_FRESH_WINDOW_SECONDS;
  if (elapsedSeconds < freshWindowSeconds) {
    return LifecycleState.ACTIVE;
  }

  const effective = computeDecayedIntensity(declaredIntensity, declaredAt, config, currentTime);

  if (effective <= config.baseline) {
    return LifecycleState.EXPIRED;
  }

  // Stale threshold: fraction of the declared range above baseline
  const staleThreshold = config.staleThreshold ?? DEFAULT_STALE_THRESHOLD;
  const staleLevel = config.baseline + (declaredIntensity - config.baseline) * staleThreshold;

  if (effective <= staleLevel) {
    return LifecycleState.STALE;
  }

  return LifecycleState.DECAYING;
}
