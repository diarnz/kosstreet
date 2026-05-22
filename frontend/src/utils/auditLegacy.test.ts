import { describe, expect, it } from 'vitest';

import { isLegacyAuditRun } from './auditLegacy';

describe('isLegacyAuditRun', () => {
  it('detects legacy runs with four-heading frame fan-out', () => {
    expect(isLegacyAuditRun({ frames_total: 64 }, 16)).toBe(true);
  });

  it('does not flag single-heading scan runs', () => {
    expect(isLegacyAuditRun({ frames_total: 16 }, 16)).toBe(false);
  });

  it('falls back to frame total heuristic when scan path is empty', () => {
    expect(isLegacyAuditRun({ frames_total: 64 }, 0)).toBe(true);
    expect(isLegacyAuditRun({ frames_total: 15 }, 0)).toBe(false);
  });
});
