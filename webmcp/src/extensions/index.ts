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
} from './personal';
export type { PersonalSignal, PersonalContext, DecayConfig } from './personal';

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
} from './relational';
export type {
  DimensionReport,
  AISelfModel,
  RelationalNorm,
  TorchState,
  RelationalContext,
} from './relational';

// Consensus voting
export { SchulzeElection } from './consensus';
export type {
  Ballot,
  SchulzeRanking,
  PairwiseResult,
  ElectionResult,
} from './consensus';

// Torch handoff
export {
  TorchGenerator,
  TorchConsumer,
  createEmptyLineage,
  appendToLineage,
} from './torch';
export type { TorchSummary, TorchLineage } from './torch';

// Negotiation
export {
  VCPCapability,
  negotiate,
  createFullHello,
} from './negotiation';
export type { VCPHello, VCPAck } from './negotiation';

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
} from './context';
export type {
  SituationalDimensionSpec,
  PersonalStateDimensionSpec,
  PersonalState,
  VCPContext,
  VCPContextJSON,
  ConformanceLevel,
  EncoderInput,
} from './context';
