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

export interface ReportSummary {
  id: string;
  category: IssueCategory;
  status: TicketStatus;
  latitude: number;
  longitude: number;
  source: 'citizen' | 'street_audit';
  confidence?: number;
  created_at: string;
}

