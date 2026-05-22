<template>
  <DashboardLayout>
    <div class="cluster-between">
      <AppSectionHeader
        eyebrow="AI Street Audit"
        title="Review proactive street-audit runs"
        description="Create backend audit runs, monitor AI pipeline handoff status, and prepare real model suggestions for human municipal review."
      />
      <div class="audit-actions">
        <AppBadge tone="source-ai-audit">PaliGemma/Gemma pipeline</AppBadge>
        <AppBadge tone="neutral">Human reviewed</AppBadge>
        <AppBadge v-if="auditRunsStore.lastFetchedAt" tone="info">
          Fetched {{ formatAuditDateTime(auditRunsStore.lastFetchedAt) }}
        </AppBadge>
        <AppButton :disabled="auditRunsStore.isLoading" variant="secondary" @click="auditRunsStore.fetchRuns">
          {{ auditRunsStore.isLoading ? 'Refreshing...' : 'Refresh runs' }}
        </AppButton>
      </div>
    </div>

    <PitchModeBanner
      v-if="auditRunsStore.usingDemoRuns"
      data-mode="demo"
      message="Prepared demo audit runs are shown because live backend audit data is empty or unavailable."
    />

    <AppCard v-if="auditRunsStore.error" class="audit-error" variant="inset">
      <AppBadge tone="danger">Backend error</AppBadge>
      <p>{{ auditRunsStore.error }}</p>
      <AppButton variant="secondary" @click="auditRunsStore.fetchRuns">Retry fetch</AppButton>
    </AppCard>

    <section class="audit-command-grid">
      <AuditRunForm
        :error="auditRunsStore.createError"
        :is-creating="auditRunsStore.isCreating"
        @create="auditRunsStore.createRun"
      />

      <AppCard class="stack audit-principles" variant="inset">
        <div>
          <p class="eyebrow">Review philosophy</p>
          <h2>AI suggests. Municipality verifies.</h2>
        </div>
        <p>
          KoStreet does not turn model output into tickets automatically. The backend and AI pipeline
          produce candidates; municipal users review evidence before conversion.
        </p>
        <div class="audit-principles__grid">
          <span v-for="principle in principles" :key="principle">{{ principle }}</span>
        </div>
      </AppCard>
    </section>

    <AuditRunMetrics :metrics="auditRunsStore.metrics" />

    <AuditRunFilters
      :filters="auditRunsStore.filters"
      @clear="auditRunsStore.clearFilters"
      @update:search="auditRunsStore.setSearch"
      @update:status="auditRunsStore.setStatus"
    />

    <section class="audit-workspace">
      <AuditRunQueue
        :is-demo-data="auditRunsStore.usingDemoRuns"
        :is-loading="auditRunsStore.isLoading"
        :runs="auditRunsStore.filteredRuns"
        :selected-run-id="auditRunsStore.selectedRunId"
        @select="auditRunsStore.selectRun"
      />

      <AuditRunDetailPanel
        :convert-error-by-id="auditSuggestionsStore.convertErrorById"
        :convert-loading-by-id="auditSuggestionsStore.convertLoadingById"
        :converted-report-by-suggestion-id="auditSuggestionsStore.convertedReportBySuggestionId"
        :is-demo-data="auditRunsStore.usingDemoRuns"
        :review-error-by-id="auditSuggestionsStore.reviewErrorById"
        :review-loading-by-id="auditSuggestionsStore.reviewLoadingById"
        :run="auditRunsStore.selectedRun"
        :suggestions="selectedRunSuggestions"
        :suggestions-error="selectedRunSuggestionsError"
        :suggestions-loading="selectedRunSuggestionsLoading"
        @convert-suggestion="auditSuggestionsStore.convertSuggestionToReport"
        @refresh-suggestions="refreshSelectedRunSuggestions"
        @review-suggestion="auditSuggestionsStore.reviewSuggestion"
      />
    </section>

    <DemoAuditSuggestionPanel
      v-if="uiStore.demoMode"
      :suggestions="demoAuditSuggestions"
    />
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import PitchModeBanner from '@/components/common/PitchModeBanner.vue';
import DemoAuditSuggestionPanel from '@/components/audit/DemoAuditSuggestionPanel.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AuditRunDetailPanel from '@/components/audit/AuditRunDetailPanel.vue';
import AuditRunFilters from '@/components/audit/AuditRunFilters.vue';
import AuditRunForm from '@/components/audit/AuditRunForm.vue';
import AuditRunMetrics from '@/components/audit/AuditRunMetrics.vue';
import AuditRunQueue from '@/components/audit/AuditRunQueue.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { demoAuditSuggestions } from '@/demo/demoAuditSuggestions';
import { useAuditRunsStore } from '@/stores/auditRuns';
import { useAuditSuggestionsStore } from '@/stores/auditSuggestions';
import { useUiStore } from '@/stores/ui';
import { formatAuditDateTime } from '@/utils/auditFormatting';

