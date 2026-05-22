<template>
  <textarea
    class="app-textarea"
    :aria-label="ariaLabel"
    :disabled="disabled"
    :maxlength="maxlength"
    :placeholder="placeholder"
    :value="modelValue"
    @input="onInput"
  />
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue?: string;
    placeholder?: string;
    disabled?: boolean;
    ariaLabel?: string;
    maxlength?: number;
  }>(),
  {
    modelValue: '',
    placeholder: '',
    disabled: false,
    ariaLabel: undefined,
    maxlength: undefined,
  },
);

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value);
}
</script>

<style scoped>
.app-textarea {
  width: 100%;
  min-height: 8rem;
  resize: vertical;
  border: var(--border-soft);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  color: var(--color-ink);
  background: rgba(255, 253, 247, 0.92);
}

.app-textarea::placeholder {
  color: rgba(58, 63, 59, 0.5);
}

.app-textarea:disabled {
  color: rgba(58, 63, 59, 0.5);
  background: rgba(215, 208, 194, 0.3);
}
</style>

