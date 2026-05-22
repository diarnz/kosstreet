import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { BadgeTone } from '@/types/ui';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export type RegionOverlayVariant = 'classic' | 'neon';

/** Default overlay look. Set to `classic` to revert to the original flat circles. */
export const DEFAULT_REGION_OVERLAY_VARIANT: RegionOverlayVariant = 'neon';

export interface SeverityCircleStyle {
  stroke: string;
  fill: string;
}

export interface NeonSeverityCircleStyle {
  fill: string;
  fillOpacity: number;
  breatheMinOpacity: number;
  breatheMaxOpacity: number;
  breatheMinScale: number;
  breatheMaxScale: number;
  breatheDuration: number;
}

export interface SeverityLegendItem {
  severity: AuditSuggestionSeverity;
  label: string;
  stroke: string;
  description: string;
}

export interface RegionOverlayPosition {
  centerXPercent: number;
  centerYPercent: number;
  radiusPercent: number;
}

export interface RegionTooltipContent {
  title: string;
  body: string;
}

/** Original flat circle palette — kept as the rollback base. */
export const CLASSIC_SEVERITY_CIRCLE_STYLES: Record<AuditSuggestionSeverity, SeverityCircleStyle> = {
  low: {
    stroke: '#22c55e',
    fill: 'rgba(34, 197, 94, 0.22)',
  },
  medium: {
    stroke: '#eab308',
    fill: 'rgba(234, 179, 8, 0.24)',
  },
  high: {
    stroke: '#ef4444',
    fill: 'rgba(239, 68, 68, 0.22)',
  },
  critical: {
    stroke: '#b91c1c',
    fill: 'rgba(185, 28, 28, 0.24)',
  },
};

/** Soft translucent disks — single fill, no outline, gentle breathe animation. */
export const NEON_SEVERITY_CIRCLE_STYLES: Record<AuditSuggestionSeverity, NeonSeverityCircleStyle> = {
  low: {
    fill: '#22c55e',
    fillOpacity: 0.32,
    breatheMinOpacity: 0.22,
    breatheMaxOpacity: 0.42,
    breatheMinScale: 0.94,
    breatheMaxScale: 1.06,
    breatheDuration: 3.2,
  },
  medium: {
    fill: '#eab308',
    fillOpacity: 0.3,
    breatheMinOpacity: 0.2,
    breatheMaxOpacity: 0.4,
    breatheMinScale: 0.94,
    breatheMaxScale: 1.06,
    breatheDuration: 3.2,
  },
  high: {
    fill: '#ef4444',
    fillOpacity: 0.28,
    breatheMinOpacity: 0.18,
    breatheMaxOpacity: 0.38,
    breatheMinScale: 0.93,
    breatheMaxScale: 1.07,
    breatheDuration: 3,
  },
  critical: {
    fill: '#dc2626',
    fillOpacity: 0.26,
    breatheMinOpacity: 0.16,
    breatheMaxOpacity: 0.36,
    breatheMinScale: 0.92,
    breatheMaxScale: 1.08,
    breatheDuration: 2.8,
  },
};

const severityBadgeTones: Record<AuditSuggestionSeverity, BadgeTone> = {
  low: 'severity-low',
  medium: 'severity-medium',
  high: 'severity-high',
  critical: 'severity-critical',
};

export const SEVERITY_LEGEND_ITEMS: SeverityLegendItem[] = [
  {
    severity: 'low',
    label: 'Low',
    stroke: NEON_SEVERITY_CIRCLE_STYLES.low.fill,
    description: 'Minor issue; monitor or schedule routine maintenance.',
  },
  {
    severity: 'medium',
    label: 'Medium',
    stroke: NEON_SEVERITY_CIRCLE_STYLES.medium.fill,
    description: 'Noticeable issue affecting street usability.',
  },
  {
    severity: 'high',
    label: 'High',
    stroke: NEON_SEVERITY_CIRCLE_STYLES.high.fill,
    description: 'Significant hazard requiring timely municipal action.',
  },
  {
    severity: 'critical',
    label: 'Critical',
    stroke: NEON_SEVERITY_CIRCLE_STYLES.critical.fill,
    description: 'Severe hazard with urgent safety impact.',
  },
];

export function resolveApiAssetUrl(path: string | null | undefined): string | null {
  if (!path) {
    return null;
  }

  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}

