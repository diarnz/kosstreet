<template>
  <AppCard class="photo-field stack-lg animate-scale-in" variant="default">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Step 1</p>
        <h2>Add a photo of the issue</h2>
      </div>
      <AppBadge :tone="modelValue ? 'success' : 'neutral'">
        {{ modelValue ? 'Added' : 'Optional' }}
      </AppBadge>
    </div>

    <label
      class="photo-field__dropzone"
      :class="{ 'photo-field__dropzone--filled': modelValue, 'photo-field__dropzone--drag': isDragging }"
      @dragenter.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @dragover.prevent
      @drop.prevent="onDrop"
    >
      <input
        class="sr-only"
        type="file"
        accept="image/*"
        capture="environment"
        @change="onFileChange"
      />
      <div class="photo-field__camera" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none">
          <path
            d="M4 8h3l1.5-2h7L17 8h3a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2v-8a2 2 0 012-2z"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linejoin="round"
          />
          <circle cx="12" cy="13" r="3.5" stroke="currentColor" stroke-width="1.8" />
        </svg>
      </div>
      <span class="photo-field__cta">{{ modelValue ? 'Change photo' : 'Tap to capture or upload' }}</span>
      <small>PNG, JPG up to {{ maxSizeMb }} MB</small>
    </label>

    <p v-if="error" class="photo-field__error">{{ error }}</p>
    <p v-if="analysisError" class="photo-field__error">{{ analysisError }}</p>

    <p v-if="isAnalyzing" class="photo-field__analyzing">AI is scanning your photo…</p>

    <div v-if="previewUrl && modelValue" class="photo-field__preview animate-fade-in">
      <div class="photo-field__media">
        <AnalyzedFrameViewer
          v-if="analysis?.regions?.length"
          layout="scanner"
          :image-url="previewUrl"
          :regions="analysis.regions"
          :severity="analysis.severity ?? undefined"
          :category="analysis.category ?? undefined"
          :description="analysis.description ?? undefined"
          :confidence="analysis.confidence ?? undefined"
          alt="AI detection overlay on citizen photo"
          aria-label="Citizen issue photo with AI detection overlay"
        />
        <img v-else :src="previewUrl" alt="Selected issue photo preview" />
      </div>
      <div class="photo-field__meta">
        <strong>{{ modelValue.name }}</strong>
        <span>{{ fileSizeLabel }}</span>
        <AppButton variant="secondary" size="sm" @click="$emit('update:modelValue', null)">
          Remove
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
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import { useImagePreview } from '@/composables/useImagePreview';
import type { ReportImageAnalysis } from '@/types/report';

const props = withDefaults(
  defineProps<{
    modelValue: File | null;
    maxSizeMb?: number;
    analysis?: ReportImageAnalysis | null;
    isAnalyzing?: boolean;
    analysisError?: string | null;
  }>(),
  {
    maxSizeMb: 8,
    analysis: null,
    isAnalyzing: false,
    analysisError: null,
  },
);

const emit = defineEmits<{
  'update:modelValue': [file: File | null];
}>();

const error = ref<string | null>(null);
const isDragging = ref(false);
const { previewUrl } = useImagePreview(toRef(props, 'modelValue'));

const fileSizeLabel = computed(() => {
  if (!props.modelValue) return '';
  return `${(props.modelValue.size / 1024 / 1024).toFixed(2)} MB`;
});

function acceptFile(file: File | null) {
  error.value = null;
  if (!file) {
    emit('update:modelValue', null);
    return;
  }

  if (!file.type.startsWith('image/')) {
    error.value = 'Please choose an image file.';
    return;
  }

  if (file.size > props.maxSizeMb * 1024 * 1024) {
    error.value = `Image must be ${props.maxSizeMb} MB or smaller.`;
    return;
  }

  emit('update:modelValue', file);
}

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  acceptFile(input.files?.[0] ?? null);
}

function onDrop(event: DragEvent) {
  isDragging.value = false;
  acceptFile(event.dataTransfer?.files?.[0] ?? null);
}
</script>

<style scoped>
.photo-field h2 {
  margin: 0;
}

.photo-field__dropzone {
  display: grid;
  gap: var(--space-2);
  place-items: center;
  min-height: 11rem;
  padding: var(--space-8);
  border: 2px dashed rgba(47, 93, 80, 0.28);
  border-radius: var(--radius-xl);
  background:
    radial-gradient(circle at 50% 0%, rgba(217, 144, 47, 0.08), transparent 55%),
    rgba(255, 253, 247, 0.62);
  cursor: pointer;
  text-align: center;
  transition:
    border-color var(--motion-fast) ease,
    transform var(--motion-fast) var(--ease-out-expo),
    box-shadow var(--motion-fast) ease;
}

.photo-field__dropzone:hover,
.photo-field__dropzone--drag {
  transform: translateY(-2px);
  border-color: rgba(47, 93, 80, 0.48);
  box-shadow: var(--shadow-card);
}

.photo-field__dropzone--filled {
  min-height: 7rem;
}

.photo-field__camera {
  display: grid;
  place-items: center;
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  color: var(--color-municipal-green);
  background: rgba(221, 232, 213, 0.55);
}

.photo-field__camera svg {
  width: 1.65rem;
  height: 1.65rem;
}

.photo-field__cta {
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

.photo-field__analyzing {
  margin: 0;
  color: var(--color-municipal-green);
  font-weight: 700;
}

.photo-field__preview {
  display: grid;
  grid-template-columns: minmax(0, 16rem) 1fr;
  gap: var(--space-4);
  align-items: center;
}

.photo-field__media {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.photo-field__media img,
.photo-field__media :deep(.analyzed-frame-viewer__image) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-field__media :deep(.analyzed-frame-viewer),
.photo-field__media :deep(.analyzed-frame-viewer__layout),
.photo-field__media :deep(.analyzed-frame-viewer__media) {
  height: 100%;
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
