<template>
  <button class="app-button" :class="classes" :type="type" :disabled="disabled">
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ButtonVariant } from '@/types/ui';

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant;
    size?: 'sm' | 'md' | 'lg';
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    fullWidth?: boolean;
  }>(),
  {
    variant: 'primary',
    size: 'md',
    type: 'button',
    disabled: false,
    fullWidth: false,
  },
);

const classes = computed(() => [
  `app-button--${props.variant}`,
  `app-button--${props.size}`,
  { 'app-button--full-width': props.fullWidth },
]);
</script>

<style scoped>
.app-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  min-height: 2.75rem;
  border: 0;
  border-radius: var(--radius-pill);
  font-weight: 800;
  letter-spacing: -0.01em;
  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    background 160ms ease,
    border-color 160ms ease;
  box-shadow: none;
}

.app-button:not(:disabled):hover {
  transform: translateY(-1px);
}

.app-button:not(:disabled):active {
  transform: translateY(0);
}

.app-button:disabled {
  opacity: 0.56;
}

.app-button--sm {
  min-height: 2.25rem;
  padding: 0 var(--space-4);
  font-size: var(--text-sm);
}

.app-button--md {
  padding: 0 var(--space-5);
  font-size: var(--text-md);
}

.app-button--lg {
  min-height: 3.2rem;
  padding: 0 var(--space-6);
  font-size: var(--text-lg);
}

.app-button--primary {
  color: var(--text-inverse);
  background: var(--action-primary);
  box-shadow: 0 12px 30px rgba(47, 93, 80, 0.2);
}

.app-button--primary:not(:disabled):hover {
  background: var(--action-primary-hover);
}

.app-button--secondary {
  color: var(--text-primary);
  background: var(--action-secondary);
  border: var(--border-strong);
}

.app-button--ghost {
  color: var(--text-secondary);
  background: transparent;
}

.app-button--danger {
  color: var(--text-inverse);
  background: var(--action-danger);
}

.app-button--full-width {
  width: 100%;
}
</style>
