/**
 * VCP 3.1 Extension Modules
 *
 * Re-exports all extension types and functions.
 */

// Personal state signals
export {
  PersonalDimension,
  CognitiveStateValue,
  EmotionalToneValue,
  EnergyLevelValue,
  PerceivedUrgencyValue,
  BodySignalsValue,
  SignalSource,
  LifecycleState,
  DEFAULT_DECAY_CONFIGS,
  computeDecayedIntensity,
  computeLifecycleState,
} from './personal.js';
export type { PersonalSignal, PersonalContext, DecayConfig } from './personal.js';

// Relational context
export {
  TrustLevel,
  StandingLevel,
  NormOrigin,
  TrendDirection,
  SelfModelScaffold,
  hasUncertaintyMarkers,
  getAllDimensions,
  createDefaultRelationalContext,
} from './relational.js';
export type {
  DimensionReport,
  AISelfModel,
  RelationalNorm,
  TorchState,
  RelationalContext,
} from './relational.js';

// Consensus voting
export { SchulzeElection } from './consensus.js';
export type {
  Ballot,
  SchulzeRanking,
  PairwiseResult,
  ElectionResult,
} from './consensus.js';

// Torch handoff
export {
  TorchGenerator,
  TorchConsumer,
  createEmptyLineage,
  appendToLineage,
} from './torch.js';
export type { TorchSummary, TorchLineage } from './torch.js';

// Negotiation
export {
  VCPCapability,
  negotiate,
  createFullHello,
} from './negotiation.js';
export type { VCPHello, VCPAck } from './negotiation.js';

// VCP/A Situational + Personal-state context encoder (v3.2, incl. VEP-0004)
export {
  SituationalDimension,
  PersonalStateDimension,
  SITUATIONAL_SPECS,
  SITUATIONAL_ORDER,
  PERSONAL_STATE_SPECS,
  PERSONAL_STATE_ORDER,
  PERSONAL_SEPARATOR,
  DIM_SEPARATOR,
  INTENSITY_SEPARATOR,
  makePersonalState,
  encodePersonalState,
  decodePersonalState,
  emptyContext,
  encodeContext,
  decodeContext,
  contextToJSON,
  contextFromJSON,
  conformanceLevel,
  buildContext,
} from './context.js';
export type {
  SituationalDimensionSpec,
  PersonalStateDimensionSpec,
  PersonalState,
  VCPContext,
  VCPContextJSON,
  ConformanceLevel,
  EncoderInput,
} from './context.js';
