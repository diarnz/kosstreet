import type { AuditFrameDetail, AuditFrameSummary, AuditScanPoint, OnDemandAnalyzeQuota } from '@/types/audit';
import type { StreetViewCurrentView } from '@/types/streetView';
import { apiGet, apiPost } from './client';

export interface AnalyzeViewPayload {
  latitude: number;
  longitude: number;
  heading: number;
  pitch?: number;
}

export function analyzeAuditView(runId: string, payload: AnalyzeViewPayload): Promise<AuditFrameDetail> {
  return apiPost<AuditFrameDetail, AnalyzeViewPayload>(
    `/api/v1/audit-runs/${encodeURIComponent(runId)}/analyze-view`,
    payload,
  );
}

export function getOnDemandAnalyzeQuota(runId: string): Promise<OnDemandAnalyzeQuota> {
  return apiGet<OnDemandAnalyzeQuota>(
    `/api/v1/audit-runs/${encodeURIComponent(runId)}/on-demand-quota`,
  );
}

export function listAuditScanPath(runId: string): Promise<AuditScanPoint[]> {
  return apiGet<AuditScanPoint[]>(`/api/v1/audit-runs/${encodeURIComponent(runId)}/scan-path`);
}

export function listAuditFrames(runId: string): Promise<AuditFrameSummary[]> {  return apiGet<AuditFrameSummary[]>(`/api/v1/audit-runs/${encodeURIComponent(runId)}/frames`);
}

export function getAuditFrame(runId: string, frameIndex: number): Promise<AuditFrameDetail> {
  return apiGet<AuditFrameDetail>(
    `/api/v1/audit-runs/${encodeURIComponent(runId)}/frames/${frameIndex}`,
  );
}

export function auditFrameImagePath(runId: string, frameIndex: number): string {
  return `/api/v1/audit-runs/${encodeURIComponent(runId)}/frames/${frameIndex}/image`;
}

export function auditSuggestionFrameImagePath(suggestionId: string): string {
  return `/api/v1/audit-suggestions/${encodeURIComponent(suggestionId)}/frame-image`;
}
