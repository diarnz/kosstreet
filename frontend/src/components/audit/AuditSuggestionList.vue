<template>
  <AppCard class="audit-suggestion-list stack" variant="inset">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">AI suggestion review</p>
        <h3>Model-produced detections</h3>
      </div>
      <div class="cluster">
        <AppBadge tone="source-ai-audit">{{ suggestions.length }} suggestions</AppBadge>
        <AppButton :disabled="isLoading" size="sm" type="button" variant="secondary" @click="$emit('refresh')">
          {{ isLoading ? 'Refreshing...' : 'Refresh' }}
        </AppButton>
      </div>
    </div>

    <p>
      Suggestions below are persisted backend records from the AI street-audit pipeline. Municipal
      decisions are saved back to the backend before any conversion into dashboard reports.
    </p>

    <AppCard v-if="error" class="audit-suggestion-list__error" variant="inset">
      <AppBadge tone="danger">Suggestion fetch failed</AppBadge>
      <p>{{ error }}</p>
      <AppButton size="sm" type="button" variant="secondary" @click="$emit('refresh')">Retry</AppButton>
    </AppCard>

    <AppEmptyState
      v-else-if="!isLoading && suggestions.length === 0"
      action-label="Refresh suggestions"
      description="The backend returned no suggestions for this run. This can happen when no frame clears the confidence threshold or all external frame/model calls fail."
      title="No AI suggestions returned"
      tone="audit"
      @action="$emit('refresh')"
    />

    <p v-else-if="isLoading" class="muted">Loading AI suggestions from the backend...</p>

    <div v-else class="audit-suggestion-list__grid">
      <AuditSuggestionCard
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        :convert-error="convertErrorById[suggestion.id] ?? null"
        :converted-report-id="convertedReportBySuggestionId[suggestion.id] ?? null"
        :is-converting="convertLoadingById[suggestion.id] ?? false"
        :is-reviewing="reviewLoadingById[suggestion.id] ?? false"
        :review-error="reviewErrorById[suggestion.id] ?? null"
        :suggestion="suggestion"
        @convert="$emit('convert', $event)"
        @review="(suggestionId, payload) => $emit('review', suggestionId, payload)"
      />
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AuditSuggestionCard from '@/components/audit/AuditSuggestionCard.vue';
import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';

defineProps<{
  suggestions: AuditSuggestion[];
  isLoading: boolean;
  error: string | null;
  reviewLoadingById: Record<string, boolean>;
  reviewErrorById: Record<string, string | null>;
  convertLoadingById: Record<string, boolean>;
  convertErrorById: Record<string, string | null>;
  convertedReportBySuggestionId: Record<string, string>;
}>();

defineEmits<{
  refresh: [];
  review: [suggestionId: string, payload: AuditSuggestionReviewPayload];
  convert: [suggestionId: string];
}>();
</script>

<style scoped>
.audit-suggestion-list h3,
.audit-suggestion-list p {
  margin: 0;
}

.audit-suggestion-list p {
  color: var(--text-secondary);
}

.audit-suggestion-list__error {
  display: grid;
  gap: var(--space-3);
}

.audit-suggestion-list__grid {
  display: grid;
  gap: var(--space-4);
}
</style>
