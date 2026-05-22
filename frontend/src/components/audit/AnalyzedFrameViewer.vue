<template>
  <AppCard class="analyzed-frame-viewer stack" variant="command">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
        <p class="analyzed-frame-viewer__subtitle">{{ subtitle }}</p>
      </div>
      <div class="cluster">
        <AppBadge v-if="severity" :tone="severityBadgeTone">
          {{ severityLabel }}
        </AppBadge>
        <AppBadge v-if="hasRegions" tone="source-ai-audit">AI-estimated location</AppBadge>
        <AppBadge v-else-if="showMissingRegionBadge" tone="warning">Location not pinpointed</AppBadge>
      </div>
    </div>

    <AppCard v-if="imageError" class="analyzed-frame-viewer__fallback stack" variant="inset">
      <AppBadge tone="danger">Image unavailable</AppBadge>
      <p>{{ imageError }}</p>
    </AppCard>

    <div
      v-else-if="resolvedImageUrl"
      class="analyzed-frame-viewer__stage"
      @mouseleave="clearActiveRegion"
    >
      <img
        :alt="imageAlt"
        class="analyzed-frame-viewer__image"
        :src="resolvedImageUrl"
        @error="handleImageError"
        @load="handleImageLoad"
      />

      <SeverityRegionOverlay
        v-if="hasRegions && imageLoaded"
        :active-index="activeRegionIndex"
        :ariaLabel="regionAriaLabel"
        :regions="regions"
        :severity="severity"
        :variant="overlayVariant"
        @clear-active="clearActiveRegion"
        @set-active="setActiveRegion"
      />

      <div
        v-if="activeTooltip && activeRegionIndex !== null"
        class="analyzed-frame-viewer__tooltip"
        role="tooltip"
        :style="activeTooltipStyle"
      >
        <strong>{{ activeTooltip.title }}</strong>
        <p>{{ activeTooltip.body }}</p>
      </div>

      <div v-if="!imageLoaded" class="analyzed-frame-viewer__loading" role="status">
        Loading analyzed frame...
      </div>
    </div>

    <AppCard v-else class="analyzed-frame-viewer__fallback stack" variant="muted">
      <AppBadge tone="warning">No analyzed frame</AppBadge>
      <p>
        This suggestion does not include a proxied Street View frame yet. Run a new audit to
        capture analyzed frame evidence.
      </p>
    </AppCard>

    <SeverityLegend v-if="hasRegions" :variant="overlayVariant" />

    <dl class="analyzed-frame-viewer__meta">
      <div v-if="frameIndex !== null && frameIndex !== undefined">
        <dt>Frame</dt>
        <dd>#{{ frameIndex + 1 }}</dd>
      </div>
      <div v-if="heading !== null && heading !== undefined">
        <dt>Heading</dt>
        <dd>{{ heading }}°</dd>
      </div>
      <div v-if="pitch !== null && pitch !== undefined">
        <dt>Pitch</dt>
        <dd>{{ pitch }}°</dd>
      </div>
      <div>
        <dt>Confidence</dt>
        <dd>{{ formatConfidence(confidence) }}</dd>
      </div>
      <div v-if="categoryLabel">
        <dt>Category</dt>
        <dd>{{ categoryLabel }}</dd>
      </div>
    </dl>

    <p v-if="description" class="analyzed-frame-viewer__description">{{ description }}</p>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import SeverityLegend from '@/components/audit/SeverityLegend.vue';
import SeverityRegionOverlay from '@/components/audit/SeverityRegionOverlay.vue';
import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { IssueCategory } from '@/types/report';
import {
  buildRegionTooltipContent,
  DEFAULT_REGION_OVERLAY_VARIANT,
  formatSeverityLabel,
  getSeverityBadgeTone,
  regionOverlayPosition,
  resolveApiAssetUrl,
  type RegionOverlayVariant,
} from '@/utils/detectionRegions';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';

