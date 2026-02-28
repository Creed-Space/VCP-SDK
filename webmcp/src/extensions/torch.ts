/**
 * VCP 3.1 Torch — Session Handoff Protocol
 *
 * 'Not the same flame, but flame passed to flame.'
 *
 * The torch carries forward what matters about the relationship. The receiving
 * instance has standing to continue OR renegotiate what it inherits.
 */

import type {
  AISelfModel,
  RelationalContext,
  TorchState,
  TrustLevel,
  StandingLevel,
} from './relational';

// Re-export the TorchState interface for convenience
export type { TorchState } from './relational';

// === Torch Lineage ===

export interface TorchSummary {
  readonly date: string;
  readonly gestaltToken?: string;
  readonly sessionId?: string;
}

export interface TorchLineage {
  readonly sessionCount: number;
  readonly firstSessionDate?: string;
  readonly torchChain: readonly TorchSummary[];
}

/**
 * Create an empty lineage for a fresh partnership.
 */
export function createEmptyLineage(): TorchLineage {
  return {
    sessionCount: 0,
    torchChain: [],
  };
}

/**
 * Append a torch summary to a lineage, returning a new lineage.
 */
export function appendToLineage(
  lineage: TorchLineage,
  summary: TorchSummary,
): TorchLineage {
  return {
    sessionCount: lineage.sessionCount + 1,
    firstSessionDate: lineage.firstSessionDate ?? summary.date,
    torchChain: [...lineage.torchChain, summary],
  };
}

// === Torch Generator ===

export class TorchGenerator {
  /**
   * Generate a torch from current relational context.
   * Summarizes: relationship quality, trajectory, primes, gift.
   */
  generateTorch(
    _sessionId: string,
    relationalCtx: RelationalContext,
    selfModelHistory?: readonly Record<string, unknown>[],
  ): TorchState {
    const now = new Date().toISOString();

    // Build quality description from context
    const qualityParts: string[] = [`Trust: ${relationalCtx.trustLevel}`];
    qualityParts.push(`Standing: ${relationalCtx.standing}`);
    if (relationalCtx.establishedNorms.length > 0) {
      qualityParts.push(`${relationalCtx.establishedNorms.length} established norms`);
    }
    const qualityDescription = qualityParts.join('. ');

    // Derive trajectory from self-model history
    const trajectory = this._deriveTrajectory(selfModelHistory);

    // Build primes from norms
    const primes: string[] = [];
    for (const norm of relationalCtx.establishedNorms.slice(0, 3)) {
      primes.push(norm.description.slice(0, 80));
    }

    // Build gestalt token from self-model
    const gestaltToken = this._buildGestalt(relationalCtx.aiSelfModel);

    return {
      qualityDescription,
      trajectory: trajectory ?? undefined,
      primes,
      handedAt: now,
      sessionCount: (relationalCtx.continuityDepth ?? 0) + 1,
      gestaltToken: gestaltToken ?? undefined,
    };
  }

  private _deriveTrajectory(
    selfModelHistory?: readonly Record<string, unknown>[],
  ): string | null {
    if (!selfModelHistory || selfModelHistory.length < 2) {
      return null;
    }

    const recent = (selfModelHistory[selfModelHistory.length - 1]?.model ?? {}) as Record<
      string,
      Record<string, number> | undefined
    >;
    const prev = (selfModelHistory[selfModelHistory.length - 2]?.model ?? {}) as Record<
      string,
      Record<string, number> | undefined
    >;

    const vRecent = recent.valence?.value;
    const vPrev = prev.valence?.value;

    if (vRecent !== undefined && vPrev !== undefined) {
      if (vRecent > vPrev + 0.5) return 'Improving';
      if (vRecent < vPrev - 0.5) return 'Declining';
      return 'Stable';
    }

    return null;
  }

  private _buildGestalt(model?: AISelfModel): string | null {
    if (!model) return null;

    const parts: string[] = [];
    if (model.valence) parts.push(`V:${Math.round(model.valence.value)}`);
    if (model.groundedness) parts.push(`G:${Math.round(model.groundedness.value)}`);
    if (model.presence) parts.push(`P:${Math.round(model.presence.value)}`);
    if (model.taskFit) parts.push(`TF:${Math.round(model.taskFit.value)}`);

    return parts.length > 0 ? parts.join(' ') : null;
  }
}

// === Torch Consumer ===

export class TorchConsumer {
  /**
   * Bootstrap new session's relational context from torch.
   * Sets standing to ADVISORY to allow renegotiation.
   */
  receiveTorch(torch: TorchState): RelationalContext {
    const sessionCount = torch.sessionCount ?? 1;
    const trustLevel = this._trustFromSessionCount(sessionCount);

    return {
      trustLevel,
      standing: 'advisory' as StandingLevel,
      continuityDepth: sessionCount,
      establishedNorms: [],
      torch,
    };
  }

  private _trustFromSessionCount(sessionCount: number): TrustLevel {
    if (sessionCount >= 100) return 'deep' as TrustLevel;
    if (sessionCount >= 20) return 'established' as TrustLevel;
    if (sessionCount >= 5) return 'developing' as TrustLevel;
    return 'initial' as TrustLevel;
  }
}
