<template>
  <nav class="step-rail" :aria-label="ariaLabel">
    <ol class="step-rail__list">
      <li
        v-for="(step, index) in steps"
        :key="step.id"
        class="step-rail__item"
        :class="{
          'step-rail__item--current': step.id === currentStep,
          'step-rail__item--complete': completedSteps.includes(step.id),
          'step-rail__item--clickable': completedSteps.includes(step.id) && step.id !== currentStep,
        }"
      >
        <button
          v-if="completedSteps.includes(step.id) && step.id !== currentStep"
          class="step-rail__button"
          type="button"
          @click="$emit('navigate', step.id)"
        >
          <span class="step-rail__dot" aria-hidden="true">
            <svg viewBox="0 0 16 16" fill="none">
              <path
                d="M3.5 8.2l2.8 2.8 6.2-6.4"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>
          <span class="step-rail__label">{{ step.label }}</span>
        </button>
        <div v-else class="step-rail__static">
          <span class="step-rail__dot" aria-hidden="true">
            <span v-if="step.id === currentStep">{{ index + 1 }}</span>
            <span v-else>{{ index + 1 }}</span>
          </span>
          <span class="step-rail__label">{{ step.label }}</span>
        </div>
        <span
          v-if="index < steps.length - 1"
          class="step-rail__connector"
          :class="{ 'step-rail__connector--complete': completedSteps.includes(step.id) }"
          aria-hidden="true"
        />
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
export interface ReportStep {
  id: string;
  label: string;
}

withDefaults(
  defineProps<{
    currentStep: string;
    steps: ReportStep[];
    completedSteps: string[];
    ariaLabel?: string;
  }>(),
  {
    ariaLabel: 'Report progress',
  },
);

defineEmits<{
  navigate: [stepId: string];
}>();
</script>

<style scoped>
.step-rail__list {
  display: flex;
  gap: 0;
  align-items: flex-start;
  padding: 0;
  margin: 0;
  list-style: none;
  overflow-x: auto;
  scrollbar-width: none;
}

.step-rail__list::-webkit-scrollbar {
  display: none;
}

.step-rail__item {
  position: relative;
  display: flex;
  flex: 1 1 0;
  flex-direction: column;
  align-items: center;
  min-width: 4.5rem;
}

.step-rail__button,
.step-rail__static {
  display: grid;
  gap: var(--space-2);
  justify-items: center;
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
}

.step-rail__button {
  cursor: pointer;
}

.step-rail__dot {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border: 2px solid rgba(23, 33, 26, 0.14);
  border-radius: 50%;
  color: var(--text-muted);
  background: rgba(255, 253, 247, 0.9);
  font-size: 0.78rem;
  font-weight: 900;
  transition:
    transform var(--motion-fast) var(--ease-spring),
    background var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    color var(--motion-fast) ease;
}

.step-rail__dot svg {
  width: 0.85rem;
  height: 0.85rem;
}

.step-rail__label {
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  white-space: nowrap;
}

.step-rail__connector {
  position: absolute;
  top: 1rem;
  left: calc(50% + 1rem);
  width: calc(100% - 2rem);
  height: 2px;
  background: rgba(23, 33, 26, 0.1);
  transform: translateY(-50%);
}

.step-rail__connector--complete {
  background: rgba(47, 93, 80, 0.45);
}

.step-rail__item--current .step-rail__dot {
  color: var(--text-inverse);
  background: var(--action-primary);
  border-color: transparent;
  transform: scale(1.08);
  box-shadow: 0 8px 22px rgba(47, 93, 80, 0.28);
}

.step-rail__item--current .step-rail__label {
  color: var(--text-primary);
}

.step-rail__item--complete .step-rail__dot {
  color: var(--color-municipal-green);
  border-color: rgba(47, 93, 80, 0.35);
  background: rgba(221, 232, 213, 0.72);
}

.step-rail__item--complete .step-rail__label {
  color: var(--text-secondary);
}

.step-rail__item--clickable:hover .step-rail__dot {
  transform: scale(1.04);
}

@media (max-width: 640px) {
  .step-rail__item {
    min-width: 3.5rem;
  }

  .step-rail__dot {
    width: 1.75rem;
    height: 1.75rem;
    font-size: 0.68rem;
  }

  .step-rail__dot svg {
    width: 0.75rem;
    height: 0.75rem;
  }

  .step-rail__label {
    font-size: 0.6rem;
    letter-spacing: 0.03em;
  }

  .step-rail__connector {
    top: 0.875rem;
    left: calc(50% + 0.875rem);
    width: calc(100% - 1.75rem);
  }
}
</style>
