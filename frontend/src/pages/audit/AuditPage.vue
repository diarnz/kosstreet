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
        :is-loading="auditRunsStore.isLoading"
        :runs="auditRunsStore.filteredRuns"
        :selected-run-id="auditRunsStore.selectedRunId"
        @select="auditRunsStore.selectRun"
      />

      <AuditRunDetailPanel :run="auditRunsStore.selectedRun" />
    </section>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AuditRunDetailPanel from '@/components/audit/AuditRunDetailPanel.vue';
import AuditRunFilters from '@/components/audit/AuditRunFilters.vue';
import AuditRunForm from '@/components/audit/AuditRunForm.vue';
import AuditRunMetrics from '@/components/audit/AuditRunMetrics.vue';
import AuditRunQueue from '@/components/audit/AuditRunQueue.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useAuditRunsStore } from '@/stores/auditRuns';
import { formatAuditDateTime } from '@/utils/auditFormatting';

const auditRunsStore = useAuditRunsStore();

const principles = ['Suggested, not automatic', 'Confidence shown when returned', 'Human verified', 'Ticket-ready after backend conversion'];

onMounted(() => {
  void auditRunsStore.fetchRuns();
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
