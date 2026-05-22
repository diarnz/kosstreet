import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';

export const SEVERITY_COLORS: Record<AuditSuggestionSeverity, string> = {
  low: '#22c55e',
  medium: '#eab308',
  high: '#ef4444',
  critical: '#b91c1c',
};

export const SEVERITY_LABELS: Record<AuditSuggestionSeverity, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
};

export const SEVERITY_DEFAULT_RADIUS: Record<AuditSuggestionSeverity, number> = {
  low: 0.06,
  medium: 0.09,
  high: 0.12,
  critical: 0.14,
};

export function getPrimaryRegion(
  regions?: DetectionRegion[] | null,
): DetectionRegion | null {
  if (!regions?.length) {
    return null;
  }
  return regions[0] ?? null;
}

export function getSeverityColor(severity?: AuditSuggestionSeverity | null): string {
  if (!severity) {
    return SEVERITY_COLORS.medium;
  }
  return SEVERITY_COLORS[severity];
}

export function boundingBoxToRegion(box: {
  x: number;
  y: number;
  width: number;
  height: number;
}): DetectionRegion {
  return {
    center_x: box.x + box.width / 2,
    center_y: box.y + box.height / 2,
    radius: Math.max(box.width, box.height) / 2,
  };
}

export function regionMarkerStyle(region: DetectionRegion) {
  const diameter = region.radius * 200;
  return {
    left: `${region.center_x * 100}%`,
    top: `${region.center_y * 100}%`,
    width: `${diameter}%`,
    height: `${diameter}%`,
    borderColor: 'rgba(255, 255, 255, 0.95)',
  };
}

export function svgCircleProps(region: DetectionRegion) {
  return {
    cx: region.center_x * 100,
    cy: region.center_y * 100,
    r: region.radius * 100,
  };
}
