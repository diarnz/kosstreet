<template>
  <div class="filter-bar" role="search" aria-label="Filter reports">
    <div class="filter-bar__search-wrap">
      <svg class="filter-bar__search-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="6.5" cy="6.5" r="4" stroke="currentColor" stroke-width="1.4" />
        <path d="M10 10l3 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
      </svg>
      <input
        class="filter-bar__search"
        type="search"
        :value="filters.search"
        aria-label="Search reports"
        placeholder="Search reports…"
        @input="$emit('update:search', ($event.target as HTMLInputElement).value)"
      />
    </div>

    <span class="filter-bar__divider" aria-hidden="true" />

    <select
      class="filter-bar__select"
      :value="filters.status"
      aria-label="Filter by status"
      @change="onStatusChange"
    >
      <option value="all">All statuses</option>
      <option v-for="status in statuses" :key="status.value" :value="status.value">
        {{ status.label }}
      </option>
    </select>

    <select
      class="filter-bar__select"
      :value="filters.category"
      aria-label="Filter by category"
      @change="onCategoryChange"
    >
      <option value="all">All categories</option>
      <option v-for="category in categories" :key="category.value" :value="category.value">
        {{ category.label }}
      </option>
    </select>

    <select
      class="filter-bar__select"
      :value="filters.source"
      aria-label="Filter by source"
      @change="onSourceChange"
    >
      <option value="all">All sources</option>
      <option value="citizen">Citizen</option>
      <option value="street_audit">AI audit</option>
    </select>

    <button
      v-if="filters.search || filters.status !== 'all' || filters.category !== 'all' || filters.source !== 'all'"
      class="filter-bar__clear"
      type="button"
      aria-label="Clear all filters"
      @click="$emit('clear')"
    >
      ✕
    </button>
  </div>
</template>

<script setup lang="ts">
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
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  padding: 0.32rem 0.5rem 0.32rem 0.32rem;
  border: 1px solid rgba(23, 33, 26, 0.09);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.6);
  backdrop-filter: blur(14px);
  width: fit-content;
  max-width: 100%;
}

/* Search */
.filter-bar__search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-bar__search-icon {
  position: absolute;
  left: 0.65rem;
  width: 13px;
  height: 13px;
  color: var(--text-muted);
  pointer-events: none;
  flex-shrink: 0;
}

.filter-bar__search {
  height: 2rem;
  padding: 0 0.75rem 0 2rem;
  border: none;
  border-radius: var(--radius-pill);
  background: rgba(23, 33, 26, 0.05);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 750;
  width: 14rem;
  outline: none;
  transition: background var(--motion-fast) ease, width var(--motion-base) var(--ease-out-expo);
}

.filter-bar__search::placeholder {
  color: var(--text-muted);
  font-weight: 700;
}

.filter-bar__search:focus {
  background: rgba(47, 93, 80, 0.07);
  width: 18rem;
}

/* Vertical divider */
.filter-bar__divider {
  display: block;
  width: 1px;
  height: 1.25rem;
  background: rgba(23, 33, 26, 0.1);
  flex-shrink: 0;
  margin: 0 0.1rem;
}

/* Selects */
.filter-bar__select {
  height: 2rem;
  padding: 0 1.75rem 0 0.75rem;
  border: none;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 800;
  cursor: pointer;
  appearance: auto;
  outline: none;
  transition: background var(--motion-fast) ease, color var(--motion-fast) ease;
}

.filter-bar__select:hover,
.filter-bar__select:focus {
  background: rgba(47, 93, 80, 0.07);
  color: var(--text-primary);
}

/* Clear */
.filter-bar__clear {
  display: grid;
  place-items: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  border: none;
  background: rgba(200, 76, 58, 0.1);
  color: var(--color-repair-red);
  font-size: 0.6rem;
  font-weight: 900;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--motion-fast) ease, transform var(--motion-fast) ease;
}

.filter-bar__clear:hover {
  background: rgba(200, 76, 58, 0.2);
  transform: scale(1.08);
}

@media (max-width: 760px) {
  .filter-bar {
    width: 100%;
    border-radius: var(--radius-lg);
  }

  .filter-bar__search {
    width: 100%;
  }

  .filter-bar__search:focus {
    width: 100%;
  }
}
</style>
