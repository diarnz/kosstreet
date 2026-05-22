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
  notes?: string | null;
  status: AuditRunStatus;
  frames_total: number;
  frames_done: number;
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
