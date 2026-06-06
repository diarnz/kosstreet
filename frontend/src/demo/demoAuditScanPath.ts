import type { AuditFrameDetail, AuditFrameSummary, AuditScanPoint } from '@/types/audit';
import type { IssueCategory } from '@/types/report';
import { demoAuditSuggestions } from '@/demo/demoAuditSuggestions';
import {
  DEMO_AUDIT_RUN_ID,
  DEMO_AUDIT_RUN_LEGACY_ID,
  DEMO_SCAN_POINT_COUNT,
} from '@/demo/demoAuditConstants';

export { DEMO_AUDIT_RUN_ID, DEMO_AUDIT_RUN_LEGACY_ID, DEMO_SCAN_POINT_COUNT };

const DEMO_HEADINGS = [0, 90, 180, 270] as const;

type DemoDetection = {
  frameIndex: number;
  suggestionId: string;
  severity: NonNullable<AuditScanPoint['severity']>;
  category: IssueCategory;
  imageUrl: string;
  description: string;
  confidence: number;
  latitude: number;
  longitude: number;
};

const DEMO_DETECTIONS: DemoDetection[] = [
  {
    frameIndex: 4,
    suggestionId: 'demo-suggestion-pothole-001',
    severity: 'high',
    category: 'pothole',
    imageUrl: '/demo/audit/pothole_01.jpg',
    description: 'Likely road-surface depression near a vehicle lane.',
    confidence: 0.82,
    latitude: 42.2141,
    longitude: 20.7403,
  },
  {
    frameIndex: 9,
    suggestionId: 'demo-suggestion-garbage-001',
    severity: 'medium',
    category: 'garbage',
    imageUrl: '/demo/audit/garbage_01.jpg',
    description: 'Possible illegal dumping next to public bins.',
    confidence: 0.76,
    latitude: 42.21485,
    longitude: 20.74105,
  },
  {
    frameIndex: 13,
    suggestionId: 'demo-suggestion-sidewalk-001',
    severity: 'low',
    category: 'blocked_sidewalk',
    imageUrl: '/demo/audit/sidewalk_01.jpg',
    description: 'Possible pedestrian obstruction along a sidewalk segment.',
    confidence: 0.71,
    latitude: 42.21535,
    longitude: 20.74155,
  },
];

function detectionByFrameIndex(frameIndex: number): DemoDetection | undefined {
  return DEMO_DETECTIONS.find((detection) => detection.frameIndex === frameIndex);
}

function corridorPoint(index: number): { latitude: number; longitude: number; heading: number } {
  const startLatitude = 42.213502;
  const startLongitude = 20.7397;
  return {
    latitude: Number((startLatitude + index * 0.00012).toFixed(6)),
    longitude: Number((startLongitude + index * 0.0001).toFixed(6)),
    heading: (38 + index * 3) % 360,
  };
}

export function buildDemoScanPath(runId: string): AuditScanPoint[] {
  if (runId !== DEMO_AUDIT_RUN_ID && runId !== DEMO_AUDIT_RUN_LEGACY_ID) {
    return [];
  }

  return Array.from({ length: DEMO_SCAN_POINT_COUNT }, (_, frameIndex) => {
    const point = corridorPoint(frameIndex);
    const detection = detectionByFrameIndex(frameIndex);

    return {
      frame_index: frameIndex,
      latitude: detection?.latitude ?? point.latitude,
      longitude: detection?.longitude ?? point.longitude,
      heading: point.heading,
      pitch: 0,
      is_civic_issue: Boolean(detection),
      severity: detection?.severity ?? null,
      suggestion_id: detection?.suggestionId ?? null,
      scan_source: 'pipeline',
    };
  });
}

function frameImageUrl(runId: string, frameIndex: number): string {
  const detection = detectionByFrameIndex(frameIndex);
  if (detection) {
    return detection.imageUrl;
  }
  return `/demo/audit/clean_01.jpg`;
}

export function buildDemoFrames(runId: string): AuditFrameSummary[] {
  if (runId === DEMO_AUDIT_RUN_LEGACY_ID) {
    return buildLegacyDemoFrames(runId);
  }

  if (runId !== DEMO_AUDIT_RUN_ID) {
    return [];
  }

  return buildDemoScanPath(runId).map((point) => {
    const detection = detectionByFrameIndex(point.frame_index);
    return {
      frame_index: point.frame_index,
      latitude: point.latitude,
      longitude: point.longitude,
      heading: point.heading,
      pitch: point.pitch,
      is_civic_issue: point.is_civic_issue,
      category: detection?.category ?? null,
      confidence: detection?.confidence ?? null,
      severity: point.severity ?? null,
      description: detection?.description ?? null,
      suggestion_id: point.suggestion_id ?? null,
      frame_image_url: frameImageUrl(runId, point.frame_index),
    };
  });
}

function buildLegacyDemoFrames(runId: string): AuditFrameSummary[] {
  const scanPath = buildDemoScanPath(DEMO_AUDIT_RUN_ID);
  const frames: AuditFrameSummary[] = [];
  let frameIndex = 0;

  for (const point of scanPath) {
    for (const heading of DEMO_HEADINGS) {
      const detection = heading === point.heading ? detectionByFrameIndex(point.frame_index) : undefined;
      frames.push({
        frame_index: frameIndex,
        latitude: point.latitude,
        longitude: point.longitude,
        heading,
        pitch: 0,
        is_civic_issue: Boolean(detection),
        category: detection?.category ?? null,
        confidence: detection?.confidence ?? null,
        severity: detection?.severity ?? null,
        description: detection?.description ?? null,
        suggestion_id: detection?.suggestionId ?? null,
        frame_image_url: detection?.imageUrl ?? '/demo/audit/clean_01.jpg',
      });
      frameIndex += 1;
    }
  }

  return frames;
}

export function demoSuggestionsForRun(runId: string) {
  return demoAuditSuggestions.filter((suggestion) => suggestion.audit_run_id === runId);
}

export function getDemoFrameDetail(
  runId: string,
  frameIndex: number,
): AuditFrameDetail | null {
  const frame = buildDemoFrames(runId).find((entry) => entry.frame_index === frameIndex);
  const suggestion = demoSuggestionsForRun(runId).find((entry) => entry.frame_index === frameIndex);

  if (!frame) {
    return null;
  }

  return {
    ...frame,
    detection_regions: suggestion?.detection_regions ?? [],
    analysis_result: null,
    scan_source: 'pipeline',
  };
}
