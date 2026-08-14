import { hrtime } from 'node:process';

import { SchulzeElection } from '../dist/extensions/consensus.js';
import { decodeContext, encodeContext } from '../dist/extensions/context.js';

const argumentIndex = process.argv.indexOf('--iterations');
const parsedIterations = argumentIndex === -1 ? 20_000 : Number(process.argv[argumentIndex + 1]);
const iterations = Number.isSafeInteger(parsedIterations) ? Math.max(parsedIterations, 100) : 20_000;

function summarize(name, samplesNs) {
  samplesNs.sort((left, right) => left - right);
  const totalNs = samplesNs.reduce((sum, sample) => sum + sample, 0);
  const p95Index = Math.max(Math.ceil(samplesNs.length * 0.95) - 1, 0);
  return {
    name,
    iterations: samplesNs.length,
    ops_per_second: samplesNs.length / (totalNs / 1_000_000_000),
    p50_us: samplesNs[Math.floor(samplesNs.length / 2)] / 1_000,
    p95_us: samplesNs[p95Index] / 1_000,
  };
}

const context = {
  situational: {
    time: ['🌅'],
    space: ['🏢'],
    relationship: ['colleague:professional'],
  },
  personal: {
    cognitive_state: { value: 'focused', intensity: 4 },
    energy_level: { value: 'high', intensity: 5 },
  },
};

let sink;
for (let index = 0; index < 1_000; index += 1) {
  sink = decodeContext(encodeContext(context));
}
const contextSamples = [];
for (let index = 0; index < iterations; index += 1) {
  const start = hrtime.bigint();
  sink = decodeContext(encodeContext(context));
  contextSamples.push(Number(hrtime.bigint() - start));
}

const candidates = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
const ballotCount = 30;
const consensusIterations = Math.max(Math.floor(iterations / 20), 100);
const consensusSamples = [];
for (let index = 0; index < consensusIterations; index += 1) {
  const election = new SchulzeElection(candidates);
  for (let ballot = 0; ballot < ballotCount; ballot += 1) {
    const rotation = ballot % candidates.length;
    const ranking = [...candidates.slice(rotation), ...candidates.slice(0, rotation)];
    election.addBallot({
      voterId: `voter-${ballot}`,
      rankings: ranking.map((candidate) => [candidate]),
    });
  }
  const start = hrtime.bigint();
  sink = election.compute();
  consensusSamples.push(Number(hrtime.bigint() - start));
}

if (sink === undefined) {
  throw new Error('performance probe produced no result');
}

process.stdout.write(
  `${JSON.stringify({
    runtime: 'node',
    metrics: [
      summarize('webmcp_context_roundtrip', contextSamples),
      summarize('webmcp_consensus_7x30', consensusSamples),
    ],
  })}\n`,
);
