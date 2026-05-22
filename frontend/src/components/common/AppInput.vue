<template>
  <input
    class="app-input"
    :aria-label="ariaLabel"
    :disabled="disabled"
    :placeholder="placeholder"
    :type="type"
    :value="modelValue"
    @input="onInput"
  />
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue?: string;
    placeholder?: string;
    type?: string;
    disabled?: boolean;
    ariaLabel?: string;
  }>(),
  {
    modelValue: '',
    placeholder: '',
    type: 'text',
    disabled: false,
    ariaLabel: undefined,
  },
);

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value);
}
</script>

<style scoped>
.app-input {
  width: 100%;
  min-height: 2.9rem;
  border: var(--border-soft);
  border-radius: var(--radius-sm);
  padding: 0 var(--space-4);
  color: var(--color-ink);
  background: rgba(255, 253, 247, 0.92);
}

.app-input::placeholder {
  color: rgba(58, 63, 59, 0.5);
}

.app-input:disabled {
  color: rgba(58, 63, 59, 0.5);
  background: rgba(215, 208, 194, 0.3);
}
</style>

