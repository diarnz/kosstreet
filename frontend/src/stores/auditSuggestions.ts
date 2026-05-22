import { defineStore } from 'pinia';
import {
  convertAuditSuggestionToReport,
  getAuditSuggestion,
  listAuditSuggestions,
  reviewAuditSuggestion,
} from '@/api/auditSuggestions';
import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';

interface AuditSuggestionsState {
  suggestionsByRunId: Record<string, AuditSuggestion[]>;
  suggestionDetailsById: Record<string, AuditSuggestion>;
  loadingByRunId: Record<string, boolean>;
  errorByRunId: Record<string, string | null>;
  detailLoadingById: Record<string, boolean>;
  detailErrorById: Record<string, string | null>;
  reviewLoadingById: Record<string, boolean>;
  reviewErrorById: Record<string, string | null>;
  convertLoadingById: Record<string, boolean>;
  convertErrorById: Record<string, string | null>;
  convertedReportBySuggestionId: Record<string, string>;
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}

export const useAuditSuggestionsStore = defineStore('auditSuggestions', {
  state: (): AuditSuggestionsState => ({
    suggestionsByRunId: {},
    suggestionDetailsById: {},
    loadingByRunId: {},
    errorByRunId: {},
    detailLoadingById: {},
    detailErrorById: {},
    reviewLoadingById: {},
    reviewErrorById: {},
    convertLoadingById: {},
    convertErrorById: {},
    convertedReportBySuggestionId: {},
  }),
  getters: {
    suggestionsForRun:
      (state) =>
      (runId: string | null): AuditSuggestion[] =>
        runId ? state.suggestionsByRunId[runId] ?? [] : [],
    isLoadingForRun:
      (state) =>
      (runId: string | null): boolean =>
        runId ? state.loadingByRunId[runId] ?? false : false,
    errorForRun:
      (state) =>
      (runId: string | null): string | null =>
        runId ? state.errorByRunId[runId] ?? null : null,
  },
  actions: {
    mergeSuggestion(suggestion: AuditSuggestion) {
      this.suggestionDetailsById[suggestion.id] = suggestion;
      const runSuggestions = this.suggestionsByRunId[suggestion.audit_run_id] ?? [];
      const existingIndex = runSuggestions.findIndex((item) => item.id === suggestion.id);

      if (existingIndex >= 0) {
        runSuggestions[existingIndex] = suggestion;
      } else {
        runSuggestions.push(suggestion);
      }

      this.suggestionsByRunId[suggestion.audit_run_id] = [...runSuggestions].sort((a, b) =>
        a.created_at.localeCompare(b.created_at),
      );
    },
    async fetchForRun(runId: string): Promise<AuditSuggestion[]> {
      this.loadingByRunId[runId] = true;
      this.errorByRunId[runId] = null;

      try {
        const suggestions = await listAuditSuggestions(runId);
        this.suggestionsByRunId[runId] = suggestions;
        for (const suggestion of suggestions) {
          this.suggestionDetailsById[suggestion.id] = suggestion;
        }
        return suggestions;
      } catch (error) {
        this.errorByRunId[runId] = getErrorMessage(
          error,
          'Could not load AI suggestions for this audit run.',
        );
        return [];
      } finally {
        this.loadingByRunId[runId] = false;
      }
    },
    async fetchSuggestion(suggestionId: string): Promise<AuditSuggestion | null> {
      this.detailLoadingById[suggestionId] = true;
      this.detailErrorById[suggestionId] = null;

      try {
        const suggestion = await getAuditSuggestion(suggestionId);
        this.mergeSuggestion(suggestion);
        return suggestion;
      } catch (error) {
        this.detailErrorById[suggestionId] = getErrorMessage(
          error,
          'Could not load the selected AI suggestion.',
        );
        return null;
      } finally {
        this.detailLoadingById[suggestionId] = false;
      }
    },
    async reviewSuggestion(
      suggestionId: string,
      payload: AuditSuggestionReviewPayload,
    ): Promise<AuditSuggestion | null> {
      this.reviewLoadingById[suggestionId] = true;
      this.reviewErrorById[suggestionId] = null;

      try {
        const suggestion = await reviewAuditSuggestion(suggestionId, payload);
        this.mergeSuggestion(suggestion);
        return suggestion;
      } catch (error) {
        this.reviewErrorById[suggestionId] = getErrorMessage(
          error,
          'Could not persist the review decision.',
        );
        return null;
      } finally {
        this.reviewLoadingById[suggestionId] = false;
      }
    },
    async convertSuggestionToReport(suggestionId: string): Promise<string | null> {
      this.convertLoadingById[suggestionId] = true;
      this.convertErrorById[suggestionId] = null;

      try {
        const result = await convertAuditSuggestionToReport(suggestionId);
        this.convertedReportBySuggestionId[suggestionId] = result.report_id;
        const suggestion = this.suggestionDetailsById[suggestionId];
        if (suggestion) {
          this.mergeSuggestion({
            ...suggestion,
            status: 'converted_to_report',
            converted_report_id: result.report_id,
          });
        }
        return result.report_id;
      } catch (error) {
        this.convertErrorById[suggestionId] = getErrorMessage(
          error,
          'Could not convert the AI suggestion into a report.',
        );
        return null;
      } finally {
        this.convertLoadingById[suggestionId] = false;
      }
    },
  },
});
