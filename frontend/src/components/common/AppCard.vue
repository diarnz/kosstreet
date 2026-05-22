<template>
  <section class="app-card" :class="classes">
    <slot />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { CardVariant } from '@/types/ui';

const props = withDefaults(
  defineProps<{
    variant?: CardVariant;
    interactive?: boolean;
  }>(),
  {
    variant: 'default',
    interactive: false,
  },
);

const classes = computed(() => [
  `app-card--${props.variant}`,
  { 'app-card--interactive': props.interactive },
]);
</script>

<style scoped>
.app-card {
  border: var(--border-soft);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  background: var(--surface-panel);
  box-shadow: var(--shadow-inset);
}

.app-card--elevated {
  box-shadow: var(--shadow-card);
}

.app-card--muted {
  background: var(--surface-muted);
}

.app-card--inset {
  background: var(--surface-inset);
  box-shadow: inset 0 0 0 1px rgba(23, 33, 26, 0.04);
}

.app-card--command {
  background:
    linear-gradient(135deg, rgba(255, 253, 247, 0.94), rgba(221, 232, 213, 0.48)),
    var(--surface-panel-strong);
  box-shadow: var(--shadow-command);
}

.app-card--interactive {
  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    border-color 160ms ease;
}

.app-card--interactive:hover {
  transform: translateY(-2px);
  border-color: rgba(47, 93, 80, 0.32);
  box-shadow: var(--shadow-card);
}
</style>
