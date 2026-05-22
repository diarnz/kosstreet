import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { IssueCategory } from '@/types/report';

export interface AuditFrameSummary {
  id: string;
  audit_run_id: string;
  frame_index: number;
  latitude: number;
  longitude: number;
  heading: number;
  pitch: number;
  is_civic_issue: boolean;
  category: IssueCategory | null;
  confidence: number | null;
  severity: AuditSuggestionSeverity | null;
  suggestion_id: string | null;
  has_detection_regions: boolean;
  frame_image_url: string;
  created_at: string;
}

export interface AuditFrameDetail extends AuditFrameSummary {
  description: string | null;
  detection_regions: DetectionRegion[] | null;
  model_name: string | null;
}

export type AuditFrameFilterMode = 'all' | 'detections';

export type AuditFrameSeverityFilter = 'all' | AuditSuggestionSeverity;

export type AuditFrameCategoryFilter = 'all' | IssueCategory;
