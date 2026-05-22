<template>
  <ol
    class="workflow-timeline"
    :class="{ 'workflow-timeline--compact': compact }"
    aria-label="Workflow"
  >
    <li
      v-for="status in statuses"
      :key="status.value"
      class="workflow-timeline__item"
      :class="{
        'workflow-timeline__item--current': status.value === currentStatus,
        'workflow-timeline__item--done': isDone(status.value),
      }"
    >
      <StatusPill :status="status.value" />
      <span v-if="!compact">{{ status.description }}</span>
    </li>
  </ol>
</template>

<script setup lang="ts">
import StatusPill from './StatusPill.vue';
import type { TicketStatus } from '@/types/report';

const props = withDefaults(
  defineProps<{
    currentStatus?: TicketStatus;
    compact?: boolean;
  }>(),
  {
    currentStatus: 'new',
    compact: false,
  },
);

const order: TicketStatus[] = [
  'new',
  'verified',
  'assigned',
  'in_progress',
  'resolved',
  'rejected',
];

const statuses: Array<{ value: TicketStatus; description: string }> = [
  { value: 'new', description: 'Submitted' },
  { value: 'verified', description: 'Verified' },
  { value: 'assigned', description: 'Assigned' },
  { value: 'in_progress', description: 'In progress' },
  { value: 'resolved', description: 'Resolved' },
  { value: 'rejected', description: 'Rejected' },
];

function isDone(status: TicketStatus): boolean {
  const currentIndex = order.indexOf(props.currentStatus);
  const statusIndex = order.indexOf(status);
  return statusIndex < currentIndex && props.currentStatus !== 'rejected';
}
</script>

<style scoped>
.workflow-timeline {
  display: grid;
  gap: var(--space-3);
  padding: 0;
  margin: 0;
  list-style: none;
}

.workflow-timeline--compact {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.workflow-timeline__item {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.55);
}

.workflow-timeline--compact .workflow-timeline__item {
  padding: 0;
  border: 0;
  background: transparent;
  opacity: 0.45;
}

.workflow-timeline__item--current {
  opacity: 1;
}

.workflow-timeline__item--done {
  opacity: 0.72;
}

.workflow-timeline--compact .workflow-timeline__item--current {
  opacity: 1;
  transform: scale(1.04);
}

.workflow-timeline__item span {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>
