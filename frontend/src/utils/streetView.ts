import type { AuditSuggestion } from '@/types/detection';
import type { ReportSummary } from '@/types/report';
import type { StreetViewTarget } from '@/types/streetView';
import { categoryLabels } from '@/utils/reportFormatting';

export const STREET_VIEW_SEARCH_RADIUS_METERS = 50;
export const STREET_VIEW_FALLBACK_RADIUS_METERS = 100;

export function hasValidCoordinates(target: Pick<StreetViewTarget, 'latitude' | 'longitude'>): boolean {
  return (
    Number.isFinite(target.latitude) &&
    Number.isFinite(target.longitude) &&
    target.latitude >= -90 &&
    target.latitude <= 90 &&
    target.longitude >= -180 &&
    target.longitude <= 180
  );
}

export function reportToStreetViewTarget(report: ReportSummary): StreetViewTarget {
  return {
    id: report.id,
    label: categoryLabels[report.category],
    latitude: report.latitude,
    longitude: report.longitude,
    description: report.description,
    source: 'report',
  };
}

export function suggestionToStreetViewTarget(suggestion: AuditSuggestion): StreetViewTarget {
  return {
    id: suggestion.id,
    label: categoryLabels[suggestion.category],
    latitude: suggestion.latitude,
    longitude: suggestion.longitude,
    heading: suggestion.heading,
    pitch: suggestion.pitch,
    description: suggestion.description,
    source: 'audit_suggestion',
  };
}

export function getStreetViewPov(target: StreetViewTarget): google.maps.StreetViewPov | undefined {
  if (target.heading === null && target.pitch === null) {
    return undefined;
  }

  if (target.heading === undefined && target.pitch === undefined) {
    return undefined;
  }

  return {
    heading: target.heading ?? 0,
    pitch: target.pitch ?? 0,
  };
}
