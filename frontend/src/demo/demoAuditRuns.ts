import type { AuditRunSummary } from '@/types/audit';

export const demoAuditRuns: AuditRunSummary[] = [
  {
    id: 'demo-audit-run-001',
    municipality: 'Prishtina',
    route_name: 'Prishtina civic corridor demo',
    notes: 'Prepared demo run showing how proactive street-audit suggestions enter municipal review.',
    status: 'completed',
    created_at: '2026-05-22T08:40:00.000Z',
  },
  {
    id: 'demo-audit-run-002',
    municipality: 'Prishtina',
    route_name: 'Bill Clinton Boulevard demo segment',
    notes: 'Queued demo run for explaining backend orchestration and approved imagery handoff.',
    status: 'queued',
    created_at: '2026-05-22T10:18:00.000Z',
  },
];
