<template>
  <span class="department-chip">
    <span class="department-chip__label">Route to</span>
    <strong>{{ department }}</strong>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { IssueCategory } from '@/types/report';
import { getSuggestedDepartment } from '@/utils/reportRouting';

const props = defineProps<{
  category: IssueCategory;
}>();

const department = computed(() => getSuggestedDepartment(props.category));
</script>

<style scoped>
.department-chip {
  display: inline-flex;
  gap: 0.35rem;
  align-items: center;
  padding: 0.35rem 0.65rem;
  border-radius: var(--radius-pill);
  color: var(--status-verified-text);
  background: var(--color-info-surface);
  font-size: var(--text-xs);
}

.department-chip__label {
  color: var(--text-muted);
  font-weight: 750;
}

.department-chip strong {
  font-weight: 900;
}
</style>
