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

export interface ReportSummary {
  id: string;
  category: IssueCategory;
  status: TicketStatus;
  latitude: number;
  longitude: number;
  source: ReportSource;
  description?: string | null;
  confidence?: number;
  created_at: string;
}

export interface ReportCreatePayload {
  category: IssueCategory;
  latitude: number;
  longitude: number;
  source: 'citizen';
  description?: string;
  confidence?: number;
}
