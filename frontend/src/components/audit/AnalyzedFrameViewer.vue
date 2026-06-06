<template>
  <section
    class="analyzed-frame-viewer"
    :class="`analyzed-frame-viewer--${layout}`"
    :aria-label="ariaLabel"
  >
    <div class="analyzed-frame-viewer__layout">
      <div
        ref="mediaRef"
        class="analyzed-frame-viewer__media"
        :class="{
          'analyzed-frame-viewer__media--zoomable': zoomable,
          'analyzed-frame-viewer__media--loading': imageLoading && resolvedImageUrl,
        }"
        :role="zoomable ? 'button' : undefined"
        :tabindex="zoomable ? 0 : undefined"
        :aria-label="zoomable ? 'View photo fullscreen' : undefined"
        @click="zoomable ? openZoom() : undefined"
        @keydown.enter.prevent="zoomable ? openZoom() : undefined"
        @keydown.space.prevent="zoomable ? openZoom() : undefined"
      >
        <img
          v-if="resolvedImageUrl"
          :key="resolvedImageUrl"
          :src="resolvedImageUrl"
          :alt="alt"
          class="analyzed-frame-viewer__image"
          :loading="layout === 'scanner' ? 'eager' : 'lazy'"
          @load="handleImageReady"
          @error="handleImageReady"
        />
        <div v-else class="analyzed-frame-viewer__placeholder muted">No frame image</div>

        <DetectionCircleOverlay
          v-if="resolvedImageUrl && displayRegions.length"
          overlay-id="viewer"
          :category="category ?? undefined"
          :confidence="confidence ?? undefined"
          :description="description ?? undefined"
          :interactive="layout === 'detail' || layout === 'scanner'"
          :regions="displayRegions"
          :severity="severity ?? undefined"
        />

        <div v-if="layout === 'inspector'" class="analyzed-frame-viewer__hud">
          <span
            v-if="severity"
            class="analyzed-frame-viewer__hud-severity"
            :class="`analyzed-frame-viewer__hud-severity--${severity}`"
          >
            {{ severityLabel }}
          </span>
          <span v-if="confidence != null" class="analyzed-frame-viewer__hud-confidence">
            {{ confidenceLabel }}
          </span>
        </div>

        <button
          v-if="zoomable && resolvedImageUrl"
          type="button"
          class="analyzed-frame-viewer__expand"
          aria-label="Open fullscreen photo"
          @click.stop="openZoom"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M9 3H5a2 2 0 00-2 2v4M15 3h4a2 2 0 012 2v4M9 21H5a2 2 0 01-2-2v-4M15 21h4a2 2 0 002-2v-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <div
        v-if="layout !== 'scanner' && layout !== 'inspector'"
        class="analyzed-frame-viewer__summary"
      >
        <div class="analyzed-frame-viewer__title-row">
          <p class="analyzed-frame-viewer__title">
            {{ frameLabel ?? 'Analyzed frame' }}
          </p>
          <span
            v-if="severity"
            class="analyzed-frame-viewer__severity"
            :class="`analyzed-frame-viewer__severity--${severity}`"
          >
            {{ severityLabel }}
          </span>
        </div>

        <p v-if="category || confidence != null" class="analyzed-frame-viewer__facts">
          <span v-if="category">{{ categoryLabel }}</span>
          <span v-if="category && confidence != null"> · </span>
          <span v-if="confidence != null">{{ confidenceLabel }}</span>
        </p>

        <p v-if="description" class="analyzed-frame-viewer__description">
          {{ description }}
        </p>

        <p class="analyzed-frame-viewer__hint muted">
          <AppBadge v-if="showMissingRegionsBadge" tone="warning">Location not pinpointed</AppBadge>
          <template v-else>
            {{ hasRegions ? 'Tap the highlight for AI finding details.' : 'No pinpoint overlay for this frame.' }}
          </template>
        </p>
        <p v-if="hasRegions || showMissingRegionsBadge" class="analyzed-frame-viewer__disclaimer muted">
          AI-estimated location
        </p>

        <dl v-if="showMetadata && metaItems.length" class="analyzed-frame-viewer__meta">
          <div v-for="item in metaItems" :key="item.label">
            <dt>{{ item.label }}</dt>
            <dd>{{ item.value }}</dd>
          </div>
        </dl>
      </div>
    </div>

    <AnalyzedFrameLightbox
      :open="zoomOpen"
      :origin-rect="zoomOrigin"
      :image-url="imageUrl"
      :regions="regions"
      :severity="severity"
      :category="category"
      :description="description"
      :confidence="confidence"
      :frame-index="frameIndex"
      :frames-total="framesTotal"
      :alt="alt"
      @close="closeZoom"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AnalyzedFrameLightbox, { type LightboxOriginRect } from '@/components/audit/AnalyzedFrameLightbox.vue';
