import { apiGet } from './client';
import type { ReportSummary } from '@/types/report';

export function listReports(): Promise<ReportSummary[]> {
  return apiGet<ReportSummary[]>('/api/v1/reports');
}

