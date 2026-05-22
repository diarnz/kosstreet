import { defineStore } from 'pinia';
import { createAuditRun, listAuditRuns } from '@/api/auditRuns';
import { demoAuditRuns } from '@/demo/demoAuditRuns';
import { useUiStore } from '@/stores/ui';
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
    usingDemoRuns(state): boolean {
      const uiStore = useUiStore();
      return uiStore.demoMode && (state.runs.length === 0 || Boolean(state.error));
    },
    dataMode(): 'live' | 'demo' {
      return this.usingDemoRuns ? 'demo' : 'live';
    },
    visibleRuns(state): AuditRunSummary[] {
      return this.usingDemoRuns ? demoAuditRuns : state.runs;
    },
    filteredRuns(state): AuditRunSummary[] {
      const search = state.filters.search.trim().toLowerCase();

      return this.visibleRuns.filter((run) => {
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

      return this.visibleRuns.find((run) => run.id === state.selectedRunId) ?? null;
    },
    metrics(): AuditRunMetrics {
      return {
        total: this.visibleRuns.length,
        queued: this.visibleRuns.filter((run) => run.status === 'queued').length,
        running: this.visibleRuns.filter((run) => run.status === 'running').length,
        completed: this.visibleRuns.filter((run) => run.status === 'completed').length,
        failed: this.visibleRuns.filter((run) => run.status === 'failed').length,
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
