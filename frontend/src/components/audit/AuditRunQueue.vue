<template>
  <AppCard class="audit-run-queue stack" variant="command">
    <div class="cluster-between">
      <div>
        <h2>Audit run queue</h2>
        <p>{{ runs.length }} run{{ runs.length === 1 ? '' : 's' }} in current view.</p>
      </div>
      <AppLoading v-if="isLoading" label="Loading audit runs" tone="audit" />
    </div>

    <AppEmptyState
      v-if="!isLoading && runs.length === 0"
      tone="audit"
      title="No audit runs in this view"
      description="Create a real audit run or clear filters to see available backend runs."
    />

    <div v-else class="audit-run-queue__list" role="list">
      <button
        v-for="run in runs"
        :key="run.id"
        class="audit-run-queue__item"
        :class="{ 'audit-run-queue__item--selected': run.id === selectedRunId }"
        type="button"
        role="listitem"
        @click="$emit('select', run.id)"
      >
        <span class="cluster">
          <AuditRunStatusPill :status="run.status" />
          <AppBadge tone="source-ai-audit" size="sm">AI Street Audit</AppBadge>
        </span>
        <strong>{{ run.route_name }}</strong>
        <span class="audit-run-queue__meta">
          {{ run.municipality }} · {{ formatAuditDateTime(run.created_at) }}
        </span>
        <span v-if="run.notes" class="audit-run-queue__notes">{{ run.notes }}</span>
      </button>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import type { AuditRunSummary } from '@/types/audit';
import { formatAuditDateTime } from '@/utils/auditFormatting';
import AuditRunStatusPill from './AuditRunStatusPill.vue';

defineProps<{
  runs: AuditRunSummary[];
  selectedRunId: string | null;
  isLoading: boolean;
}>();

defineEmits<{
  select: [runId: string];
}>();
</script>

<style scoped>
.audit-run-queue h2 {
  margin: 0 0 var(--space-2);
}

.audit-run-queue p {
  color: var(--text-secondary);
}

.audit-run-queue__list {
  display: grid;
  gap: var(--space-3);
  max-height: 42rem;
  overflow: auto;
  padding-right: var(--space-1);
}

.audit-run-queue__item {
  display: grid;
  gap: var(--space-3);
  width: 100%;
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.68);
  text-align: left;
}

.audit-run-queue__item--selected {
  border-color: var(--source-ai-audit-border);
  background: rgba(232, 226, 212, 0.58);
  box-shadow: var(--shadow-card);
}

.audit-run-queue__meta,
.audit-run-queue__notes {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>
