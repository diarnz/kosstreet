<template>
  <div class="filter-bar glass-panel">
    <p class="command-label filter-bar__label">Filters</p>
    <div class="filter-bar__controls">
      <AppInput
        class="filter-bar__search"
        :model-value="filters.search"
        aria-label="Search reports"
        placeholder="Search…"
        @update:model-value="$emit('update:search', $event)"
      />

      <select :value="filters.status" aria-label="Filter by status" @change="onStatusChange">
        <option value="all">All statuses</option>
        <option v-for="status in statuses" :key="status.value" :value="status.value">
          {{ status.label }}
        </option>
      </select>

      <select :value="filters.category" aria-label="Filter by category" @change="onCategoryChange">
        <option value="all">All categories</option>
        <option v-for="category in categories" :key="category.value" :value="category.value">
          {{ category.label }}
        </option>
      </select>

      <select :value="filters.source" aria-label="Filter by source" @change="onSourceChange">
        <option value="all">All sources</option>
        <option value="citizen">Citizen</option>
        <option value="street_audit">AI audit</option>
      </select>

      <AppButton variant="secondary" size="sm" @click="$emit('clear')">Clear</AppButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppButton from '@/components/common/AppButton.vue';
import AppInput from '@/components/common/AppInput.vue';
import type { DashboardFiltersState } from '@/types/dashboard';
import type { IssueCategory, ReportSource, TicketStatus } from '@/types/report';
import { categoryLabels, statusLabels } from '@/utils/reportFormatting';

defineProps<{
  filters: DashboardFiltersState;
}>();

const emit = defineEmits<{
  'update:search': [value: string];
  'update:status': [value: TicketStatus | 'all'];
  'update:category': [value: IssueCategory | 'all'];
  'update:source': [value: ReportSource | 'all'];
  clear: [];
}>();

const statuses = (Object.keys(statusLabels) as TicketStatus[]).map((value) => ({
  value,
  label: statusLabels[value],
}));

const categories = (Object.keys(categoryLabels) as IssueCategory[]).map((value) => ({
  value,
  label: categoryLabels[value],
}));

function getSelectValue(event: Event): string {
  return (event.target as HTMLSelectElement).value;
}

function onStatusChange(event: Event) {
  emit('update:status', getSelectValue(event) as TicketStatus | 'all');
}

function onCategoryChange(event: Event) {
  emit('update:category', getSelectValue(event) as IssueCategory | 'all');
}

function onSourceChange(event: Event) {
  emit('update:source', getSelectValue(event) as ReportSource | 'all');
}
</script>

<style scoped>
.filter-bar {
  display: grid;
  gap: var(--space-3);
  padding: var(--space-4);
}

.filter-bar__controls {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.filter-bar__search {
  flex: 1 1 12rem;
  min-width: 10rem;
}

select {
  min-height: 2.65rem;
  padding: 0 0.85rem;
  border: var(--border-soft);
  border-radius: var(--radius-pill);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.72);
  font-size: var(--text-sm);
  font-weight: 750;
  transition: border-color var(--motion-fast) ease, box-shadow var(--motion-fast) ease;
}

select:focus-visible {
  border-color: rgba(47, 93, 80, 0.35);
}

@media (max-width: 620px) {
  .filter-bar__controls {
    flex-direction: column;
    align-items: stretch;
  }

  select {
    width: 100%;
  }
}
</style>
