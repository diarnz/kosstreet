import type { IssueCategory } from './report';

export interface AiSuggestion {
  category: IssueCategory;
  confidence: number;
  explanation?: string;
}

export interface ReportDraft {
  imageFile: File | null;
  imagePreviewUrl: string | null;
  category: IssueCategory | null;
  latitude: number | null;
  longitude: number | null;
  locationAccuracy: number | null;
  locationLabel: string | null;
  description: string;
  aiSuggestion: AiSuggestion | null;
}

