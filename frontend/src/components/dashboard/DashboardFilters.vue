<template>
  <AppCard class="dashboard-filters" variant="inset">
    <AppField label="Search reports">
      <AppInput
        :model-value="filters.search"
        aria-label="Search reports"
        placeholder="Search ID, category, source, coordinates..."
        @update:model-value="$emit('update:search', $event)"
      />
    </AppField>

    <label class="dashboard-filters__field">
      <span>Status</span>
      <select :value="filters.status" @change="onStatusChange">
        <option value="all">All statuses</option>
        <option v-for="status in statuses" :key="status.value" :value="status.value">
          {{ status.label }}
        </option>
      </select>
    </label>

    <label class="dashboard-filters__field">
      <span>Category</span>
      <select
        :value="filters.category"
        @change="onCategoryChange"
      >
        <option value="all">All categories</option>
        <option v-for="category in categories" :key="category.value" :value="category.value">
          {{ category.label }}
        </option>
      </select>
    </label>

    <label class="dashboard-filters__field">
      <span>Source</span>
      <select :value="filters.source" @change="onSourceChange">
        <option value="all">All sources</option>
        <option value="citizen">Citizen</option>
        <option value="street_audit">AI Street Audit</option>
      </select>
    </label>

    <AppButton variant="secondary" @click="$emit('clear')">Clear filters</AppButton>
  </AppCard>
</template>

<script setup lang="ts">
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppField from '@/components/common/AppField.vue';
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
.dashboard-filters {
  display: grid;
  grid-template-columns: minmax(14rem, 1.5fr) repeat(3, minmax(10rem, 1fr)) auto;
  gap: var(--space-3);
  align-items: end;
}

.dashboard-filters__field {
  display: grid;
  gap: var(--space-2);
}

.dashboard-filters__field span {
  font-size: var(--text-sm);
  font-weight: 800;
}

select {
  min-height: 2.9rem;
  border: var(--border-soft);
  border-radius: var(--radius-sm);
  padding: 0 var(--space-4);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.92);
}

@media (max-width: 980px) {
  .dashboard-filters {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 620px) {
  .dashboard-filters {
    grid-template-columns: 1fr;
  }
}
</style>
