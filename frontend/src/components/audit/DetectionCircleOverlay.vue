<template>
  <div class="detection-overlay" :class="{ 'detection-overlay--interactive': interactive }">
    <svg
      class="detection-overlay__svg"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <radialGradient :id="gradientId" cx="50%" cy="50%" r="50%">
          <stop offset="0%" :stop-color="severityColor" stop-opacity="0.45" />
          <stop offset="55%" :stop-color="severityColor" stop-opacity="0.18" />
          <stop offset="100%" :stop-color="severityColor" stop-opacity="0" />
        </radialGradient>
        <filter :id="glowId" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="1.2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <g
        v-for="(region, index) in displayRegions"
        :key="index"
        class="detection-overlay__target"
        :class="{ 'detection-overlay__target--active': activeIndex === index }"
      >
        <circle
          class="detection-overlay__pulse"
          :cx="region.center_x * 100"
          :cy="region.center_y * 100"
          :r="region.radius * 115"
          :stroke="severityColor"
        />
        <circle
          class="detection-overlay__ring"
          :cx="region.center_x * 100"
          :cy="region.center_y * 100"
          :r="region.radius * 100"
          :stroke="severityColor"
          :filter="`url(#${glowId})`"
        />
        <circle
          class="detection-overlay__core"
          :cx="region.center_x * 100"
          :cy="region.center_y * 100"
          :r="region.radius * 88"
          :fill="`url(#${gradientId})`"
          :stroke="severityColor"
        />
        <circle
          class="detection-overlay__reticle"
          :cx="region.center_x * 100"
          :cy="region.center_y * 100"
          r="0.9"
          :fill="severityColor"
          stroke="#fff"
        />
        <line
          class="detection-overlay__crosshair"
          :x1="region.center_x * 100 - region.radius * 28"
          :x2="region.center_x * 100 + region.radius * 28"
          :y1="region.center_y * 100"
          :y2="region.center_y * 100"
          :stroke="severityColor"
        />
        <line
          class="detection-overlay__crosshair"
          :x1="region.center_x * 100"
          :x2="region.center_x * 100"
          :y1="region.center_y * 100 - region.radius * 28"
          :y2="region.center_y * 100 + region.radius * 28"
          :stroke="severityColor"
        />
        <circle
          v-if="interactive"
          class="detection-overlay__hit"
          :cx="region.center_x * 100"
          :cy="region.center_y * 100"
          :r="hitRadius(region)"
          @click.stop="toggleInfo(index)"
        />
      </g>
    </svg>

    <button
      v-if="interactive && displayRegions.length"
      type="button"
      class="detection-overlay__tap-hint"
      :style="primaryHintStyle"
      @click.stop="toggleInfo(0)"
    >
      Tap highlight
    </button>

    <div
      v-if="interactive && activeIndex != null && activeRegion"
      class="detection-overlay__info animate-fade-in"
      :style="infoPanelStyle(activeRegion)"
      role="dialog"
      aria-label="Detection details"
      @click.stop
    >
      <div class="detection-overlay__info-head">
        <span class="detection-overlay__info-badge" :style="{ '--tone': severityColor }">
          {{ severityLabel }}
        </span>
        <button type="button" class="detection-overlay__info-close" @click="activeIndex = null">
          ×
        </button>
      </div>
      <strong class="detection-overlay__info-title">{{ categoryLabel }}</strong>
      <p v-if="confidence != null" class="detection-overlay__info-confidence">
        {{ confidenceLabel }} confidence
      </p>
      <p class="detection-overlay__info-copy">
        {{ description ?? 'The model flagged an issue in this area of the frame.' }}
      </p>
      <p class="detection-overlay__info-note muted">AI-estimated location — approximate, not survey-grade.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { IssueCategory } from '@/types/report';
import {
  getSeverityColor,
  SEVERITY_LABELS,
} from '@/utils/detectionRegions';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';

const props = withDefaults(
  defineProps<{
    regions?: DetectionRegion[] | null;
    severity?: AuditSuggestionSeverity | null;
    category?: IssueCategory | null;
    description?: string | null;
    confidence?: number | null;
    interactive?: boolean;
    overlayId?: string;
  }>(),
  {
    regions: () => [],
    severity: null,
    category: null,
    description: null,
    confidence: null,
    interactive: true,
    overlayId: 'detection',
  },
);

const activeIndex = ref<number | null>(null);

const uid = Math.random().toString(36).slice(2, 8);
const gradientId = computed(() => `detection-grad-${props.overlayId}-${uid}`);
const glowId = computed(() => `detection-glow-${props.overlayId}-${uid}`);

