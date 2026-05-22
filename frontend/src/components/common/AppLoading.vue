<template>
  <div class="app-loading" :class="`app-loading--${variant}`" role="status" aria-live="polite">
    <span v-if="variant === 'spinner'" class="app-loading__spinner" aria-hidden="true" />
    <span v-else class="app-loading__skeleton" aria-hidden="true" />
    <span>{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string;
    variant?: 'spinner' | 'skeleton';
    tone?: 'neutral' | 'success' | 'audit';
  }>(),
  {
    label: 'Loading',
    variant: 'spinner',
    tone: 'neutral',
  },
);
</script>

<style scoped>
.app-loading {
  display: inline-flex;
  gap: var(--space-3);
  align-items: center;
  color: var(--text-secondary);
  font-weight: 700;
}

.app-loading__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(47, 93, 80, 0.22);
  border-top-color: var(--action-primary);
  border-radius: 50%;
  animation: spin 800ms linear infinite;
}

.app-loading__skeleton {
  width: 5rem;
  height: 0.85rem;
  border-radius: var(--radius-pill);
  background: linear-gradient(90deg, rgba(215, 208, 194, 0.4), rgba(255, 253, 247, 0.9), rgba(215, 208, 194, 0.4));
  background-size: 200% 100%;
  animation: shimmer 1200ms ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}
</style>
