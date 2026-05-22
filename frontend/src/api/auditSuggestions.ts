import type {
  AuditSuggestion,
  AuditSuggestionConversionResult,
  AuditSuggestionReviewPayload,
} from '@/types/detection';
import { apiGet, apiPatch, apiPost } from './client';

export type ListAuditSuggestions = (runId: string) => Promise<AuditSuggestion[]>;
export type ReviewAuditSuggestion = (
  suggestionId: string,
  payload: AuditSuggestionReviewPayload,
) => Promise<AuditSuggestion>;
export type ConvertAuditSuggestionToReport = (
  suggestionId: string,
) => Promise<AuditSuggestionConversionResult>;

export const auditSuggestionEndpoints = {
  list: '/api/v1/audit-runs/:runId/suggestions',
  detail: '/api/v1/audit-suggestions/:id',
  review: '/api/v1/audit-suggestions/:id',
  convertToReport: '/api/v1/audit-suggestions/:id/convert-to-report',
} as const;

export function listAuditSuggestions(runId: string): Promise<AuditSuggestion[]> {
  return apiGet<AuditSuggestion[]>(`/api/v1/audit-runs/${encodeURIComponent(runId)}/suggestions`);
}

export function getAuditSuggestion(suggestionId: string): Promise<AuditSuggestion> {
  return apiGet<AuditSuggestion>(`/api/v1/audit-suggestions/${encodeURIComponent(suggestionId)}`);
}

export function reviewAuditSuggestion(
  suggestionId: string,
  payload: AuditSuggestionReviewPayload,
): Promise<AuditSuggestion> {
  return apiPatch<AuditSuggestion, AuditSuggestionReviewPayload>(
    `/api/v1/audit-suggestions/${encodeURIComponent(suggestionId)}`,
    payload,
  );
}

export function convertAuditSuggestionToReport(
  suggestionId: string,
): Promise<AuditSuggestionConversionResult> {
  return apiPost<AuditSuggestionConversionResult, Record<string, never>>(
    `/api/v1/audit-suggestions/${encodeURIComponent(suggestionId)}/convert-to-report`,
    {},
  );
}
