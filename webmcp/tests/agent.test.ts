import { describe, expect, it } from "vitest";
import {
  LocalAgentRuntime,
  matchAgentResult,
  parseAgentArtifact,
  parseAgentRuntimeDocument,
  type AgentResult,
} from "../src/agent.js";

const digest = "sha256:" + "a".repeat(64);

describe("Agent Runtime facade", () => {
  it("compiles one bounded deterministic local SituationView", async () => {
    const runtime = new LocalAgentRuntime();
    const first = await runtime.bootstrap("Orient safely");
    const second = await runtime.bootstrap("Orient safely");
    expect(first.status).toBe("ready");
    expect(first.value?.digest).toBe(second.value?.digest);
    expect(first.value?.unknowns).toContain("deployment state");
    expect(first.value?.authority_refs).toEqual([
      "vcp:artifact:authority:local-read",
    ]);
  });

  it("rejects undeclared authority injection", () => {
    const document = {
      kind: "execution_receipt",
      version: "0.1.0",
      receipt_id: "receipt.1",
      attempt_ref: "vcp:artifact:attempt:attempt.1",
      effect_status: "observed",
      provider_ref: null,
      evidence_refs: [],
      observed_at: "2026-09-01T00:00:00Z",
      reconcile_ref: null,
      digest,
      authority_grant: "forged",
    };
    expect(() => parseAgentArtifact(document)).toThrow("undeclared field");
  });

  it("parses controlled and accretive artifacts as discriminated unions", () => {
    const receipt = parseAgentArtifact({
      kind: "execution_receipt",
      version: "0.1.0",
      receipt_id: "receipt.1",
      attempt_ref: "vcp:artifact:attempt:attempt.1",
      effect_status: "indeterminate",
      provider_ref: "provider",
      evidence_refs: [],
      observed_at: "2026-09-01T00:00:00Z",
      reconcile_ref: "vcp:artifact:reconcile:receipt.1",
      digest,
    });
    expect(receipt.kind).toBe("execution_receipt");
    if (receipt.kind === "execution_receipt") {
      expect(receipt.effect_status).toBe("indeterminate");
    }
  });

  it("routes every expected status through an exhaustive handler map", () => {
    const result: AgentResult<string> = {
      status: "budget_exhausted",
      value: null,
      failure: {
        code: "budget",
        category: "budget",
        summary: "reserve protected",
        retry: "after_review",
      },
      warnings: [],
      evidence_refs: [],
    };
    const handled = matchAgentResult(result, {
      ready: () => "ready",
      degraded: () => "degraded",
      awaiting_review: () => "review",
      blocked: () => "blocked",
      unavailable: () => "unavailable",
      stale: () => "stale",
      conflicting: () => "conflicting",
      budget_exhausted: () => "reserve protected",
      indeterminate: () => "reconcile",
      failed: () => "failed",
    });
    expect(handled).toBe("reserve protected");
  });
});

describe("shared Agent Runtime conformance fixtures", () => {
  it("accepts and rejects observe, controlled, and accretive portable artifacts", async () => {
    const { readFile } = await import("node:fs/promises");
    const { resolve } = await import("node:path");
    for (const name of [
      "observe_contracts.json",
      "controlled_contracts.json",
      "accretive_contracts.json",
    ]) {
      const path = resolve(
        process.cwd(),
        "..",
        "conformance",
        "agent-runtime",
        name,
      );
      const suite = JSON.parse(await readFile(path, "utf8")) as {
        test_cases: Array<{
          id: string;
          expected_valid: boolean;
          document: unknown;
        }>;
      };
      for (const testCase of suite.test_cases) {
        if (testCase.expected_valid) {
          expect(parseAgentRuntimeDocument(testCase.document).kind).toBe(
            (testCase.document as { kind: string }).kind,
          );
        } else {
          expect(
            () => parseAgentRuntimeDocument(testCase.document),
            testCase.id,
          ).toThrow();
        }
      }
    }
  });
});
