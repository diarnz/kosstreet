import type {
  AuditSuggestion,
  AuditSuggestionConversionResult,
  AuditSuggestionReviewPayload,
} from '@/types/detection';

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
  review: '/api/v1/audit-suggestions/:id',
  convertToReport: '/api/v1/audit-suggestions/:id/convert-to-report',
} as const;
