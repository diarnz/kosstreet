<template>
  <AppCard class="category-selector stack-lg animate-scale-in" variant="default">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Step 3</p>
        <h2>What type of issue is it?</h2>
      </div>
      <AppBadge :tone="modelValue ? 'success' : 'warning'">
        {{ modelValue ? 'Selected' : 'Required' }}
      </AppBadge>
    </div>

    <div class="category-selector__grid" role="radiogroup" aria-label="Issue category">
      <button
        v-for="option in options"
        :key="option.value"
        ref="optionButtons"
        class="category-selector__option"
        :class="{ 'category-selector__option--selected': modelValue === option.value }"
        type="button"
        role="radio"
        :aria-checked="modelValue === option.value"
        @click="$emit('update:modelValue', option.value)"
        @keydown="onOptionKeydown($event, option.value)"
      >
        <span class="category-selector__icon-wrap">
          <CategoryIcon :category="option.value" />
        </span>
        <strong>{{ option.label }}</strong>
      </button>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import CategoryIcon from './CategoryIcon.vue';
import type { IssueCategory } from '@/types/report';
import { categoryLabels } from '@/utils/reportFormatting';

defineProps<{
  modelValue: IssueCategory | null;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: IssueCategory];
}>();

const optionButtons = ref<HTMLButtonElement[]>([]);

const options: Array<{ value: IssueCategory; label: string }> = [
  { value: 'pothole', label: categoryLabels.pothole },
  { value: 'garbage', label: categoryLabels.garbage },
  { value: 'broken_streetlight', label: categoryLabels.broken_streetlight },
  { value: 'blocked_sidewalk', label: categoryLabels.blocked_sidewalk },
  { value: 'damaged_sign', label: categoryLabels.damaged_sign },
  { value: 'other', label: categoryLabels.other },
];

function selectByOffset(currentValue: IssueCategory, offset: number) {
  const currentIndex = options.findIndex((option) => option.value === currentValue);
  const nextIndex = (currentIndex + offset + options.length) % options.length;
  const nextValue = options[nextIndex].value;

  emit('update:modelValue', nextValue);
  optionButtons.value[nextIndex]?.focus();
}

function onOptionKeydown(event: KeyboardEvent, value: IssueCategory) {
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    event.preventDefault();
    selectByOffset(value, 1);
  }

  if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    event.preventDefault();
    selectByOffset(value, -1);
  }
}
</script>

<style scoped>
.category-selector h2 {
  margin: 0;
}

.category-selector__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
}

.category-selector__option {
  display: grid;
  gap: var(--space-3);
  justify-items: center;
  min-height: 6.5rem;
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.72);
  text-align: center;
  transition:
    transform var(--motion-fast) var(--ease-spring),
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.category-selector__option:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card);
}

.category-selector__option--selected {
  color: var(--text-primary);
  background: rgba(221, 232, 213, 0.62);
  border-color: rgba(47, 93, 80, 0.42);
  box-shadow: var(--shadow-command);
  transform: translateY(-2px) scale(1.02);
}

.category-selector__icon-wrap {
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 50%;
  color: var(--color-municipal-green);
  background: rgba(221, 232, 213, 0.55);
}

.category-selector__option strong {
  font-size: var(--text-sm);
}

@media (max-width: 760px) {
  .category-selector__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 420px) {
  .category-selector__grid {
    grid-template-columns: 1fr;
  }
}
</style>
