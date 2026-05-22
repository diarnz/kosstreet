<template>
  <label class="app-field" :for="forId">
    <span class="app-field__label">{{ label }}</span>
    <slot />
    <span v-if="error" class="app-field__error">{{ error }}</span>
    <span v-else-if="helper" class="app-field__helper">{{ helper }}</span>
  </label>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  helper?: string;
  error?: string;
  forId?: string;
}>();
</script>

<style scoped>
.app-field {
  display: grid;
  gap: var(--space-2);
}

.app-field__label {
  font-size: var(--text-sm);
  font-weight: 800;
  color: var(--color-ink);
}

.app-field__helper,
.app-field__error {
  font-size: var(--text-sm);
}

.app-field__helper {
  color: rgba(58, 63, 59, 0.72);
}

.app-field__error {
  color: var(--color-repair-red);
}
</style>

