<template>
  <AppCard class="department-suggestion" variant="muted">
    <AppBadge tone="info">Suggested department</AppBadge>
    <strong>{{ department }}</strong>
    <p>Derived locally from issue category. Assignment is not saved until backend workflow support exists.</p>
  </AppCard>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import type { IssueCategory } from '@/types/report';
import { getSuggestedDepartment } from '@/utils/reportRouting';

const props = defineProps<{
  category: IssueCategory;
}>();

const department = computed(() => getSuggestedDepartment(props.category));
</script>

<style scoped>
.department-suggestion {
  display: grid;
  gap: var(--space-3);
}

.department-suggestion strong {
  font-size: var(--text-lg);
}

.department-suggestion p {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>