const auditRunsStore = useAuditRunsStore();
const auditSuggestionsStore = useAuditSuggestionsStore();
const uiStore = useUiStore();

const principles = ['Suggested, not automatic', 'Confidence shown when returned', 'Human verified', 'Ticket-ready after backend conversion'];
let pollingTimer: number | undefined;

const selectedRunSuggestions = computed(() =>
  auditSuggestionsStore.suggestionsForRun(auditRunsStore.selectedRunId),
);
const selectedRunSuggestionsLoading = computed(() =>
  auditSuggestionsStore.isLoadingForRun(auditRunsStore.selectedRunId),
);
const selectedRunSuggestionsError = computed(() =>
  auditSuggestionsStore.errorForRun(auditRunsStore.selectedRunId),
);

onMounted(() => {
  void auditRunsStore.fetchRuns();
  pollingTimer = window.setInterval(() => {
    const selectedRun = auditRunsStore.selectedRun;
    if (!selectedRun || auditRunsStore.usingDemoRuns) {
      return;
    }

    if (selectedRun.status === 'queued' || selectedRun.status === 'running') {
      void auditRunsStore.fetchRuns();
      void auditSuggestionsStore.fetchForRun(selectedRun.id);
    }
  }, 8000);
});

onUnmounted(() => {
  if (pollingTimer !== undefined) {
    window.clearInterval(pollingTimer);
  }
});

watch(
  () => auditRunsStore.filteredRuns,
  (runs) => {
    if (!runs.some((run) => run.id === auditRunsStore.selectedRunId)) {
      auditRunsStore.selectRun(runs[0]?.id ?? null);
    }
  },
  { immediate: true },
);

watch(
  () => auditRunsStore.selectedRunId,
  (runId) => {
    if (runId && !auditRunsStore.usingDemoRuns) {
      void auditSuggestionsStore.fetchForRun(runId);
    }
  },
);

function refreshSelectedRunSuggestions() {
  if (auditRunsStore.selectedRunId) {
    void auditSuggestionsStore.fetchForRun(auditRunsStore.selectedRunId);
  }
}
</script>

<style scoped>
.audit-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  justify-content: flex-end;
}

.audit-error {
  display: grid;
  gap: var(--space-3);
}

.audit-error p,
p {
  color: var(--text-secondary);
}

.audit-command-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(18rem, 0.72fr);
  gap: var(--space-5);
  align-items: stretch;
}

.audit-principles h2,
.audit-principles p {
  margin: 0;
}

.audit-principles__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-2);
}

.audit-principles__grid span {
  padding: var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.55);
  font-size: var(--text-sm);
  font-weight: 800;
}

.audit-workspace {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(22rem, 1.05fr);
  gap: var(--space-5);
  align-items: start;
}

@media (max-width: 980px) {
  .audit-command-grid,
  .audit-workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .audit-principles__grid {
    grid-template-columns: 1fr;
  }
}
</style>
