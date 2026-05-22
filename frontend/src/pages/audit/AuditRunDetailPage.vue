<template>
  <DashboardLayout>
    <AppSectionHeader
      eyebrow="Audit Run Detail"
      title="Audit run lookup"
      description="Direct run URLs are resolved through the backend audit-run detail and suggestion endpoints."
    />

    <AppCard v-if="error" class="stack" variant="inset">
      <AppBadge tone="danger">Backend error</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" @click="loadRun">Retry fetch</AppButton>
    </AppCard>

    <p v-else-if="isLoading" class="muted">Loading audit run from backend...</p>

    <AuditRunDetailPanel
      v-else-if="run"
      :convert-error-by-id="auditSuggestionsStore.convertErrorById"
      :convert-loading-by-id="auditSuggestionsStore.convertLoadingById"
      :converted-report-by-suggestion-id="auditSuggestionsStore.convertedReportBySuggestionId"
      :review-error-by-id="auditSuggestionsStore.reviewErrorById"
      :review-loading-by-id="auditSuggestionsStore.reviewLoadingById"
      :run="run"
      :suggestions="suggestions"
      :suggestions-error="suggestionsError"
      :suggestions-loading="suggestionsLoading"
      @convert-suggestion="auditSuggestionsStore.convertSuggestionToReport"
      @refresh-suggestions="refreshSuggestions"
      @review-suggestion="auditSuggestionsStore.reviewSuggestion"
    />

    <AppEmptyState
      v-else
      tone="audit"
      title="Run not found"
      description="The backend did not return an audit run for this URL."
    />
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getAuditRun } from '@/api/auditRuns';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AuditRunDetailPanel from '@/components/audit/AuditRunDetailPanel.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useAuditSuggestionsStore } from '@/stores/auditSuggestions';
import { useAuditFramesStore } from '@/stores/auditFrames';
import type { AuditRunSummary } from '@/types/audit';

const route = useRoute();
const auditSuggestionsStore = useAuditSuggestionsStore();
const auditFramesStore = useAuditFramesStore();

const runId = computed(() => String(route.params.runId));
const run = ref<AuditRunSummary | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

const suggestions = computed(() => auditSuggestionsStore.suggestionsForRun(runId.value));
const suggestionsLoading = computed(() => auditSuggestionsStore.isLoadingForRun(runId.value));
const suggestionsError = computed(() => auditSuggestionsStore.errorForRun(runId.value));

async function loadRun() {
  isLoading.value = true;
  error.value = null;

  try {
    run.value = await getAuditRun(runId.value);
    await Promise.all([
      auditSuggestionsStore.fetchForRun(runId.value),
      auditFramesStore.fetchForRun(runId.value),
    ]);
  } catch (loadError) {
    error.value = loadError instanceof Error ? loadError.message : 'Could not load audit run.';
    run.value = null;
  } finally {
    isLoading.value = false;
  }
}

function refreshSuggestions() {
  void auditSuggestionsStore.fetchForRun(runId.value);
}

onMounted(() => {
  void loadRun();
});

watch(runId, () => {
  void loadRun();
});
</script>

<style scoped>
p {
  color: var(--text-secondary);
}
</style>
