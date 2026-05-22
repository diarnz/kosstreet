import type { ReportSummary } from '@/types/report';

/** Default template city for maps, search bias, and demo data. */
export const PRIZREN_VIEWPORT = {
  center: {
    latitude: 42.2139,
    longitude: 20.7397,
  },
  zoom: 14,
} as const;

/** @deprecated Use PRIZREN_VIEWPORT */
export const PRISHTINA_VIEWPORT = PRIZREN_VIEWPORT;

export const KOSOVO_BOUNDS = {
  north: 43.27,
  south: 41.85,
  east: 21.82,
  west: 20.02,
} as const;

export function hasValidCoordinates(report: ReportSummary): boolean {
  return (
    Number.isFinite(report.latitude) &&
    Number.isFinite(report.longitude) &&
    report.latitude >= -90 &&
    report.latitude <= 90 &&
    report.longitude >= -180 &&
    report.longitude <= 180
  );
}

export function getMappableReports(reports: ReportSummary[]): ReportSummary[] {
  return reports.filter(hasValidCoordinates);
}

export function getHiddenMapReportCount(reports: ReportSummary[]): number {
  return reports.length - getMappableReports(reports).length;
}

export function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
