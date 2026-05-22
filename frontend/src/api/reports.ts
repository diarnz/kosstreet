import { apiGet, apiPatch, apiPost } from './client';
import type {
  ReportCreatePayload,
  ReportDetail,
  ReportStatusUpdatePayload,
  ReportSummary,
} from '@/types/report';

export function listReports(): Promise<ReportSummary[]> {
  return apiGet<ReportSummary[]>('/api/v1/reports');
}

export function createReport(payload: ReportCreatePayload): Promise<ReportSummary> {
  return apiPost<ReportSummary, ReportCreatePayload>('/api/v1/reports', payload);
}

export function getReport(reportId: string): Promise<ReportDetail> {
  return apiGet<ReportDetail>(`/api/v1/reports/${encodeURIComponent(reportId)}`);
}

export function updateReportStatus(
  reportId: string,
  payload: ReportStatusUpdatePayload,
): Promise<ReportDetail> {
  return apiPatch<ReportDetail, ReportStatusUpdatePayload>(
    `/api/v1/reports/${encodeURIComponent(reportId)}/status`,
    payload,
  );
}
