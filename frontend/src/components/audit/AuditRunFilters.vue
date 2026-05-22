<template>
  <div class="audit-run-filters">
    <AppInput
      class="audit-run-filters__search"
      :model-value="filters.search"
      aria-label="Search audit runs"
      placeholder="Search route, municipality…"
      @update:model-value="$emit('update:search', $event)"
    />

    <select :value="filters.status" aria-label="Filter by status" @change="onStatusChange">
      <option value="all">All statuses</option>
      <option v-for="status in statuses" :key="status.value" :value="status.value">
        {{ status.label }}
      </option>
    </select>

    <AppButton variant="secondary" size="sm" @click="$emit('clear')">Clear</AppButton>
  </div>
</template>

<script setup lang="ts">
import AppButton from '@/components/common/AppButton.vue';
import AppInput from '@/components/common/AppInput.vue';
import type { AuditRunFiltersState, AuditRunStatus } from '@/types/audit';
import { auditRunStatusLabels } from '@/utils/auditFormatting';

defineProps<{
  filters: AuditRunFiltersState;
}>();

const emit = defineEmits<{
  'update:search': [value: string];
  'update:status': [value: AuditRunStatus | 'all'];
  clear: [];
}>();

const statuses = (Object.keys(auditRunStatusLabels) as AuditRunStatus[]).map((value) => ({
  value,
  label: auditRunStatusLabels[value],
}));

function onStatusChange(event: Event) {
  emit('update:status', (event.target as HTMLSelectElement).value as AuditRunStatus | 'all');
}
</script>

<style scoped>
.audit-run-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.audit-run-filters__search {
  flex: 1 1 10rem;
  min-width: 8rem;
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
}

@media (max-width: 620px) {
  .audit-run-filters {
    flex-direction: column;
    align-items: stretch;
  }

  select {
    width: 100%;
  }
}
</style>
