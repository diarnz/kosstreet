import type { ReportSummary } from '@/types/report';

export const PRISHTINA_VIEWPORT = {
  center: {
    latitude: 42.6629,
    longitude: 21.1655,
  },
  zoom: 13,
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
