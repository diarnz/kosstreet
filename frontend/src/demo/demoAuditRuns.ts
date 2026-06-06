import type { AuditRunSummary } from '@/types/audit';
import {
  DEMO_AUDIT_RUN_ID,
  DEMO_AUDIT_RUN_LEGACY_ID,
  DEMO_SCAN_POINT_COUNT,
} from '@/demo/demoAuditConstants';

export const demoAuditRuns: AuditRunSummary[] = [
  {
    id: DEMO_AUDIT_RUN_ID,
    municipality: 'Kosovo',
    route_name: 'Old town corridor demo',
    scan_latitude: 42.2137,
    scan_longitude: 20.7397,
    notes: 'Prepared demo run showing the Street View scanner, severity overlays, and municipal review.',
    status: 'completed',
    frames_total: DEMO_SCAN_POINT_COUNT,
    frames_done: DEMO_SCAN_POINT_COUNT,
    created_at: '2026-05-22T08:40:00.000Z',
  },
  {
    id: DEMO_AUDIT_RUN_LEGACY_ID,
    municipality: 'Kosovo',
    route_name: 'Legacy four-heading corridor (demo)',
    scan_latitude: 42.2137,
    scan_longitude: 20.7397,
    notes: 'Demonstrates the legacy scan fallback banner and All frames filmstrip for older runs.',
    status: 'completed',
    frames_total: 64,
    frames_done: 64,
    created_at: '2026-05-21T16:10:00.000Z',
  },
  {
    id: 'demo-audit-run-002',
    municipality: 'Kosovo',
    route_name: 'Market street demo segment',
    scan_latitude: 42.2089,
    scan_longitude: 20.7421,
    notes: 'Queued demo run for explaining backend orchestration and approved imagery handoff.',
    status: 'queued',
    frames_total: DEMO_SCAN_POINT_COUNT,
    frames_done: 0,
    created_at: '2026-05-22T10:18:00.000Z',
  },
];
