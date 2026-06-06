import { adminRequest } from '@/api/adminClient';
import type { AuditFrameSummary, AuditRunSummary } from '@/types/audit';
import type { AuditSuggestion } from '@/types/detection';

export interface AdminAuditRunSummary extends AuditRunSummary {
  is_visible?: boolean;
  suggestion_count: number;
  civic_frame_count: number;
}

export interface AdminAuditRunContent {
  suggestions: AuditSuggestion[];
  frames: AuditFrameSummary[];
}

export function adminListAuditRuns(adminKey: string): Promise<AdminAuditRunSummary[]> {
  return adminRequest<AdminAuditRunSummary[]>('/api/v1/admin/audit-runs', adminKey);
}

export function adminGetAuditRunContent(
  adminKey: string,
  runId: string,
): Promise<AdminAuditRunContent> {
  return adminRequest<AdminAuditRunContent>(
    `/api/v1/admin/audit-runs/${encodeURIComponent(runId)}/content`,
    adminKey,
  );
}

export function adminUpdateAuditRun(
  adminKey: string,
  runId: string,
  payload: { is_visible?: boolean; notes?: string | null },
): Promise<AuditRunSummary> {
  return adminRequest<AuditRunSummary>(
    `/api/v1/admin/audit-runs/${encodeURIComponent(runId)}`,
    adminKey,
    { method: 'PATCH', body: payload },
  );
}

export function adminDeleteAuditRun(adminKey: string, runId: string): Promise<void> {
  return adminRequest<void>(
    `/api/v1/admin/audit-runs/${encodeURIComponent(runId)}`,
    adminKey,
    { method: 'DELETE' },
  );
}

export function adminUpdateAuditSuggestion(
  adminKey: string,
  suggestionId: string,
  payload: { is_visible?: boolean },
): Promise<AuditSuggestion> {
  return adminRequest<AuditSuggestion>(
    `/api/v1/admin/audit-suggestions/${encodeURIComponent(suggestionId)}`,
    adminKey,
    { method: 'PATCH', body: payload },
  );
}

export function adminDeleteAuditSuggestion(adminKey: string, suggestionId: string): Promise<void> {
  return adminRequest<void>(
    `/api/v1/admin/audit-suggestions/${encodeURIComponent(suggestionId)}`,
    adminKey,
    { method: 'DELETE' },
  );
}
