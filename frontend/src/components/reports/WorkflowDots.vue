<template>
  <div class="workflow-dots" role="list" aria-label="Workflow progress">
    <span
      v-for="status in order"
      :key="status"
      role="listitem"
      class="workflow-dots__dot"
      :class="{
        'workflow-dots__dot--current': status === currentStatus,
        'workflow-dots__dot--done': isDone(status),
        [`workflow-dots__dot--${status}`]: true,
      }"
      :title="statusLabels[status]"
      :aria-label="statusLabels[status]"
      :aria-current="status === currentStatus ? 'step' : undefined"
    />
  </div>
</template>

<script setup lang="ts">
import type { TicketStatus } from '@/types/report';
import { statusLabels } from '@/utils/reportFormatting';

const props = withDefaults(
  defineProps<{
    currentStatus?: TicketStatus;
  }>(),
  {
    currentStatus: 'new',
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

function isDone(status: TicketStatus): boolean {
  const currentIndex = order.indexOf(props.currentStatus);
  const statusIndex = order.indexOf(status);
  return statusIndex < currentIndex && props.currentStatus !== 'rejected';
}
</script>

<style scoped>
.workflow-dots {
  display: flex;
  align-items: center;
  gap: 0.28rem;
}

.workflow-dots__dot {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--text-muted) 35%, transparent);
  transition:
    transform var(--motion-fast) ease,
    background var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

.workflow-dots__dot--done {
  background: color-mix(in srgb, var(--color-municipal-green) 55%, transparent);
}

.workflow-dots__dot--current {
  transform: scale(1.35);
  background: var(--color-municipal-green);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-municipal-green) 22%, transparent);
}

.workflow-dots__dot--rejected.workflow-dots__dot--current {
  background: var(--color-repair-red);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-repair-red) 22%, transparent);
}
</style>
