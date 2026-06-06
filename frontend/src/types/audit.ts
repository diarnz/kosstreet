export type AuditRunStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface AuditRunCreatePayload {
  municipality?: string;
  route_name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  notes?: string | null;
}

export interface AuditRunSummary {
  id: string;
  municipality: string;
  route_name: string;
  scan_latitude?: number | null;
  scan_longitude?: number | null;
  notes?: string | null;
  status: AuditRunStatus;
  frames_total: number;
  frames_done: number;
  is_visible?: boolean;
  created_at: string;
}

export interface AuditRunFiltersState {
  search: string;
  status: AuditRunStatus | 'all';
}

export interface AuditRunMetrics {
  total: number;
  queued: number;
  running: number;
  completed: number;
  failed: number;
}

export interface AuditFrameSummary {
  frame_index: number;
  latitude: number;
  longitude: number;
  heading: number;
  pitch: number;
  is_civic_issue: boolean;
  category?: import('./report').IssueCategory | null;
  confidence?: number | null;
  severity?: import('./detection').AuditSuggestionSeverity | null;
  description?: string | null;
  suggestion_id?: string | null;
  frame_image_url: string;
}

export interface AuditFrameDetail extends AuditFrameSummary {
  detection_regions: import('./detection').DetectionRegion[];
  analysis_result?: Record<string, unknown> | null;
  scan_source?: AuditScanSource;
}

export type AuditScanSource = 'pipeline' | 'on_demand';

export interface OnDemandAnalyzeQuota {
  limit: number;
  used: number;
  remaining: number;
  resets_at: string;
}

export interface AuditScanPoint {
  frame_index: number;
  latitude: number;
  longitude: number;
  heading: number;
  pitch: number;
  is_civic_issue: boolean;
  severity?: import('./detection').AuditSuggestionSeverity | null;
  suggestion_id?: string | null;
  suggestion_status?: import('./detection').AuditSuggestionStatus | null;
  scan_source?: AuditScanSource;
}