import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { IssueCategory } from '@/types/report';
import { resolveApiAssetUrl } from '@/utils/apiAssets';
import AppBadge from '@/components/common/AppBadge.vue';
import DetectionCircleOverlay from '@/components/audit/DetectionCircleOverlay.vue';
import {
  SEVERITY_LABELS,
} from '@/utils/detectionRegions';
import { categoryLabels, formatConfidence, formatCoordinates } from '@/utils/reportFormatting';

const props = withDefaults(
  defineProps<{
    imageUrl?: string | null;
    regions?: DetectionRegion[] | null;
    severity?: AuditSuggestionSeverity | null;
    category?: IssueCategory | null;
    description?: string | null;
    confidence?: number | null;
    frameIndex?: number | null;
    framesTotal?: number | null;
    heading?: number | null;
    pitch?: number | null;
    latitude?: number;
    longitude?: number;
    alt?: string;
    showMetadata?: boolean;
    layout?: 'compact' | 'detail' | 'scanner' | 'inspector';
    zoomable?: boolean;
    isCivicIssue?: boolean;
    ariaLabel?: string;
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
    heading: null,
    pitch: null,
    showMetadata: false,
    layout: 'compact',
    zoomable: undefined,
    alt: 'AI street audit analyzed frame',
    ariaLabel: 'Analyzed street audit frame with severity overlay',
  },
);

const emit = defineEmits<{
  'image-loading': [];
  'image-loaded': [];
}>();

const mediaRef = ref<HTMLElement | null>(null);
const zoomOpen = ref(false);
const zoomOrigin = ref<LightboxOriginRect | null>(null);
const imageLoading = ref(false);

const zoomable = computed(() => {
  if (props.zoomable != null) {
    return props.zoomable;
  }
  return props.layout === 'inspector';
});

function openZoom() {
  if (!resolvedImageUrl.value || !zoomable.value) {
    return;
  }
  zoomOrigin.value = mediaRef.value?.getBoundingClientRect() ?? null;
  zoomOpen.value = true;
}

function closeZoom() {
  zoomOpen.value = false;
}

const resolvedImageUrl = computed(() =>
  props.imageUrl ? resolveApiAssetUrl(props.imageUrl) : null,
);

watch(
  resolvedImageUrl,
  (url) => {
    if (!url) {
      imageLoading.value = false;
      emit('image-loaded');
      return;
    }
    imageLoading.value = true;
    emit('image-loading');
  },
  { immediate: true },
);

function handleImageReady() {
  imageLoading.value = false;
  emit('image-loaded');
}

const displayRegions = computed(() => props.regions ?? []);
const hasRegions = computed(() => displayRegions.value.length > 0);
const showMissingRegionsBadge = computed(
  () => Boolean(props.isCivicIssue) && !hasRegions.value,
);
const severityLabel = computed(() =>
  props.severity ? SEVERITY_LABELS[props.severity] : '',
);
const categoryLabel = computed(() =>
  props.category ? categoryLabels[props.category] : 'Detected issue',
);
const confidenceLabel = computed(() =>
  props.confidence == null ? 'Confidence unavailable' : formatConfidence(props.confidence),
);
const frameLabel = computed(() => {
  if (props.frameIndex == null) {
    return null;
  }
  if (props.framesTotal != null) {
    return `Frame ${props.frameIndex + 1} of ${props.framesTotal}`;
  }
  return `Frame ${props.frameIndex + 1}`;
});

const metaItems = computed(() => {
  const items: Array<{ label: string; value: string }> = [];

  if (props.heading != null) {
    items.push({ label: 'Heading', value: `${props.heading}°` });
  }
  if (props.pitch != null) {
    items.push({ label: 'Pitch', value: `${props.pitch}°` });
  }
  if (props.latitude != null && props.longitude != null) {
    items.push({
      label: 'Location',
      value: formatCoordinates(props.latitude, props.longitude),
    });
  }

  return items;
});
</script>

<style scoped>
.analyzed-frame-viewer__layout {
  display: grid;
  grid-template-columns: minmax(0, 11.5rem) minmax(0, 1fr);
  gap: var(--space-4);
  align-items: start;
}

.analyzed-frame-viewer--detail .analyzed-frame-viewer__layout {
  grid-template-columns: minmax(0, 16rem) minmax(0, 1fr);
}

.analyzed-frame-viewer__media {
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: 16rem;
  border-radius: var(--radius-md);
  background: var(--surface-map-placeholder);
  aspect-ratio: 4 / 3;
}

.analyzed-frame-viewer--detail .analyzed-frame-viewer__media {
  max-width: 18rem;
}

