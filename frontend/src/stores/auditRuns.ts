import { defineStore } from 'pinia';
import { createAuditRun, listAuditRuns } from '@/api/auditRuns';
import type {
  AuditRunCreatePayload,
  AuditRunFiltersState,
  AuditRunMetrics,
  AuditRunStatus,
  AuditRunSummary,
} from '@/types/audit';
import { auditRunStatusLabels, formatAuditDateTime } from '@/utils/auditFormatting';

interface AuditRunsState {
  runs: AuditRunSummary[];
  selectedRunId: string | null;
  isLoading: boolean;
  isCreating: boolean;
  error: string | null;
  createError: string | null;
  lastFetchedAt: string | null;
  filters: AuditRunFiltersState;
}

const defaultFilters = (): AuditRunFiltersState => ({
  search: '',
  status: 'all',
});

export const useAuditRunsStore = defineStore('auditRuns', {
  state: (): AuditRunsState => ({
    runs: [],
    selectedRunId: null,
    isLoading: false,
    isCreating: false,
    error: null,
    createError: null,
    lastFetchedAt: null,
    filters: defaultFilters(),
  }),
  getters: {
    filteredRuns(state): AuditRunSummary[] {
      const search = state.filters.search.trim().toLowerCase();

      return state.runs.filter((run) => {
        const matchesStatus = state.filters.status === 'all' || run.status === state.filters.status;
        const searchTarget = [
          run.id,
          run.municipality,
          run.route_name,
          auditRunStatusLabels[run.status],
          formatAuditDateTime(run.created_at),
          run.notes ?? '',
        ]
          .join(' ')
          .toLowerCase();
        const matchesSearch = !search || searchTarget.includes(search);

        return matchesStatus && matchesSearch;
      });
    },
    selectedRun(state): AuditRunSummary | null {
      if (!state.selectedRunId) {
        return null;
      }

      return state.runs.find((run) => run.id === state.selectedRunId) ?? null;
    },
    metrics(state): AuditRunMetrics {
      return {
        total: state.runs.length,
        queued: state.runs.filter((run) => run.status === 'queued').length,
        running: state.runs.filter((run) => run.status === 'running').length,
        completed: state.runs.filter((run) => run.status === 'completed').length,
        failed: state.runs.filter((run) => run.status === 'failed').length,
      };
    },
  },
  actions: {
    async fetchRuns() {
      this.isLoading = true;
      this.error = null;

      try {
        const runs = await listAuditRuns();
        this.runs = runs;
        this.lastFetchedAt = new Date().toISOString();

        if (this.selectedRunId && !runs.some((run) => run.id === this.selectedRunId)) {
          this.selectedRunId = runs[0]?.id ?? null;
        }
      } catch (error) {
        this.error =
          error instanceof Error ? error.message : 'Could not load audit runs. Check the backend and retry.';
      } finally {
        this.isLoading = false;
      }
    },
    async createRun(payload: AuditRunCreatePayload): Promise<AuditRunSummary | null> {
      this.isCreating = true;
      this.createError = null;

      try {
        const run = await createAuditRun(payload);
        this.runs = [run, ...this.runs.filter((existingRun) => existingRun.id !== run.id)];
        this.selectedRunId = run.id;
        return run;
      } catch (error) {
        this.createError =
          error instanceof Error ? error.message : 'Could not create audit run. Check the backend and retry.';
        return null;
      } finally {
        this.isCreating = false;
      }
    },
    selectRun(runId: string | null) {
      this.selectedRunId = runId;
    },
    setSearch(search: string) {
      this.filters.search = search;
    },
    setStatus(status: AuditRunStatus | 'all') {
      this.filters.status = status;
    },
    clearFilters() {
      this.filters = defaultFilters();
    },
  },
});
