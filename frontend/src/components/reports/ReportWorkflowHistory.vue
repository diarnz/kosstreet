<template>
  <AppCard class="workflow-history stack" variant="inset">
    <div>
      <p class="eyebrow">Workflow history</p>
      <h3>Backend event log</h3>
    </div>

    <AppEmptyState
      v-if="sortedEvents.length === 0"
      tone="dashboard"
      title="No workflow events returned"
      description="Workflow history will appear here after the backend returns real report events."
    />

    <ol v-else class="workflow-history__list" aria-label="Report workflow event history">
      <li v-for="event in sortedEvents" :key="event.id" class="workflow-history__event">
        <div class="workflow-history__status">
          <StatusPill v-if="event.from_status" :status="event.from_status" />
          <span v-if="event.from_status" aria-hidden="true">to</span>
          <StatusPill :status="event.to_status" />
        </div>
        <p v-if="event.note">{{ event.note }}</p>
        <span class="workflow-history__meta">
          {{ event.actor_label }} · {{ formatDateTime(event.created_at) }}
        </span>
      </li>
    </ol>
  </AppCard>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import StatusPill from './StatusPill.vue';
import type { ReportWorkflowEvent } from '@/types/report';
import { formatDateTime } from '@/utils/reportFormatting';

const props = defineProps<{
  events: ReportWorkflowEvent[];
}>();

const sortedEvents = computed(() =>
  [...props.events].sort(
    (first, second) => new Date(first.created_at).getTime() - new Date(second.created_at).getTime(),
  ),
);
</script>

<style scoped>
.workflow-history h3,
.workflow-history p {
  margin: 0;
}

.workflow-history__list {
  display: grid;
  gap: var(--space-3);
  padding: 0;
  margin: 0;
  list-style: none;
}

.workflow-history__event {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.58);
}

.workflow-history__status {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.workflow-history__status span,
.workflow-history__meta {
  color: var(--text-muted);
  font-size: var(--text-sm);
  font-weight: 750;
}

.workflow-history__event p {
  color: var(--text-secondary);
}
</style>
