import type { IssueCategory } from './report';

export type AuditSuggestionStatus =
  | 'pending_review'
  | 'accepted'
  | 'rejected'
  | 'needs_manual_review'
  | 'converted_to_report';

export type AuditSuggestionSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface AuditSuggestion {
  id: string;
  audit_run_id: string;
  category: IssueCategory;
  status: AuditSuggestionStatus;
  latitude: number;
  longitude: number;
  confidence: number;
  severity?: AuditSuggestionSeverity | null;
  description?: string | null;
  model_name?: string | null;
  explanation?: string | null;
  image_url?: string | null;
  image_attribution?: string | null;
  department?: string | null;
  heading?: number | null;
  pitch?: number | null;
  reviewer_note?: string | null;
  converted_report_id?: string | null;
  bounding_box?: BoundingBox | null;
  created_at: string;
}

export interface AuditSuggestionReviewPayload {
  status: 'accepted' | 'rejected' | 'needs_manual_review';
  reviewer_note?: string | null;
}

export interface AuditSuggestionConversionResult {
  report_id: string;
}
