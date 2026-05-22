<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="frame-lightbox"
      role="dialog"
      aria-modal="true"
      :aria-label="title"
      @click.self="emit('close')"
    >
      <button class="frame-lightbox__close" type="button" aria-label="Close" @click="emit('close')">
        ×
      </button>

      <div class="frame-lightbox__panel animate-scale-in">
        <div class="frame-lightbox__stage">
          <img
            v-if="resolvedImageUrl"
            :src="resolvedImageUrl"
            :alt="alt"
            class="frame-lightbox__image"
          />
          <div v-else class="frame-lightbox__placeholder muted">Frame unavailable</div>

          <DetectionCircleOverlay
            v-if="resolvedImageUrl && displayRegions.length"
            overlay-id="lightbox"
            :category="category ?? undefined"
            :confidence="confidence ?? undefined"
            :description="description ?? undefined"
            :regions="displayRegions"
            :severity="severity ?? undefined"
          />
        </div>

        <div class="frame-lightbox__footer">
          <div class="frame-lightbox__meta">
            <span v-if="frameLabel" class="frame-lightbox__frame">{{ frameLabel }}</span>
            <span v-if="category" class="frame-lightbox__category">{{ categoryLabel }}</span>
            <span
              v-if="severity"
              class="frame-lightbox__severity"
              :style="{ '--severity-color': severityColor }"
            >
              {{ severityLabel }}
            </span>
            <span v-if="confidence != null" class="frame-lightbox__confidence">{{ confidenceLabel }}</span>
          </div>
          <p v-if="description && !displayRegions.length" class="frame-lightbox__description">{{ description }}</p>
          <p class="frame-lightbox__hint muted">
            {{ hasRegions ? 'Tap the glowing highlight to read what the AI found.' : 'No pinpoint overlay on this frame.' }}
          </p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onUnmounted, watch } from 'vue';
import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { IssueCategory } from '@/types/report';
import { resolveApiAssetUrl } from '@/utils/apiAssets';
import { getSeverityColor, SEVERITY_LABELS } from '@/utils/detectionRegions';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';
import DetectionCircleOverlay from '@/components/audit/DetectionCircleOverlay.vue';

const props = withDefaults(
  defineProps<{
    open: boolean;
    imageUrl?: string | null;
    regions?: DetectionRegion[] | null;
    severity?: AuditSuggestionSeverity | null;
    category?: IssueCategory | null;
    description?: string | null;
    confidence?: number | null;
    frameIndex?: number | null;
    framesTotal?: number | null;
    alt?: string;
  }>(),
  {
    imageUrl: null,
    regions: () => [],
    severity: null,
    category: null,
    description: null,
    confidence: null,
    frameIndex: null,
    framesTotal: null,
    alt: 'AI street audit evidence frame',
  },
);

const emit = defineEmits<{
  close: [];
}>();

const resolvedImageUrl = computed(() =>
  props.imageUrl ? resolveApiAssetUrl(props.imageUrl) : null,
);
const displayRegions = computed(() => props.regions ?? []);
const hasRegions = computed(() => displayRegions.value.length > 0);
const severityColor = computed(() => getSeverityColor(props.severity));
const severityLabel = computed(() =>
  props.severity ? SEVERITY_LABELS[props.severity] : '',
);
const categoryLabel = computed(() =>
  props.category ? categoryLabels[props.category] : 'Issue',
);
const confidenceLabel = computed(() =>
  props.confidence == null ? '' : formatConfidence(props.confidence),
);
const frameLabel = computed(() => {
  if (props.frameIndex == null) {
    return null;
  }
  if (props.framesTotal != null) {
    return `Frame ${props.frameIndex + 1} / ${props.framesTotal}`;
  }
  return `Frame ${props.frameIndex + 1}`;
});
const title = computed(() =>
  props.category ? `${categoryLabel.value} evidence` : 'Analyzed frame evidence',
);

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close');
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', onKeydown);
    } else {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', onKeydown);
    }
  },
  { immediate: true },
);

onUnmounted(() => {
  document.body.style.overflow = '';
  window.removeEventListener('keydown', onKeydown);
});
</script>

<style scoped>
.frame-lightbox {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  background: rgba(8, 12, 18, 0.88);
  backdrop-filter: blur(10px);
}

.frame-lightbox__close {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  z-index: 2;
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  font-size: 1.6rem;
  line-height: 1;
  cursor: pointer;
}

.frame-lightbox__panel {
  display: grid;
  gap: var(--space-3);
  width: min(92vw, 68rem);
  max-height: 92vh;
}

.frame-lightbox__stage {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: #0f141d;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45);
  aspect-ratio: 1 / 1;
  max-height: min(72vh, 68rem);
}

.frame-lightbox__image,
.frame-lightbox__placeholder {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #0f141d;
}

.frame-lightbox__placeholder {
  display: grid;
  place-items: center;
  min-height: 20rem;
}

.frame-lightbox__footer {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.frame-lightbox__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.frame-lightbox__frame,
.frame-lightbox__category,
.frame-lightbox__confidence {
  font-size: var(--text-sm);
  font-weight: 800;
}

.frame-lightbox__category {
  text-transform: capitalize;
}

.frame-lightbox__severity {
  padding: 0.2rem 0.6rem;
  border: 1px solid var(--severity-color);
  border-radius: 999px;
  background: color-mix(in srgb, var(--severity-color) 18%, transparent);
  font-size: var(--text-xs);
  font-weight: 800;
  text-transform: capitalize;
}

.frame-lightbox__description {
  margin: 0;
  font-size: var(--text-base);
  line-height: 1.5;
}

.frame-lightbox__hint {
  margin: 0;
  font-size: var(--text-xs);
}
</style>