export function getSeverityCircleStyle(
  severity: AuditSuggestionSeverity | null | undefined,
  variant: RegionOverlayVariant = DEFAULT_REGION_OVERLAY_VARIANT,
): SeverityCircleStyle {
  const resolvedSeverity = severity ?? 'medium';

  if (variant === 'classic') {
    return CLASSIC_SEVERITY_CIRCLE_STYLES[resolvedSeverity] ?? CLASSIC_SEVERITY_CIRCLE_STYLES.medium;
  }

  const neon = NEON_SEVERITY_CIRCLE_STYLES[resolvedSeverity] ?? NEON_SEVERITY_CIRCLE_STYLES.medium;
  return {
    stroke: 'transparent',
    fill: `rgba(${hexToRgb(neon.fill)}, ${neon.fillOpacity})`,
  };
}

export function getNeonSeverityCircleStyle(
  severity: AuditSuggestionSeverity | null | undefined,
): NeonSeverityCircleStyle {
  if (!severity) {
    return NEON_SEVERITY_CIRCLE_STYLES.medium;
  }

  return NEON_SEVERITY_CIRCLE_STYLES[severity] ?? NEON_SEVERITY_CIRCLE_STYLES.medium;
}

export function getSeverityBadgeTone(
  severity: AuditSuggestionSeverity | null | undefined,
): BadgeTone {
  if (!severity) {
    return 'neutral';
  }

  return severityBadgeTones[severity] ?? 'neutral';
}

export function formatSeverityLabel(
  severity: AuditSuggestionSeverity | null | undefined,
): string {
  if (!severity) {
    return 'Not set';
  }

  return severity.replace(/_/g, ' ');
}

export function regionOverlayPosition(region: DetectionRegion): RegionOverlayPosition {
  return {
    centerXPercent: region.center_x * 100,
    centerYPercent: region.center_y * 100,
    radiusPercent: region.radius * 100,
  };
}

export function buildRegionTooltipContent(options: {
  category?: string | null;
  confidence?: number | null;
  description?: string | null;
  severity?: AuditSuggestionSeverity | null;
}): RegionTooltipContent {
  const titleParts: string[] = [];

  if (options.category) {
    titleParts.push(options.category);
  }

  if (options.severity) {
    titleParts.push(formatSeverityLabel(options.severity));
  }

  const title = titleParts.length > 0 ? titleParts.join(' · ') : 'AI-estimated issue';
  const bodyParts: string[] = [];

  if (options.confidence !== null && options.confidence !== undefined) {
    bodyParts.push(`Confidence ${formatConfidence(options.confidence)}`);
  }

  if (options.description) {
    bodyParts.push(options.description);
  }

  return {
    title,
    body: bodyParts.join(' · ') || 'Approximate location estimated by the vision model.',
  };
}

export function buildFrameTileLabel(options: {
  frameIndex: number;
  heading: number;
  isCivicIssue: boolean;
  category?: string | null;
  severity?: AuditSuggestionSeverity | null;
}): string {
  const frameNumber = options.frameIndex + 1;

  if (!options.isCivicIssue) {
    return `Frame ${frameNumber}, heading ${options.heading} degrees, no issue detected`;
  }

  const category = options.category ?? 'issue';
  const severity = options.severity ? formatSeverityLabel(options.severity) : 'unspecified severity';

  return `Frame ${frameNumber}, heading ${options.heading} degrees, ${category}, ${severity}`;
}

export function neonLegendSwatchStyle(
  severity: AuditSuggestionSeverity,
): Record<string, string> {
  const style = NEON_SEVERITY_CIRCLE_STYLES[severity];

  return {
    borderColor: 'transparent',
    backgroundColor: `rgba(${hexToRgb(style.fill)}, ${style.fillOpacity})`,
  };
}

function hexToRgb(hex: string): string {
  const normalized = hex.replace('#', '');
  const value =
    normalized.length === 3
      ? normalized
          .split('')
          .map((char) => char + char)
          .join('')
      : normalized;

  const red = Number.parseInt(value.slice(0, 2), 16);
  const green = Number.parseInt(value.slice(2, 4), 16);
  const blue = Number.parseInt(value.slice(4, 6), 16);

  return `${red}, ${green}, ${blue}`;
}
