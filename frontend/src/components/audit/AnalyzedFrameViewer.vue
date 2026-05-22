<template>
  <section
    class="analyzed-frame-viewer"
    :class="`analyzed-frame-viewer--${layout}`"
    :aria-label="ariaLabel"
  >
    <div class="analyzed-frame-viewer__layout">
      <div
        class="analyzed-frame-viewer__media"
      >
        <img
          v-if="resolvedImageUrl"
          :src="resolvedImageUrl"
          :alt="alt"
          class="analyzed-frame-viewer__image"
          loading="lazy"
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
      </div>

      <div class="analyzed-frame-viewer__summary">
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
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
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
    layout?: 'compact' | 'detail' | 'scanner';
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
    alt: 'AI street audit analyzed frame',
    ariaLabel: 'Analyzed street audit frame with severity overlay',
  },
);

const resolvedImageUrl = computed(() =>
  props.imageUrl ? resolveApiAssetUrl(props.imageUrl) : null,
);

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
</style>
