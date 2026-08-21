#!/usr/bin/env node

import { readFile } from 'node:fs/promises';

import {
  StandingLevel,
  TorchConsumer,
  TrustLevel,
  createDefaultRelationalContext,
  getAllDimensions,
  hasUncertaintyMarkers,
} from '../dist/index.js';

const [path] = process.argv.slice(2);
if (!path) throw new Error('usage: run-relational.mjs <relational-fixture.json>');

const document = JSON.parse(await readFile(path, 'utf8'));
if (
  typeof document !== 'object' ||
  document === null ||
  !Array.isArray(document.test_cases)
) {
  throw new TypeError('relational fixture must contain a test_cases array');
}

function toSelfModel(value) {
  const model = {};
  const names = {
    valence: 'valence',
    task_fit: 'taskFit',
    friction: 'friction',
    uncertainty: 'uncertainty',
    groundedness: 'groundedness',
    presence: 'presence',
    depth: 'depth',
  };
  for (const [wireName, runtimeName] of Object.entries(names)) {
    if (value[wireName] !== undefined) model[runtimeName] = value[wireName];
  }
  if (value.custom_dimensions !== undefined) {
    model.customDimensions = value.custom_dimensions;
  }
  return model;
}

function receiveSessionCount(sessionCount) {
  return new TorchConsumer().receiveTorch({
    qualityDescription: '',
    primes: [],
    handedAt: '1970-01-01T00:00:00.000Z',
    sessionCount,
  });
}

function execute(testCase) {
  const { id, input, expected } = testCase;
  if (id === 'trust-level-ordering') {
    return { trust_levels: Object.values(TrustLevel) };
  }
  if (id === 'standing-level-ordering') {
    return { standing_levels: Object.values(StandingLevel) };
  }
  if (id.startsWith('trust-from-session-count-')) {
    if (id.endsWith('-boundaries')) {
      return {
        boundaries: expected.boundaries.map(({ session_count }) => ({
          session_count,
          trust_level: receiveSessionCount(session_count).trustLevel,
        })),
      };
    }
    return { trust_level: receiveSessionCount(input.session_count).trustLevel };
  }
  if (id === 'self-model-valid' || id === 'self-model-no-uncertainty-invalid') {
    const model = toSelfModel(input.ai_self_model);
    return {
      valid: true,
      has_uncertainty_markers: hasUncertaintyMarkers(model),
      dimension_count: Object.keys(getAllDimensions(model)).length,
    };
  }
  if (id === 'relational-context-defaults') {
    const context = createDefaultRelationalContext();
    return {
      trust_level: context.trustLevel,
      standing: context.standing,
      continuity_depth: context.continuityDepth,
      established_norms: context.establishedNorms,
      ai_self_model: context.aiSelfModel ?? null,
      torch: context.torch ?? null,
    };
  }
  if (id === 'torch-receive-bootstraps-context') {
    const torch = input.torch;
    const context = new TorchConsumer().receiveTorch({
      qualityDescription: torch.quality_description,
      trajectory: torch.trajectory,
      primes: torch.primes,
      gift: torch.gift,
      handedAt: torch.handed_at,
      sessionCount: torch.session_count,
    });
    return {
      trust_level: context.trustLevel,
      standing: context.standing,
      continuity_depth: context.continuityDepth,
    };
  }
  return null;
}

const results = document.test_cases.map((testCase) => {
  const actual = execute(testCase);
  return actual === null
    ? { id: testCase.id, status: 'not_applicable' }
    : { id: testCase.id, status: 'checked', actual };
});
process.stdout.write(`${JSON.stringify(results)}\n`);
