<template>
  <AppCard class="category-selector stack" variant="inset">
    <div class="cluster-between">
      <div>
        <h2>Issue category</h2>
        <p>Select the category that best describes the issue.</p>
      </div>
      <AppBadge tone="warning">Required</AppBadge>
    </div>

    <div class="category-selector__grid" role="radiogroup" aria-label="Issue category">
      <button
        v-for="option in options"
        :key="option.value"
        class="category-selector__option"
        :class="{ 'category-selector__option--selected': modelValue === option.value }"
        type="button"
        role="radio"
        :aria-checked="modelValue === option.value"
        @click="$emit('update:modelValue', option.value)"
      >
        <IssueCategoryBadge :category="option.value" />
        <span>{{ option.description }}</span>
      </button>
    </div>

    <AppCard variant="muted" class="ai-note">
      <AppBadge tone="source-ai-audit">AI analysis</AppBadge>
      <p>AI image analysis is not connected yet. Choose the category manually for this report.</p>
    </AppCard>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import IssueCategoryBadge from './IssueCategoryBadge.vue';
import type { IssueCategory } from '@/types/report';

defineProps<{
  modelValue: IssueCategory | null;
}>();

defineEmits<{
  'update:modelValue': [value: IssueCategory];
}>();

const options: Array<{ value: IssueCategory; description: string }> = [
  { value: 'pothole', description: 'Road surface damage or asphalt break.' },
  { value: 'garbage', description: 'Illegal dumping or waste on the street.' },
  { value: 'broken_streetlight', description: 'Damaged or non-working streetlight.' },
  { value: 'blocked_sidewalk', description: 'Blocked pedestrian path or sidewalk.' },
  { value: 'damaged_sign', description: 'Damaged traffic or public sign.' },
  { value: 'other', description: 'Another visible civic issue.' },
];
</script>

<style scoped>
.category-selector h2 {
  margin: 0 0 var(--space-2);
}

.category-selector p {
  color: var(--text-secondary);
}

.category-selector__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.category-selector__option {
  display: grid;
  gap: var(--space-3);
  min-height: 8rem;
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.62);
  text-align: left;
}

.category-selector__option--selected {
  border-color: rgba(47, 93, 80, 0.42);
  background: rgba(221, 232, 213, 0.62);
  box-shadow: var(--shadow-card);
}

.ai-note {
  display: grid;
  gap: var(--space-3);
}

@media (max-width: 620px) {
  .category-selector__grid {
    grid-template-columns: 1fr;
  }
}
</style>