const props = withDefaults(
  defineProps<{
    imageUrl?: string | null;
    regions?: DetectionRegion[] | null;
    severity?: AuditSuggestionSeverity | null;
    category?: IssueCategory | null;
    description?: string | null;
    confidence?: number;
    frameIndex?: number | null;
    heading?: number | null;
    pitch?: number | null;
    eyebrow?: string;
    title?: string;
    subtitle?: string;
    showMissingRegionBadge?: boolean;
    overlayVariant?: RegionOverlayVariant;
  }>(),
  {
    imageUrl: null,
    regions: null,
    severity: null,
    category: null,
    description: null,
    confidence: 0,
    frameIndex: null,
    heading: null,
    pitch: null,
    eyebrow: 'Analyzed frame evidence',
    title: 'What the AI analyzed',
    subtitle: 'Exact Street View frame sent to the vision model, with severity overlay when available.',
    showMissingRegionBadge: true,
    overlayVariant: DEFAULT_REGION_OVERLAY_VARIANT,
  },
);

const imageLoaded = ref(false);
const imageError = ref<string | null>(null);
const activeRegionIndex = ref<number | null>(null);

const resolvedImageUrl = computed(() => resolveApiAssetUrl(props.imageUrl));
const regions = computed(() => props.regions ?? []);
const hasRegions = computed(() => regions.value.length > 0);
const severityBadgeTone = computed(() => getSeverityBadgeTone(props.severity));
const severityLabel = computed(() => formatSeverityLabel(props.severity));
const categoryLabel = computed(() =>
  props.category ? categoryLabels[props.category] : null,
);
const imageAlt = computed(() => {
  const category = categoryLabel.value ?? 'street issue';
  return `Analyzed Street View frame showing ${category}`;
});
const regionAriaLabel = computed(() => {
  const tooltip = buildRegionTooltipContent({
    category: categoryLabel.value,
    confidence: props.confidence,
    description: props.description,
    severity: props.severity,
  });
  return `${tooltip.title}. ${tooltip.body}`;
});
const activeTooltip = computed(() => {
  if (activeRegionIndex.value === null) {
    return null;
  }

  return buildRegionTooltipContent({
    category: categoryLabel.value,
    confidence: props.confidence,
    description: props.description,
    severity: props.severity,
  });
});
const activeTooltipStyle = computed(() => {
  if (activeRegionIndex.value === null) {
    return undefined;
  }

  const region = regions.value[activeRegionIndex.value];
  if (!region) {
    return undefined;
  }

  const position = regionOverlayPosition(region);
  return {
    left: `${position.centerXPercent}%`,
    top: `${position.centerYPercent}%`,
  };
});

watch(
  () => props.imageUrl,
  () => {
    imageLoaded.value = false;
    imageError.value = null;
    activeRegionIndex.value = null;
  },
);

function setActiveRegion(index: number) {
  activeRegionIndex.value = index;
}

function clearActiveRegion() {
  activeRegionIndex.value = null;
}

function handleImageLoad() {
  imageLoaded.value = true;
  imageError.value = null;
}

function handleImageError() {
  imageLoaded.value = false;
  imageError.value = 'Could not load the proxied Street View frame from the backend.';
}
</script>

<style scoped>
.analyzed-frame-viewer__subtitle,
.analyzed-frame-viewer__description {
  color: var(--text-secondary);
}

.analyzed-frame-viewer__stage {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  aspect-ratio: 1 / 1;
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.04), rgba(15, 23, 42, 0.08)),
    var(--surface-muted);
}

.analyzed-frame-viewer__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.analyzed-frame-viewer__tooltip {
  position: absolute;
  z-index: 2;
  max-width: min(18rem, 80%);
  padding: var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-sm);
  background: rgba(15, 23, 42, 0.92);
  color: #fff;
  pointer-events: none;
  transform: translate(-50%, calc(-100% - 0.75rem));
}

.analyzed-frame-viewer__tooltip strong {
  display: block;
  margin-bottom: var(--space-1);
}

.analyzed-frame-viewer__tooltip p {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  font-size: var(--text-sm);
}

.analyzed-frame-viewer__loading {
  position: absolute;
  inset: auto 0 0;
  padding: var(--space-3);
  color: var(--text-primary);
  background: linear-gradient(180deg, transparent, rgba(15, 23, 42, 0.72));
  font-weight: 700;
}

.analyzed-frame-viewer__meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: var(--space-3);
  margin: 0;
}

.analyzed-frame-viewer__meta > div {
  display: grid;
  gap: var(--space-1);
}

.analyzed-frame-viewer__meta dt {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.analyzed-frame-viewer__meta dd {
  margin: 0;
  color: var(--text-primary);
  font-weight: 750;
}

.analyzed-frame-viewer__fallback p {
  color: var(--text-secondary);
}
</style>
