import { adminRequest, clearStoredAdminKey, getStoredAdminKey, setStoredAdminKey } from '@/api/adminClient';
import type {
  IssueCategory,
  ReportCreatePayload,
  ReportDetail,
  ReportSource,
  ReportSummary,
  TicketStatus,
} from '@/types/report';

export { clearStoredAdminKey, getStoredAdminKey, setStoredAdminKey };

export interface ReportAdminUpdatePayload {
  category?: IssueCategory;
  status?: TicketStatus;
  latitude?: number;
  longitude?: number;
  source?: ReportSource;
  description?: string | null;
  confidence?: number | null;
  is_visible?: boolean;
}

export function adminListReports(adminKey: string): Promise<ReportSummary[]> {
  return adminRequest<ReportSummary[]>('/api/v1/admin/reports', adminKey);
}

export function adminCreateReport(
  adminKey: string,
  payload: ReportCreatePayload,
): Promise<ReportSummary> {
  return adminRequest<ReportSummary>('/api/v1/admin/reports', adminKey, {
    method: 'POST',
    body: payload,
  });
}

export function adminGetReport(adminKey: string, reportId: string): Promise<ReportDetail> {
  return adminRequest<ReportDetail>(
    `/api/v1/admin/reports/${encodeURIComponent(reportId)}`,
    adminKey,
  );
}

export function adminUpdateReport(
  adminKey: string,
  reportId: string,
  payload: ReportAdminUpdatePayload,
): Promise<ReportDetail> {
  return adminRequest<ReportDetail>(
    `/api/v1/admin/reports/${encodeURIComponent(reportId)}`,
    adminKey,
    { method: 'PATCH', body: payload },
  );
}

export function adminDeleteReport(adminKey: string, reportId: string): Promise<void> {
  return adminRequest<void>(
    `/api/v1/admin/reports/${encodeURIComponent(reportId)}`,
    adminKey,
    { method: 'DELETE' },
  );
}
