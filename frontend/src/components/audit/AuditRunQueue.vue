<template>
  <section class="report-queue">
    <div class="report-queue__head">
      <span class="report-queue__count">{{ runs.length }}</span>
    </div>

    <AppLoading v-if="isLoading" label="Loading" />

    <AppEmptyState
      v-else-if="runs.length === 0"
      tone="dashboard"
      title="No audit runs"
      description="Launch a scan to start reviewing AI detections."
    />

    <div v-else class="report-queue__list" role="list">
      <AuditRunQueueExpandCard
        v-for="run in runs"
        :key="run.id"
        :run="run"
        :selected="run.id === selectedRunId"
        :is-demo-data="isDemoData"
        @select="$emit('select', $event)"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import AuditRunQueueExpandCard from '@/components/audit/AuditRunQueueExpandCard.vue';
import type { AuditRunSummary } from '@/types/audit';

defineProps<{
  runs: AuditRunSummary[];
  selectedRunId: string | null;
  isLoading: boolean;
  isDemoData?: boolean;
}>();

defineEmits<{
  select: [runId: string];
}>();
</script>

<style scoped>
.report-queue {
  display: grid;
  gap: var(--space-2);
}

.report-queue__head {
  display: flex;
  justify-content: flex-end;
}

.report-queue__count {
  display: grid;
  place-items: center;
  min-width: 1.75rem;
  height: 1.75rem;
  padding: 0 0.45rem;
  border-radius: var(--radius-pill);
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.1);
  font-size: 0.72rem;
  font-weight: 900;
}

.report-queue__list {
  display: grid;
  gap: 1.35rem;
  max-height: 42rem;
  overflow: auto;
  padding: 0.15rem 2px 1.25rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(47, 93, 80, 0.15) transparent;
}

@media (max-width: 640px) {
  .report-queue__list {
    gap: var(--space-3);
    max-height: none;
    overflow: visible;
    padding-bottom: 0.5rem;
  }
}
</style>
