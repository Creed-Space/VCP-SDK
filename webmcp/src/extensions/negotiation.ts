/**
 * VCP 3.1 Negotiation — Protocol Handshake
 *
 * Implements the VCP hello/ack negotiation for capability discovery
 * between a client and server.
 */

// === Interfaces ===

export interface VCPHello {
  /** Protocol version the client supports */
  readonly version: string;
  /** Capabilities the client requests */
  readonly requestedCapabilities: readonly string[];
  /** Client identifier */
  readonly clientId?: string;
  /** Constitutional reference */
  readonly constitutionRef?: string;
}

export interface VCPAck {
  /** Negotiated protocol version */
  readonly version: string;
  /** Capabilities the server agrees to provide */
  readonly grantedCapabilities: readonly string[];
  /** Capabilities the server does not support */
  readonly deniedCapabilities: readonly string[];
  /** Server identifier */
  readonly serverId?: string;
  /** Whether the negotiation succeeded */
  readonly success: boolean;
  /** Reason for partial or full denial */
  readonly reason?: string;
}

/** Known VCP 3.1 capabilities */
export const VCPCapability = {
  /** Categorical context (9 situational dimensions) */
  CATEGORICAL_CONTEXT: 'categorical_context',
  /** Personal state signals (5 dimensions with intensity) */
  PERSONAL_CONTEXT: 'personal_context',
  /** Signal decay computation */
  SIGNAL_DECAY: 'signal_decay',
  /** Relational context layer */
  RELATIONAL_CONTEXT: 'relational_context',
  /** Torch session handoff */
  TORCH_HANDOFF: 'torch_handoff',
  /** AI self-model in relational context */
  AI_SELF_MODEL: 'ai_self_model',
  /** Schulze consensus voting */
  CONSENSUS_VOTING: 'consensus_voting',
  /** Generation preferences (user-steerable sliders) */
  GENERATION_PREFS: 'generation_prefs',
  /** VCP attestation chain */
  ATTESTATION: 'attestation',
  /** Inter-agent context messaging */
  INTER_AGENT: 'inter_agent',
} as const;

export type VCPCapability = (typeof VCPCapability)[keyof typeof VCPCapability];

// === Negotiation Function ===

/**
 * Negotiate VCP capabilities between client hello and server capabilities.
 *
 * Grants capabilities that both the client requests and the server supports.
 * Denies capabilities the client requests but the server does not support.
 */
export function negotiate(
  hello: VCPHello,
  serverCapabilities: readonly string[],
): VCPAck {
  const serverSet = new Set(serverCapabilities);

  const granted: string[] = [];
  const denied: string[] = [];

  for (const cap of hello.requestedCapabilities) {
    if (serverSet.has(cap)) {
      granted.push(cap);
    } else {
      denied.push(cap);
    }
  }

  const success = denied.length === 0;

  return {
    version: hello.version,
    grantedCapabilities: granted,
    deniedCapabilities: denied,
    success,
    reason: success
      ? undefined
      : `Server does not support: ${denied.join(', ')}`,
  };
}

/**
 * Create a standard VCP 3.1 hello requesting all capabilities.
 */
export function createFullHello(clientId?: string, constitutionRef?: string): VCPHello {
  return {
    version: '3.1.0',
    requestedCapabilities: Object.values(VCPCapability),
    clientId,
    constitutionRef,
  };
}
