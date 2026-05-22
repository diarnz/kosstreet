<template>
  <AppCard class="audit-run-detail stack" variant="command">
    <template v-if="run">
      <div class="cluster-between">
        <div>
          <p class="eyebrow">Selected audit run</p>
          <h2>{{ run.route_name }}</h2>
        </div>
        <div class="cluster">
          <AuditRunStatusPill :status="run.status" />
          <AppBadge v-if="isDemoData" tone="warning">Demo run</AppBadge>
        </div>
      </div>

      <dl class="audit-run-detail__grid">
        <div>
          <dt>Run ID</dt>
          <dd>{{ run.id }}</dd>
        </div>
        <div>
          <dt>Municipality</dt>
          <dd>{{ run.municipality }}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{{ formatAuditDateTime(run.created_at) }}</dd>
        </div>
        <div>
          <dt>Status meaning</dt>
          <dd>{{ auditRunStatusDescriptions[run.status] }}</dd>
        </div>
        <div>
          <dt>Pipeline progress</dt>
          <dd>{{ run.frames_done }} / {{ run.frames_total }} frames</dd>
        </div>
        <div class="audit-run-detail__wide">
          <dt>Notes</dt>
          <dd>{{ run.notes || 'No notes provided.' }}</dd>
        </div>
      </dl>

      <AppCard variant="inset" class="stack">
        <div class="cluster">
          <AppBadge tone="source-ai-audit">Pipeline handoff</AppBadge>
          <AppBadge tone="neutral">Human-in-the-loop</AppBadge>
        </div>
        <p>
          {{
            isDemoData
              ? 'This is a prepared Pitch Mode audit run. It demonstrates the review workflow without claiming live scanning.'
              : 'This run is a real backend record. Backend and AI services own Street View or approved imagery retrieval, PaliGemma/Gemma analysis, confidence scoring, deduplication, and status progression.'
          }}
        </p>
      </AppCard>

      <AuditSuggestionList
        v-if="!isDemoData"
        :convert-error-by-id="convertErrorById"
        :convert-loading-by-id="convertLoadingById"
        :converted-report-by-suggestion-id="convertedReportBySuggestionId"
        :error="suggestionsError"
        :is-loading="suggestionsLoading"
        :review-error-by-id="reviewErrorById"
        :review-loading-by-id="reviewLoadingById"
        :suggestions="suggestions"
        @convert="$emit('convertSuggestion', $event)"
        @refresh="$emit('refreshSuggestions')"
        @review="(suggestionId, payload) => $emit('reviewSuggestion', suggestionId, payload)"
      />

      <AppEmptyState
        v-else
        tone="audit"
        title="Demo run selected"
        description="Pitch Mode demo suggestions are shown in the separate demo panel. Live suggestion review is only available for backend audit runs."
      />
    </template>

    <AppEmptyState
      v-else
      tone="audit"
      title="Select an audit run"
      description="Choose a run from the queue to inspect backend status and AI review readiness."
    />
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import type { AuditRunSummary } from '@/types/audit';
import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';
import { auditRunStatusDescriptions, formatAuditDateTime } from '@/utils/auditFormatting';
import AuditSuggestionList from './AuditSuggestionList.vue';
import AuditRunStatusPill from './AuditRunStatusPill.vue';

withDefaults(
  defineProps<{
    run: AuditRunSummary | null;
    isDemoData?: boolean;
    suggestions?: AuditSuggestion[];
    suggestionsLoading?: boolean;
    suggestionsError?: string | null;
    reviewLoadingById?: Record<string, boolean>;
    reviewErrorById?: Record<string, string | null>;
    convertLoadingById?: Record<string, boolean>;
    convertErrorById?: Record<string, string | null>;
    convertedReportBySuggestionId?: Record<string, string>;
  }>(),
  {
    isDemoData: false,
    suggestions: () => [],
    suggestionsLoading: false,
    suggestionsError: null,
    reviewLoadingById: () => ({}),
    reviewErrorById: () => ({}),
    convertLoadingById: () => ({}),
    convertErrorById: () => ({}),
    convertedReportBySuggestionId: () => ({}),
  },
);

defineEmits<{
  refreshSuggestions: [];
  reviewSuggestion: [suggestionId: string, payload: AuditSuggestionReviewPayload];
  convertSuggestion: [suggestionId: string];
}>();
</script>

<style scoped>
.audit-run-detail h2 {
  margin: 0;
  font-size: clamp(1.6rem, 4vw, 2.4rem);
}

.audit-run-detail p {
  color: var(--text-secondary);
}

.audit-run-detail__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin: 0;
}

.audit-run-detail__grid > div {
  display: grid;
  gap: var(--space-2);
  min-width: 0;
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  background: rgba(255, 253, 247, 0.58);
}

.audit-run-detail__wide {
  grid-column: 1 / -1;
}

dt {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

dd {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--text-primary);
  font-weight: 750;
}

@media (max-width: 620px) {
  .audit-run-detail__grid {
    grid-template-columns: 1fr;
  }
}
</style>
