<template>
  <section class="glass-panel" :class="[`glass-panel--${padding}`, { 'glass-panel--elevated': elevated, 'glass-panel--interactive': interactive }]">
    <header v-if="label || $slots.header" class="glass-panel__header">
      <slot name="header">
        <p v-if="label" class="command-label">{{ label }}</p>
      </slot>
    </header>
    <slot />
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string;
    elevated?: boolean;
    interactive?: boolean;
    padding?: 'sm' | 'md' | 'lg';
  }>(),
  {
    elevated: false,
    interactive: false,
    padding: 'md',
  },
);
</script>

<style scoped>
.glass-panel {
  display: grid;
  gap: var(--space-4);
}

.glass-panel--sm {
  padding: var(--space-4);
}

.glass-panel--md {
  padding: var(--space-5);
}

.glass-panel--lg {
  padding: var(--space-6);
}

.glass-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
