<template>
  <AppCard class="audit-run-filters" variant="inset">
    <AppField label="Search audit runs">
      <AppInput
        :model-value="filters.search"
        aria-label="Search audit runs"
        placeholder="Search route, municipality, status, ID..."
        @update:model-value="$emit('update:search', $event)"
      />
    </AppField>

    <label class="audit-run-filters__field">
      <span>Status</span>
      <select :value="filters.status" @change="onStatusChange">
        <option value="all">All statuses</option>
        <option v-for="status in statuses" :key="status.value" :value="status.value">
          {{ status.label }}
        </option>
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
  display: grid;
  grid-template-columns: minmax(14rem, 1fr) minmax(10rem, 0.45fr) auto;
  gap: var(--space-3);
  align-items: end;
}

.audit-run-filters__field {
  display: grid;
  gap: var(--space-2);
}

.audit-run-filters__field span {
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

@media (max-width: 760px) {
  .audit-run-filters {
    grid-template-columns: 1fr;
  }
}
</style>
