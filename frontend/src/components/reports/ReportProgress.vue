<template>
  <ol class="report-progress" aria-label="Report progress">
    <li
      v-for="(step, index) in steps"
      :key="step.id"
      class="report-progress__item"
      :class="{
        'report-progress__item--current': step.id === currentStep,
        'report-progress__item--complete': completedSteps.includes(step.id),
      }"
    >
      <span>{{ String(index + 1).padStart(2, '0') }}</span>
      <strong>{{ step.label }}</strong>
    </li>
  </ol>
</template>

<script setup lang="ts">
export interface ReportStep {
  id: string;
  label: string;
}

defineProps<{
  currentStep: string;
  steps: ReportStep[];
  completedSteps: string[];
}>();
</script>

<style scoped>
.report-progress {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: var(--space-2);
  padding: 0;
  margin: 0;
  list-style: none;
}

.report-progress__item {
  display: grid;
  gap: var(--space-1);
  padding: var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface-inset);
}

.report-progress__item span {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
}

.report-progress__item strong {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.report-progress__item--current {
  border-color: rgba(47, 93, 80, 0.32);
  background: rgba(221, 232, 213, 0.58);
}

.report-progress__item--current strong,
.report-progress__item--complete strong {
  color: var(--text-primary);
}

.report-progress__item--complete span {
  color: var(--color-municipal-green);
}
</style>

