import { describe, expect, it } from 'vitest';

import type { AuditScanPoint } from '@/types/audit';
import type { AuditSuggestion } from '@/types/detection';
import {
  enrichScanPathWithSuggestionStatus,
  upsertScanPoint,
} from './auditScanPath';

const basePoint = (frameIndex: number, suggestionId?: string): AuditScanPoint => ({
  frame_index: frameIndex,
  latitude: 42.21,
  longitude: 20.74,
  heading: 40,
  pitch: 0,
  is_civic_issue: Boolean(suggestionId),
  severity: suggestionId ? 'high' : null,
  suggestion_id: suggestionId ?? null,
});

describe('auditScanPath utilities', () => {
  it('upserts scan points by frame index', () => {
    const initial = [basePoint(0), basePoint(1)];
    const updated = upsertScanPoint(initial, {
      ...basePoint(1),
      is_civic_issue: true,
      severity: 'medium',
      suggestion_id: 'suggestion-1',
    });

    expect(updated).toHaveLength(2);
    expect(updated[1]?.suggestion_id).toBe('suggestion-1');
  });

  it('enriches scan points with suggestion review status', () => {
    const scanPath = [basePoint(2, 'suggestion-1'), basePoint(3, 'suggestion-2')];
    const suggestions = [
      { id: 'suggestion-1', status: 'converted_to_report' },
      { id: 'suggestion-2', status: 'rejected' },
    ] as AuditSuggestion[];

    const enriched = enrichScanPathWithSuggestionStatus(scanPath, suggestions);

    expect(enriched[0]?.suggestion_status).toBe('converted_to_report');
    expect(enriched[1]?.suggestion_status).toBe('rejected');
  });
});
