import { defineStore } from 'pinia';
import { listReports } from '@/api/reports';
import type { DashboardFiltersState, DashboardMetrics } from '@/types/dashboard';
import type { IssueCategory, ReportSource, ReportSummary, TicketStatus } from '@/types/report';
import { getMappableReports, hasValidCoordinates } from '@/utils/map';
import { categoryLabels, formatCoordinates, sourceLabels, statusLabels } from '@/utils/reportFormatting';

interface ReportsState {
  reports: ReportSummary[];
  selectedReportId: string | null;
  isLoading: boolean;
  error: string | null;
  lastFetchedAt: string | null;
  filters: DashboardFiltersState;
}

const defaultFilters = (): DashboardFiltersState => ({
  search: '',
  status: 'all',
  category: 'all',
  source: 'all',
});

export const useReportsStore = defineStore('reports', {
  state: (): ReportsState => ({
    reports: [],
    selectedReportId: null,
    isLoading: false,
    error: null,
    lastFetchedAt: null,
    filters: defaultFilters(),
  }),
  getters: {
    filteredReports(state): ReportSummary[] {
      const search = state.filters.search.trim().toLowerCase();

      return state.reports.filter((report) => {
        const matchesStatus = state.filters.status === 'all' || report.status === state.filters.status;
        const matchesCategory =
          state.filters.category === 'all' || report.category === state.filters.category;
        const matchesSource = state.filters.source === 'all' || report.source === state.filters.source;
        const searchTarget = [
          report.id,
          categoryLabels[report.category],
          statusLabels[report.status],
          sourceLabels[report.source],
          formatCoordinates(report.latitude, report.longitude),
          report.description ?? '',
        ]
          .join(' ')
          .toLowerCase();
        const matchesSearch = !search || searchTarget.includes(search);

        return matchesStatus && matchesCategory && matchesSource && matchesSearch;
      });
    },
    selectedReport(state): ReportSummary | null {
      if (!state.selectedReportId) {
        return null;
      }

      return state.reports.find((report) => report.id === state.selectedReportId) ?? null;
    },
    mappableFilteredReports(): ReportSummary[] {
      return getMappableReports(this.filteredReports);
    },
    hiddenMapReports(): ReportSummary[] {
      return this.filteredReports.filter((report) => !hasValidCoordinates(report));
    },
    selectedMappableReport(): ReportSummary | null {
      if (!this.selectedReport || !hasValidCoordinates(this.selectedReport)) {
        return null;
      }

      return this.selectedReport;
    },
    metrics(state): DashboardMetrics {
      return {
        total: state.reports.length,
        new: state.reports.filter((report) => report.status === 'new').length,
        inProgress: state.reports.filter((report) => report.status === 'in_progress').length,
        resolved: state.reports.filter((report) => report.status === 'resolved').length,
        citizen: state.reports.filter((report) => report.source === 'citizen').length,
        streetAudit: state.reports.filter((report) => report.source === 'street_audit').length,
      };
    },
  },
  actions: {
    async fetchReports() {
      this.isLoading = true;
      this.error = null;

      try {
        const reports = await listReports();
        this.reports = reports;
        this.lastFetchedAt = new Date().toISOString();

        if (this.selectedReportId && !reports.some((report) => report.id === this.selectedReportId)) {
          this.selectedReportId = reports[0]?.id ?? null;
        }
      } catch (error) {
        this.error =
          error instanceof Error ? error.message : 'Could not load reports. Check the backend and retry.';
      } finally {
        this.isLoading = false;
      }
    },
    setReports(reports: ReportSummary[]) {
      this.reports = reports;
    },
    selectReport(reportId: string | null) {
      this.selectedReportId = reportId;
    },
    setSearch(search: string) {
      this.filters.search = search;
    },
    setStatus(status: TicketStatus | 'all') {
      this.filters.status = status;
    },
    setCategory(category: IssueCategory | 'all') {
      this.filters.category = category;
    },
    setSource(source: ReportSource | 'all') {
      this.filters.source = source;
    },
    clearFilters() {
      this.filters = defaultFilters();
    },
  },
});
