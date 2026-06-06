import { apiGet, apiPatch } from './client';
import { resolveApiBaseUrl } from '@/utils/apiBaseUrl';
import type {
  ReportCreatePayload,
  ReportDetail,
  ReportImageAnalysis,
  ReportStatusUpdatePayload,
  ReportSummary,
} from '@/types/report';

const API_BASE_URL = resolveApiBaseUrl();

export function listReports(): Promise<ReportSummary[]> {
  return apiGet<ReportSummary[]>('/api/v1/reports');
}

export async function analyzeReportImage(file: File): Promise<ReportImageAnalysis> {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch(`${API_BASE_URL}/api/v1/reports/analyze-image`, {
    method: 'POST',
    body: formData,
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail =
      body && typeof body === 'object' && 'detail' in body && typeof body.detail === 'string'
        ? body.detail
        : `Image analysis failed (${response.status})`;
    throw new Error(detail);
  }

  return body as ReportImageAnalysis;
}

export async function createReport(
  payload: ReportCreatePayload,
  imageFile?: File | null,
): Promise<ReportSummary> {
  if (!imageFile) {
    const response = await fetch(`${API_BASE_URL}/api/v1/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(
        body && typeof body === 'object' && 'detail' in body && typeof body.detail === 'string'
          ? body.detail
          : `Create report failed (${response.status})`,
      );
    }
    return body as ReportSummary;
  }

  const formData = new FormData();
  formData.append('data', JSON.stringify(payload));
  formData.append('image', imageFile);

  const response = await fetch(`${API_BASE_URL}/api/v1/reports`, {
    method: 'POST',
    body: formData,
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      body && typeof body === 'object' && 'detail' in body && typeof body.detail === 'string'
        ? body.detail
        : `Create report failed (${response.status})`,
    );
  }

  return body as ReportSummary;
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
