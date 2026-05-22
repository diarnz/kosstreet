<template>
  <div class="empty-state" :class="`empty-state--${tone}`">
    <div class="empty-state__marker" aria-hidden="true" />
    <div class="stack">
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
    </div>
    <AppButton v-if="actionLabel" variant="secondary" @click="$emit('action')">
      {{ actionLabel }}
    </AppButton>
  </div>
</template>

<script setup lang="ts">
import AppButton from './AppButton.vue';

defineProps<{
  title: string;
  description: string;
  actionLabel?: string;
  tone?: 'neutral' | 'report' | 'dashboard' | 'audit';
}>();

defineEmits<{
  action: [];
}>();
</script>

<style scoped>
.empty-state {
  display: grid;
  gap: var(--space-4);
  place-items: start;
  padding: var(--space-8);
  border: 1px dashed rgba(47, 93, 80, 0.28);
  border-radius: var(--radius-lg);
  background: rgba(221, 232, 213, 0.34);
}

.empty-state__marker {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.95), rgba(63, 110, 140, 0.85)),
    var(--color-municipal-green);
  box-shadow: 0 12px 26px rgba(47, 93, 80, 0.18);
}

h2 {
  margin: 0;
  font-size: var(--text-xl);
}

p {
  max-width: 42rem;
  color: var(--text-secondary);
}

.empty-state--dashboard {
  border-color: rgba(63, 110, 140, 0.26);
  background: rgba(221, 232, 238, 0.36);
}

.empty-state--dashboard .empty-state__marker {
  background: linear-gradient(135deg, var(--color-resolved-blue), var(--color-municipal-green));
}

.empty-state--audit {
  border-color: rgba(102, 81, 41, 0.24);
  background: rgba(232, 226, 212, 0.42);
}

.empty-state--audit .empty-state__marker {
  background: linear-gradient(135deg, var(--color-amber-signal), #7a6335);
}

.empty-state--report .empty-state__marker {
  background: linear-gradient(135deg, var(--color-municipal-green), var(--color-garbage-green));
}
</style>
