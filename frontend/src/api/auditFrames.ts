import { apiGet } from './client';
import type { AuditFrameDetail, AuditFrameSummary } from '@/types/auditFrame';

export const auditFrameEndpoints = {
  list: '/api/v1/audit-runs/:runId/frames',
  detail: '/api/v1/audit-runs/:runId/frames/:frameIndex',
  image: '/api/v1/audit-runs/:runId/frames/:frameIndex/image',
} as const;

export function listAuditFrames(runId: string): Promise<AuditFrameSummary[]> {
  return apiGet<AuditFrameSummary[]>(
    `/api/v1/audit-runs/${encodeURIComponent(runId)}/frames`,
  );
}

export function getAuditFrame(runId: string, frameIndex: number): Promise<AuditFrameDetail> {
  return apiGet<AuditFrameDetail>(
    `/api/v1/audit-runs/${encodeURIComponent(runId)}/frames/${frameIndex}`,
  );
}
