import type { AuditSuggestionSeverity, BoundingBox } from '@/types/detection';

export interface DetectionCircle {
  x: number;
  y: number;
  radius: number;
}

export function boundingBoxToCircle(box: BoundingBox): DetectionCircle {
  return {
    x: box.x + box.width / 2,
    y: box.y + box.height / 2,
    radius: Math.max(box.width, box.height) / 2,
  };
}

export function getSeverityCircleTone(
  severity?: AuditSuggestionSeverity | null,
): 'low' | 'medium' | 'high' {
  if (severity === 'high' || severity === 'critical') {
    return 'high';
  }

  if (severity === 'low') {
    return 'low';
  }

  return 'medium';
}
