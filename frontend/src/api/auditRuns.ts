import { apiGet, apiPost } from './client';
import type { AuditRunCreatePayload, AuditRunSummary } from '@/types/audit';

export function listAuditRuns(): Promise<AuditRunSummary[]> {
  return apiGet<AuditRunSummary[]>('/api/v1/audit-runs');
}

export function createAuditRun(payload: AuditRunCreatePayload): Promise<AuditRunSummary> {
  return apiPost<AuditRunSummary, AuditRunCreatePayload>('/api/v1/audit-runs', payload);
}
