import { defineStore } from 'pinia';
import { getReport, listReports, updateReportStatus } from '@/api/reports';
import { demoReports, findDemoReport } from '@/demo/demoReports';
import { useUiStore } from '@/stores/ui';
import type { DashboardFiltersState, DashboardMetrics } from '@/types/dashboard';
import type {
  IssueCategory,
  ReportDetail,
  ReportSource,
  ReportStatusUpdatePayload,
  ReportSummary,
  TicketStatus,
} from '@/types/report';
import { getMappableReports, hasValidCoordinates } from '@/utils/map';
import { categoryLabels, formatCoordinates, sourceLabels, statusLabels } from '@/utils/reportFormatting';
import { getAllowedNextStatuses } from '@/utils/reportWorkflow';

interface ReportsState {
  reports: ReportSummary[];
  selectedReportId: string | null;
  isLoading: boolean;
  error: string | null;
  lastFetchedAt: string | null;
  filters: DashboardFiltersState;
  reportDetailsById: Record<string, ReportDetail>;
  detailLoadingById: Record<string, boolean>;
  detailErrorById: Record<string, string | null>;
  isUpdatingStatus: boolean;
  statusUpdateError: string | null;
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
    reportDetailsById: {},
    detailLoadingById: {},
    detailErrorById: {},
    isUpdatingStatus: false,
    statusUpdateError: null,
  }),
  getters: {
    usingDemoReports(state): boolean {
      const uiStore = useUiStore();
      return uiStore.demoMode && (state.reports.length === 0 || Boolean(state.error));
    },
    dataMode(): 'live' | 'demo' {
      return this.usingDemoReports ? 'demo' : 'live';
    },
    visibleReports(state): ReportSummary[] {
      return this.usingDemoReports ? demoReports : state.reports;
    },
    filteredReports(state): ReportSummary[] {
      const search = state.filters.search.trim().toLowerCase();

      return this.visibleReports.filter((report) => {
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

      return this.visibleReports.find((report) => report.id === state.selectedReportId) ?? null;
    },
    selectedReportDetail(state): ReportDetail | null {
      if (!state.selectedReportId) {
        return null;
      }

      if (this.usingDemoReports) {
        return findDemoReport(state.selectedReportId);
      }

      return state.reportDetailsById[state.selectedReportId] ?? null;
    },
    selectedDetailIsLoading(state): boolean {
      if (!state.selectedReportId) {
        return false;
      }

      return state.detailLoadingById[state.selectedReportId] ?? false;
    },
    selectedDetailError(state): string | null {
      if (!state.selectedReportId) {
        return null;
      }

      return state.detailErrorById[state.selectedReportId] ?? null;
    },
    allowedNextStatuses(state): TicketStatus[] {
      const selectedReport = state.selectedReportId
        ? this.visibleReports.find((report) => report.id === state.selectedReportId)
        : null;
      const selectedDetail = state.selectedReportId ? state.reportDetailsById[state.selectedReportId] : null;
      const status = selectedDetail?.status ?? selectedReport?.status;

      return status ? getAllowedNextStatuses(status) : [];
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
        total: this.visibleReports.length,
        new: this.visibleReports.filter((report) => report.status === 'new').length,
        inProgress: this.visibleReports.filter((report) => report.status === 'in_progress').length,
        resolved: this.visibleReports.filter((report) => report.status === 'resolved').length,
        citizen: this.visibleReports.filter((report) => report.source === 'citizen').length,
        streetAudit: this.visibleReports.filter((report) => report.source === 'street_audit').length,
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
    mergeReportDetail(detail: ReportDetail) {
      this.reportDetailsById[detail.id] = detail;
      const reportIndex = this.reports.findIndex((report) => report.id === detail.id);

      if (reportIndex >= 0) {
        this.reports[reportIndex] = {
          id: detail.id,
          category: detail.category,
          status: detail.status,
          latitude: detail.latitude,
          longitude: detail.longitude,
          source: detail.source,
          description: detail.description,
          confidence: detail.confidence,
          image_url: detail.image_url,
          severity: detail.severity,
          detection_regions: detail.detection_regions,
          created_at: detail.created_at,
        };
      }
    },
    async fetchReportDetail(reportId: string): Promise<ReportDetail | null> {
      if (this.usingDemoReports) {
        const demoReport = findDemoReport(reportId);
        if (demoReport) {
          this.reportDetailsById[reportId] = demoReport;
          this.detailErrorById[reportId] = null;
          return demoReport;
        }
      }

      this.detailLoadingById[reportId] = true;
      this.detailErrorById[reportId] = null;

      try {
        const detail = await getReport(reportId);
        this.mergeReportDetail(detail);
        return detail;
      } catch (error) {
        this.detailErrorById[reportId] =
          error instanceof Error
            ? error.message
            : 'Could not load report details. Try again.';
        return null;
      } finally {
        this.detailLoadingById[reportId] = false;
      }
    },
    async updateSelectedReportStatus(payload: ReportStatusUpdatePayload): Promise<ReportDetail | null> {
      if (!this.selectedReportId) {
        this.statusUpdateError = 'Select a report before updating workflow status.';
        return null;
      }

      if (this.usingDemoReports) {
        this.statusUpdateError =
          'Pitch Mode demo records do not persist workflow changes. Backend PATCH support is required.';
        return null;
      }

      this.isUpdatingStatus = true;
      this.statusUpdateError = null;

      try {
        const detail = await updateReportStatus(this.selectedReportId, payload);
        this.mergeReportDetail(detail);
        return detail;
      } catch (error) {
        this.statusUpdateError =
          error instanceof Error
            ? error.message
            : 'Could not update status. Try again.';
        return null;
      } finally {
        this.isUpdatingStatus = false;
      }
    },
    selectReport(reportId: string | null) {
      this.selectedReportId = reportId;
      this.statusUpdateError = null;
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