.analyzed-frame-viewer__image,
.analyzed-frame-viewer__placeholder {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.analyzed-frame-viewer__placeholder {
  display: grid;
  place-items: center;
  min-height: 8rem;
  font-size: var(--text-sm);
}

.analyzed-frame-viewer__summary {
  display: grid;
  gap: var(--space-2);
  min-width: 0;
  padding-top: var(--space-1);
}

.analyzed-frame-viewer__title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.analyzed-frame-viewer__title {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 850;
}

.analyzed-frame-viewer__severity {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  font-size: var(--text-xs);
  font-weight: 800;
  text-transform: capitalize;
}

.analyzed-frame-viewer__severity--low {
  border: 1px solid #22c55e;
  background: rgba(34, 197, 94, 0.12);
}

.analyzed-frame-viewer__severity--medium {
  border: 1px solid #eab308;
  background: rgba(234, 179, 8, 0.12);
}

.analyzed-frame-viewer__severity--high,
.analyzed-frame-viewer__severity--critical {
  border: 1px solid #ef4444;
  background: rgba(239, 68, 68, 0.12);
}

.analyzed-frame-viewer__facts {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 750;
}

.analyzed-frame-viewer__description {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-sm);
  line-height: 1.45;
}

.analyzed-frame-viewer--inspector .analyzed-frame-viewer__layout {
  grid-template-columns: 1fr;
}

.analyzed-frame-viewer--inspector .analyzed-frame-viewer__media {
  max-width: none;
  width: 100%;
  aspect-ratio: 4 / 5;
  min-height: 6.5rem;
  border-radius: var(--radius-md);
}

.analyzed-frame-viewer__media--loading .analyzed-frame-viewer__image {
  opacity: 0.35;
  filter: blur(2px);
}

.analyzed-frame-viewer__media--loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    110deg,
    transparent 0%,
    rgba(255, 255, 255, 0.08) 45%,
    transparent 90%
  );
  animation: analyzed-frame-shimmer 1.1s ease-in-out infinite;
  pointer-events: none;
}

@keyframes analyzed-frame-shimmer {
  from {
    transform: translateX(-120%);
  }
  to {
    transform: translateX(120%);
  }
}

.analyzed-frame-viewer__media--zoomable {
  cursor: zoom-in;
}

.analyzed-frame-viewer__media--zoomable:focus-visible {
  outline: 2px solid color-mix(in srgb, var(--color-municipal-green) 55%, transparent);
  outline-offset: 2px;
}

.analyzed-frame-viewer__expand {
  position: absolute;
  top: 0.35rem;
  right: 0.35rem;
  z-index: 2;
  display: grid;
  place-items: center;
  width: 1.65rem;
  height: 1.65rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: var(--radius-md);
  background: rgba(8, 12, 10, 0.55);
  color: #fff;
  cursor: pointer;
  backdrop-filter: blur(8px);
  opacity: 0.78;
  transform: scale(1);
  transition:
    opacity var(--motion-fast) ease,
    transform var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.analyzed-frame-viewer__media--zoomable:hover .analyzed-frame-viewer__expand,
.analyzed-frame-viewer__expand:focus-visible {
  opacity: 1;
  transform: scale(1.06);
}

.analyzed-frame-viewer__expand:hover {
  background: rgba(8, 12, 10, 0.82);
}

.analyzed-frame-viewer__hud {
  position: absolute;
  inset: auto 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.45rem 0.4rem;
  background: linear-gradient(180deg, transparent, rgba(8, 12, 10, 0.82));
  pointer-events: none;
}

.analyzed-frame-viewer__hud-severity,
.analyzed-frame-viewer__hud-confidence {
  display: inline-flex;
  align-items: center;
  padding: 0.12rem 0.42rem;
  border-radius: 999px;
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  backdrop-filter: blur(6px);
}

.analyzed-frame-viewer__hud-severity {
  text-transform: capitalize;
}

.analyzed-frame-viewer__hud-severity--low {
  background: rgba(34, 197, 94, 0.88);
  color: #fff;
}

.analyzed-frame-viewer__hud-severity--medium {
  background: rgba(234, 179, 8, 0.92);
  color: #1a1408;
}

.analyzed-frame-viewer__hud-severity--high,
.analyzed-frame-viewer__hud-severity--critical {
  background: rgba(239, 68, 68, 0.9);
  color: #fff;
}

.analyzed-frame-viewer__hud-confidence {
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.analyzed-frame-viewer--scanner .analyzed-frame-viewer__layout {
  grid-template-columns: 1fr;
}

.analyzed-frame-viewer--scanner .analyzed-frame-viewer__media {
  max-width: none;
  aspect-ratio: 4 / 3;
}

.analyzed-frame-viewer__disclaimer {
  margin: 0;
  font-size: var(--text-xs);
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.analyzed-frame-viewer__hint {
  margin: 0;
  font-size: var(--text-xs);
  line-height: 1.4;
}

.analyzed-frame-viewer__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
  margin: var(--space-1) 0 0;
  padding-top: var(--space-2);
  border-top: var(--border-soft);
}

.analyzed-frame-viewer__meta > div {
  display: grid;
  gap: 0.1rem;
}

dt {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

dd {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 700;
}

@media (max-width: 640px) {
  .analyzed-frame-viewer__layout,
  .analyzed-frame-viewer--detail .analyzed-frame-viewer__layout {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }

  .analyzed-frame-viewer__media,
  .analyzed-frame-viewer--detail .analyzed-frame-viewer__media {
    max-width: none;
  }
}
</style>
