<template>
  <AppCard class="photo-field stack" variant="inset">
    <div class="cluster-between">
      <div>
        <h2>Photo</h2>
        <p>Select a photo for local review. Image upload will be connected when the backend endpoint exists.</p>
      </div>
      <AppBadge tone="neutral">Local preview only</AppBadge>
    </div>

    <label class="photo-field__dropzone">
      <input
        class="sr-only"
        type="file"
        accept="image/*"
        capture="environment"
        @change="onFileChange"
      />
      <span>{{ modelValue ? 'Change image' : 'Choose or take a photo' }}</span>
      <small>Image files up to {{ maxSizeMb }} MB</small>
    </label>

    <p v-if="error" class="photo-field__error">{{ error }}</p>

    <div v-if="previewUrl && modelValue" class="photo-field__preview">
      <img :src="previewUrl" alt="Selected issue photo preview" />
      <div class="photo-field__meta">
        <strong>{{ modelValue.name }}</strong>
        <span>{{ fileSizeLabel }} · {{ modelValue.type }}</span>
        <AppButton variant="secondary" size="sm" @click="$emit('update:modelValue', null)">
          Remove image
        </AppButton>
      </div>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, ref, toRef } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import { useImagePreview } from '@/composables/useImagePreview';

const props = withDefaults(
  defineProps<{
    modelValue: File | null;
    maxSizeMb?: number;
  }>(),
  {
    maxSizeMb: 8,
  },
);

const emit = defineEmits<{
  'update:modelValue': [file: File | null];
}>();

const error = ref<string | null>(null);
const { previewUrl } = useImagePreview(toRef(props, 'modelValue'));

const fileSizeLabel = computed(() => {
  if (!props.modelValue) return '';
  return `${(props.modelValue.size / 1024 / 1024).toFixed(2)} MB`;
});

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0] ?? null;
  error.value = null;

  if (!file) {
    emit('update:modelValue', null);
    return;
  }

  if (!file.type.startsWith('image/')) {
    error.value = 'Please choose an image file.';
    input.value = '';
    return;
  }

  if (file.size > props.maxSizeMb * 1024 * 1024) {
    error.value = `Image must be ${props.maxSizeMb} MB or smaller.`;
    input.value = '';
    return;
  }

  emit('update:modelValue', file);
}
</script>

<style scoped>
.photo-field h2 {
  margin: 0 0 var(--space-2);
}

.photo-field p {
  color: var(--text-secondary);
}

.photo-field__dropzone {
  display: grid;
  gap: var(--space-2);
  place-items: center;
  min-height: 9rem;
  padding: var(--space-6);
  border: 1px dashed rgba(47, 93, 80, 0.34);
  border-radius: var(--radius-lg);
  background: rgba(255, 253, 247, 0.58);
  cursor: pointer;
  text-align: center;
}

.photo-field__dropzone span {
  color: var(--text-primary);
  font-weight: 900;
}

.photo-field__dropzone small,
.photo-field__meta span {
  color: var(--text-muted);
}

.photo-field__error {
  color: var(--color-repair-red);
  font-weight: 800;
}

.photo-field__preview {
  display: grid;
  grid-template-columns: minmax(0, 12rem) 1fr;
  gap: var(--space-4);
  align-items: center;
}

.photo-field__preview img {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: var(--radius-md);
  object-fit: cover;
}

.photo-field__meta {
  display: grid;
  gap: var(--space-2);
}

@media (max-width: 620px) {
  .photo-field__preview {
    grid-template-columns: 1fr;
  }
}
</style>

