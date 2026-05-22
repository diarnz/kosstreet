import type { IssueCategory, ReportSource, TicketStatus } from './report';

export interface DashboardFiltersState {
  search: string;
  status: TicketStatus | 'all';
  category: IssueCategory | 'all';
  source: ReportSource | 'all';
}

export interface DashboardMetrics {
  total: number;
  new: number;
  inProgress: number;
  resolved: number;
  citizen: number;
  streetAudit: number;
}

