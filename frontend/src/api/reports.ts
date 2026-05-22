import { apiGet, apiPost } from './client';
import type { ReportCreatePayload, ReportSummary } from '@/types/report';

export function listReports(): Promise<ReportSummary[]> {
  return apiGet<ReportSummary[]>('/api/v1/reports');
}

export function createReport(payload: ReportCreatePayload): Promise<ReportSummary> {
  return apiPost<ReportSummary, ReportCreatePayload>('/api/v1/reports', payload);
}
