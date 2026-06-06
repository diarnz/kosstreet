export type IssueCategory =
  | 'pothole'
  | 'garbage'
  | 'broken_streetlight'
  | 'blocked_sidewalk'
  | 'damaged_sign'
  | 'other';

export type TicketStatus =
  | 'new'
  | 'verified'
  | 'assigned'
  | 'in_progress'
  | 'resolved'
  | 'rejected';

export type ReportSource = 'citizen' | 'street_audit';

export type ReportSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface ReportDetectionRegion {
  center_x: number;
  center_y: number;
  radius: number;
}

export interface ReportImageAnalysis {
  category?: IssueCategory | null;
  confidence?: number | null;
  severity?: ReportSeverity | null;
  description?: string | null;
  is_civic_issue?: boolean;
  regions: ReportDetectionRegion[];
}

export interface ReportSummary {
  id: string;
  category: IssueCategory;
  status: TicketStatus;
  latitude: number;
  longitude: number;
  source: ReportSource;
  description?: string | null;
  confidence?: number;
  is_visible?: boolean;
  image_url?: string | null;
  severity?: ReportSeverity | null;
  detection_regions?: ReportDetectionRegion[];
  created_at: string;
}

export interface ReportWorkflowEvent {
  id: string;
  report_id: string;
  from_status?: TicketStatus | null;
  to_status: TicketStatus;
  note?: string | null;
  created_at: string;
  actor_type: 'municipality' | 'system';
  actor_label: string;
}

export interface ReportDetail extends ReportSummary {
  updated_at: string;
  resolution_note?: string | null;
  rejection_reason?: string | null;
  workflow_events: ReportWorkflowEvent[];
}

export interface ReportCreatePayload {
  category: IssueCategory;
  latitude: number;
  longitude: number;
  source: 'citizen';
  description?: string;
  confidence?: number;
  severity?: ReportSeverity | null;
  detection_regions?: ReportDetectionRegion[];
}

export interface ReportStatusUpdatePayload {
  status: TicketStatus;
  note?: string | null;
}
