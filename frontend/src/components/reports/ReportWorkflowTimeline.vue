<template>
  <ol class="workflow-timeline" aria-label="Municipal workflow timeline">
    <li
      v-for="status in statuses"
      :key="status.value"
      :class="{ 'workflow-timeline__item--current': status.value === currentStatus }"
      class="workflow-timeline__item"
    >
      <StatusPill :status="status.value" />
      <span>{{ status.description }}</span>
    </li>
  </ol>
</template>

<script setup lang="ts">
import StatusPill from './StatusPill.vue';
import type { TicketStatus } from '@/types/report';

withDefaults(
  defineProps<{
    currentStatus?: TicketStatus;
  }>(),
  {
    currentStatus: 'new',
  },
);

const statuses: Array<{ value: TicketStatus; description: string }> = [
  { value: 'new', description: 'Report submitted and waiting for municipal review.' },
  { value: 'verified', description: 'Municipality confirms the issue is valid.' },
  { value: 'assigned', description: 'Responsible department receives ownership.' },
  { value: 'in_progress', description: 'Field work or service response is underway.' },
  { value: 'resolved', description: 'Issue is marked complete after action.' },
  { value: 'rejected', description: 'Report is closed when municipal review rejects the issue.' },
];
</script>

<style scoped>
.workflow-timeline {
  display: grid;
  gap: var(--space-3);
  padding: 0;
  margin: 0;
  list-style: none;
}

.workflow-timeline__item {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.56);
}

.workflow-timeline__item--current {
  border-color: rgba(47, 93, 80, 0.34);
  background: rgba(221, 232, 213, 0.52);
}

.workflow-timeline__item span:last-child {
  color: var(--text-secondary);
}
</style>
