import type { AuditFrameDetail, AuditFrameSummary, AuditScanPoint } from '@/types/audit';
import type { AuditSuggestion } from '@/types/detection';

export function frameDetailToScanPoint(frame: AuditFrameDetail): AuditScanPoint {
  return {
    frame_index: frame.frame_index,
    latitude: frame.latitude,
    longitude: frame.longitude,
    heading: frame.heading,
    pitch: frame.pitch,
    is_civic_issue: frame.is_civic_issue,
    severity: frame.severity ?? null,
    suggestion_id: frame.suggestion_id ?? null,
    scan_source: frame.scan_source ?? 'pipeline',
  };
}

export function frameDetailToSummary(frame: AuditFrameDetail): AuditFrameSummary {
  return {
    frame_index: frame.frame_index,
    latitude: frame.latitude,
    longitude: frame.longitude,
    heading: frame.heading,
    pitch: frame.pitch,
    is_civic_issue: frame.is_civic_issue,
    category: frame.category ?? null,
    confidence: frame.confidence ?? null,
    severity: frame.severity ?? null,
    description: frame.description ?? null,
    suggestion_id: frame.suggestion_id ?? null,
    frame_image_url: frame.frame_image_url,
  };
}

export function upsertScanPoint(
  scanPath: AuditScanPoint[],
  point: AuditScanPoint,
): AuditScanPoint[] {
  const next = [...scanPath];
  const existingIndex = next.findIndex((entry) => entry.frame_index === point.frame_index);

  if (existingIndex >= 0) {
    next[existingIndex] = point;
  } else {
    next.push(point);
  }

  return next.sort((left, right) => left.frame_index - right.frame_index);
}

export function upsertFrameSummary(
  frames: AuditFrameSummary[],
  frame: AuditFrameSummary,
): AuditFrameSummary[] {
  const next = [...frames];
  const existingIndex = next.findIndex((entry) => entry.frame_index === frame.frame_index);

  if (existingIndex >= 0) {
    next[existingIndex] = frame;
  } else {
    next.push(frame);
  }

  return next.sort((left, right) => left.frame_index - right.frame_index);
}

export function enrichScanPathWithSuggestionStatus(
  scanPath: AuditScanPoint[],
  suggestions: AuditSuggestion[],
): AuditScanPoint[] {
  const statusBySuggestionId = new Map(
    suggestions.map((suggestion) => [suggestion.id, suggestion.status]),
  );

  return scanPath.map((point) => ({
    ...point,
    suggestion_status: point.suggestion_id
      ? (statusBySuggestionId.get(point.suggestion_id) ?? null)
      : null,
  }));
}
