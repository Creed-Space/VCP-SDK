import { describe, expect, it } from "vitest";
import fc from "fast-check";

import { SchulzeElection } from "../src/extensions/consensus.js";
import {
  decodeContext,
  decodePersonalState,
  encodeContext,
  encodePersonalState,
  makePersonalState,
} from "../src/extensions/context.js";
import { negotiate } from "../src/extensions/negotiation.js";

const PROPERTY_OPTIONS = { numRuns: 500, seed: 0x564350 } as const;
const identifier = fc.stringMatching(/^[a-z][a-z0-9_]{0,31}$/);
const extensionIdentifier = fc
  .stringMatching(/^[A-Za-z][A-Za-z0-9-]{0,31}$/)
  .map((suffix) => `VCP-X-${suffix}`);
const coreFeatures = {
  encryption: true,
  injection_scanning: true,
  revocation: true,
  audit_chain: true,
  context_opacity: true,
} as const;

describe("deterministic generative invariants", () => {
  it("round-trips protocol-safe personal state values", () => {
    fc.assert(
      fc.property(
        identifier,
        fc.option(fc.integer({ min: 1, max: 5 }), { nil: null }),
        (value, intensity) => {
          const state = makePersonalState(value, intensity);
          expect(decodePersonalState(encodePersonalState(state))).toEqual(
            state,
          );
        },
      ),
      PROPERTY_OPTIONS,
    );
  });

  it("partitions requested capabilities without loss or invention", () => {
    fc.assert(
      fc.property(
        fc.uniqueArray(extensionIdentifier, { maxLength: 32 }),
        fc.uniqueArray(extensionIdentifier, { maxLength: 32 }),
        (requested, supported) => {
          const result = negotiate(
            {
              type: "vcp-hello",
              version: "3.1",
              min_version: "1.0",
              extensions: requested,
            },
            {
              supported_versions: ["1.0", "3.1"],
              extensions: Object.fromEntries(
                supported.map((extension) => [extension, {}]),
              ),
              core_features: coreFeatures,
            },
          );
          expect(result.type).toBe("vcp-ack");
          if (result.type !== "vcp-ack") return;
          const supportedSet = new Set(supported);
          expect(result.supported).toEqual(
            requested.filter((capability) => supportedSet.has(capability)),
          );
          expect(result.unsupported).toEqual(
            requested.filter((capability) => !supportedSet.has(capability)),
          );
          expect(
            [
              ...result.supported,
              ...result.unsupported,
            ].sort(),
          ).toEqual([...requested].sort());
        },
      ),
      PROPERTY_OPTIONS,
    );
  });

  it("selects the first choice from every complete single ballot", () => {
    fc.assert(
      fc.property(
        fc.uniqueArray(identifier, { minLength: 1, maxLength: 12 }),
        (candidates) => {
          const election = new SchulzeElection(candidates);
          election.addBallot({
            voterId: "property-voter",
            rankings: candidates.map((candidate) => [candidate]),
          });
          const result = election.compute();
          expect(result.winner).toBe(candidates[0]);
          expect(result.candidates).toEqual(candidates);
          expect(result.pairwiseMatrix).toHaveLength(candidates.length);
          expect(result.strongestPaths).toHaveLength(candidates.length);
        },
      ),
      PROPERTY_OPTIONS,
    );
  });

  it("normalizes arbitrary bounded wire input idempotently", () => {
    fc.assert(
      fc.property(fc.string({ maxLength: 256 }), (wire) => {
        const canonical = encodeContext(decodeContext(wire));
        expect(encodeContext(decodeContext(canonical))).toBe(canonical);
      }),
      PROPERTY_OPTIONS,
    );
  });
});