const displayRegions = computed(() => props.regions ?? []);
const activeRegion = computed(() =>
  activeIndex.value == null ? null : displayRegions.value[activeIndex.value] ?? null,
);
const severityColor = computed(() => getSeverityColor(props.severity));
const severityLabel = computed(() =>
  props.severity ? SEVERITY_LABELS[props.severity] : 'Issue',
);
const categoryLabel = computed(() =>
  props.category ? categoryLabels[props.category] : 'Detected issue',
);
const confidenceLabel = computed(() =>
  props.confidence == null ? 'Unknown' : formatConfidence(props.confidence),
);

const primaryRegion = computed(() => displayRegions.value[0] ?? null);
const primaryHintStyle = computed(() => {
  const region = primaryRegion.value;
  if (!region) {
    return {};
  }
  return {
    left: `${clampPercent(region.center_x * 100, 18, 82)}%`,
    top: `${clampPercent(region.center_y * 100 + region.radius * 70, 12, 88)}%`,
  };
});

watch(
  () => props.regions,
  () => {
    activeIndex.value = null;
  },
);

function toggleInfo(index: number) {
  activeIndex.value = activeIndex.value === index ? null : index;
}

function infoPanelStyle(region: DetectionRegion) {
  return {
    left: `${clampPercent(region.center_x * 100, 22, 78)}%`,
    top: `${clampPercent(region.center_y * 100 - region.radius * 95, 10, 62)}%`,
  };
}

function hitRadius(region: DetectionRegion) {
  return Math.max(region.radius * 120, 8);
}

function clampPercent(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}
</script>

<style scoped>
.detection-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.detection-overlay--interactive {
  pointer-events: auto;
}

.detection-overlay__svg {
  width: 100%;
  height: 100%;
}

.detection-overlay__pulse {
  fill: none;
  stroke-width: 0.55;
  vector-effect: non-scaling-stroke;
  opacity: 0.55;
  animation: detection-pulse-ring 2.2s ease-out infinite;
}

.detection-overlay__ring {
  fill: none;
  stroke-width: 0.75;
  stroke-dasharray: 3 2.5;
  vector-effect: non-scaling-stroke;
  opacity: 0.95;
}

.detection-overlay__core {
  stroke-width: 0.65;
  vector-effect: non-scaling-stroke;
}

.detection-overlay__reticle {
  stroke-width: 0.35;
  vector-effect: non-scaling-stroke;
}

.detection-overlay__crosshair {
  stroke-width: 0.35;
  vector-effect: non-scaling-stroke;
  opacity: 0.85;
}

.detection-overlay__hit {
  fill: transparent;
  stroke: transparent;
  cursor: pointer;
  pointer-events: all;
}

.detection-overlay__target--active .detection-overlay__ring {
  stroke-width: 1;
  stroke-dasharray: none;
}

.detection-overlay__target--active .detection-overlay__core {
  stroke-width: 0.9;
}

.detection-overlay__tap-hint {
  position: absolute;
  z-index: 2;
  padding: 0.25rem 0.55rem;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 999px;
  background: rgba(8, 12, 18, 0.72);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  transform: translate(-50%, -50%);
  cursor: pointer;
  pointer-events: all;
}

.detection-overlay__info {
  position: absolute;
  z-index: 3;
  display: grid;
  gap: var(--space-2);
  width: min(16rem, 72%);
  padding: var(--space-3);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: var(--radius-md);
  background: rgba(8, 12, 18, 0.92);
  color: #fff;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  transform: translate(-50%, -100%);
  pointer-events: all;
}

.detection-overlay__info-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.detection-overlay__info-badge {
  padding: 0.15rem 0.55rem;
  border: 1px solid var(--tone);
  border-radius: 999px;
  background: color-mix(in srgb, var(--tone) 20%, transparent);
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
}

.detection-overlay__info-close {
  display: grid;
  place-items: center;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
}

.detection-overlay__info-title {
  font-size: var(--text-sm);
  font-weight: 900;
}

.detection-overlay__info-confidence {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
  font-size: var(--text-xs);
  font-weight: 800;
}

.detection-overlay__info-copy {
  margin: 0;
  font-size: var(--text-sm);
  line-height: 1.45;
}

.detection-overlay__info-note {
  margin: 0;
  font-size: 0.68rem;
  line-height: 1.35;
}

@keyframes detection-pulse-ring {
  0%,
  100% {
    opacity: 0.55;
  }

  50% {
    opacity: 0.12;
  }
}

@media (prefers-reduced-motion: reduce) {
  .detection-overlay__pulse {
    animation: none;
    opacity: 0.35;
  }
}
</style>
