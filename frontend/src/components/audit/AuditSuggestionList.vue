<template>
  <section class="audit-suggestion-list">
    <header class="audit-suggestion-list__head">
      <div>
        <p class="command-label">AI suggestions</p>
        <h3>{{ suggestions.length }} detections</h3>
      </div>
      <AppButton :disabled="isLoading" size="sm" type="button" variant="secondary" @click="$emit('refresh')">
        {{ isLoading ? 'Syncing…' : 'Refresh' }}
      </AppButton>
    </header>

    <p v-if="error" class="audit-suggestion-list__error">{{ error }}</p>

    <AppEmptyState
      v-else-if="!isLoading && suggestions.length === 0"
      tone="audit"
      title="No suggestions yet"
      description="The AI pipeline has not returned detections for this run."
      action-label="Refresh"
      @action="$emit('refresh')"
    />

    <AppLoading v-else-if="isLoading" label="Loading suggestions" />

    <div v-else class="audit-suggestion-list__grid">
      <div
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="audit-suggestion-list__item"
        :class="{ 'audit-suggestion-list__item--selected': suggestion.id === selectedSuggestionId }"
      >
        <AuditSuggestionCard
          :compact="compactCards"
          :convert-error="convertErrorById[suggestion.id] ?? null"
          :converted-report-id="convertedReportBySuggestionId[suggestion.id] ?? null"
          :is-converting="convertLoadingById[suggestion.id] ?? false"
          :is-reviewing="reviewLoadingById[suggestion.id] ?? false"
          :review-error="reviewErrorById[suggestion.id] ?? null"
          :show-scanner-action="showScannerActions"
          :suggestion="suggestion"
          @convert="$emit('convert', $event)"
          @review="(suggestionId, payload) => $emit('review', suggestionId, payload)"
          @select="$emit('select', $event)"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import AppButton from '@/components/common/AppButton.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
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
  selectedSuggestionId?: string | null;
  showScannerActions?: boolean;
  compactCards?: boolean;
}>();

defineEmits<{
  refresh: [];
  review: [suggestionId: string, payload: AuditSuggestionReviewPayload];
  convert: [suggestionId: string];
  select: [suggestionId: string];
}>();
</script>

<style scoped>
.audit-suggestion-list {
  display: grid;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: 1px solid rgba(23, 33, 26, 0.08);
}

.audit-suggestion-list__head {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: flex-end;
  justify-content: space-between;
}

.audit-suggestion-list h3 {
  margin: 0.15rem 0 0;
  font-size: 1rem;
  font-weight: 850;
}

.audit-suggestion-list__error {
  margin: 0;
  color: var(--color-repair-red);
  font-size: var(--text-sm);
  font-weight: 750;
}

.audit-suggestion-list__grid {
  display: grid;
  gap: var(--space-3);
}

.audit-suggestion-list__item {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-2);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  transition: border-color var(--motion-fast), background var(--motion-fast);
}

.audit-suggestion-list__item--selected {
  border-color: rgba(47, 93, 80, 0.28);
  background: rgba(47, 93, 80, 0.06);
}
</style>
