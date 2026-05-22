import type { AuditFrameSummary, AuditRunSummary, AuditScanPoint } from '@/types/audit';
import type { AuditSuggestion } from '@/types/detection';
import type { ReportSummary } from '@/types/report';
import type { StreetViewTarget } from '@/types/streetView';
import { loadGoogleMaps } from '@/utils/googleMaps';
import { categoryLabels } from '@/utils/reportFormatting';

const COORDINATE_ROUTE_RE =
  /^coordinates:\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$/i;

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

export function auditRunToStreetViewTarget(
  run: AuditRunSummary,
  latitude: number,
  longitude: number,
  heading?: number | null,
  pitch?: number | null,
): StreetViewTarget {
  return {
    id: run.id,
    label: run.route_name,
    latitude,
    longitude,
    heading,
    pitch,
    description: run.notes,
    source: 'audit_run',
  };
}

export function scanPointToStreetViewTarget(
  run: AuditRunSummary,
  point: AuditScanPoint,
): StreetViewTarget {
  return auditRunToStreetViewTarget(
    run,
    point.latitude,
    point.longitude,
    point.heading,
    point.pitch,
  );
}

export function pickInitialScanPoint(
  scanPath: AuditScanPoint[],
): AuditScanPoint | null {
  if (!scanPath.length) {
    return null;
  }
  return scanPath.find((point) => point.is_civic_issue) ?? scanPath[0] ?? null;
}

export async function resolveAuditRunStreetViewTarget(
  run: AuditRunSummary,
  fetchFrames?: (runId: string) => Promise<AuditFrameSummary[]>,
): Promise<StreetViewTarget | null> {
  if (run.scan_latitude != null && run.scan_longitude != null) {
    return auditRunToStreetViewTarget(run, run.scan_latitude, run.scan_longitude);
  }

  const coordinateMatch = COORDINATE_ROUTE_RE.exec(run.route_name.trim());
  if (coordinateMatch) {
    return auditRunToStreetViewTarget(
      run,
      Number(coordinateMatch[1]),
      Number(coordinateMatch[2]),
    );
  }

  if (fetchFrames) {
    const frames = await fetchFrames(run.id);
    const firstFrame = frames[0];
    if (firstFrame) {
      return auditRunToStreetViewTarget(
        run,
        firstFrame.latitude,
        firstFrame.longitude,
        firstFrame.heading,
        firstFrame.pitch,
      );
    }
  }

  return null;
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

export async function snapToStreetViewAtCoordinates(
  latitude: number,
  longitude: number,
): Promise<{ latitude: number; longitude: number; description?: string } | null> {
  const maps = await loadGoogleMaps();
  const service = new maps.StreetViewService();

  for (const radius of [STREET_VIEW_SEARCH_RADIUS_METERS, STREET_VIEW_FALLBACK_RADIUS_METERS]) {
    for (const source of [maps.StreetViewSource.OUTDOOR, maps.StreetViewSource.DEFAULT] as const) {
      const data = await new Promise<google.maps.StreetViewPanoramaData | null>((resolve) => {
        service.getPanorama(
          {
            location: { lat: latitude, lng: longitude },
            preference: maps.StreetViewPreference.NEAREST,
            radius,
            source,
          },
          (result, status) => {
            resolve(status === maps.StreetViewStatus.OK && result ? result : null);
          },
        );
      });

      const latLng = data?.location?.latLng;
      if (latLng) {
        return {
          latitude: Number(latLng.lat().toFixed(6)),
          longitude: Number(latLng.lng().toFixed(6)),
          description: data.location?.description ?? undefined,
        };
      }
    }
  }

  return null;
}
