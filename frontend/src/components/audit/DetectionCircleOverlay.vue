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
          <stop offset="0%" :stop-color="severityColor" stop-opacity="0.55" />
          <stop offset="50%" :stop-color="severityColor" stop-opacity="0.22" />
          <stop offset="100%" :stop-color="severityColor" stop-opacity="0" />
        </radialGradient>
        <filter :id="glowId" x="-120%" y="-120%" width="340%" height="340%">
          <feGaussianBlur stdDeviation="3.5" result="blur1" />
          <feGaussianBlur stdDeviation="1.2" result="blur2" />
          <feMerge>
            <feMergeNode in="blur1" />
            <feMergeNode in="blur2" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter :id="`${glowId}-soft`" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="1.8" result="blur" />
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
          class="detection-overlay__pulse-outer"
          :cx="region.center_x * 100"
          :cy="region.center_y * 100"
          :r="region.radius * 130"
          :stroke="severityColor"
        />
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
          :filter="`url(#${glowId}-soft)`"
        />
        <circle
          class="detection-overlay__reticle"
          :cx="region.center_x * 100"
          :cy="region.center_y * 100"
          r="1.1"
          :fill="severityColor"
          stroke="#fff"
          stroke-width="0.4"
        />
        <line
          class="detection-overlay__crosshair"
          :x1="region.center_x * 100 - region.radius * 32"
          :x2="region.center_x * 100 + region.radius * 32"
          :y1="region.center_y * 100"
          :y2="region.center_y * 100"
          :stroke="severityColor"
          :filter="`url(#${glowId}-soft)`"
        />
        <line
          class="detection-overlay__crosshair"
          :x1="region.center_x * 100"
          :x2="region.center_x * 100"
          :y1="region.center_y * 100 - region.radius * 32"
          :y2="region.center_y * 100 + region.radius * 32"
          :stroke="severityColor"
          :filter="`url(#${glowId}-soft)`"
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

    <div
      v-if="interactive && activeIndex != null && activeRegion"
      class="detection-overlay__info animate-fade-in"
      :style="{ '--tone': severityColor, ...infoPanelStyle(activeRegion) }"
      role="dialog"
      aria-label="Detection details"
      @click.stop
    >
      <div class="detection-overlay__info-accent" :style="{ background: severityColor }" />

      <div class="detection-overlay__info-head">
        <span class="detection-overlay__info-badge">{{ severityLabel }}</span>
        <button type="button" class="detection-overlay__info-close" aria-label="Close" @click="activeIndex = null">
          <svg viewBox="0 0 16 16" fill="none" width="10" height="10" aria-hidden="true">
            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <strong class="detection-overlay__info-title">{{ categoryLabel }}</strong>

      <div v-if="confidence != null" class="detection-overlay__info-conf">
        <div class="detection-overlay__info-conf-track">
          <span
            class="detection-overlay__info-conf-fill"
            :style="{ width: `${confidence * 100}%`, background: severityColor }"
          />
        </div>
        <span class="detection-overlay__info-conf-val">{{ confidenceLabel }}</span>
      </div>

      <p class="detection-overlay__info-copy">
        {{ description ?? 'The model flagged an issue in this area of the frame.' }}
      </p>

      <p class="detection-overlay__info-note">
        AI-estimated location — approximate, not survey-grade.
      </p>
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

watch(
  () => props.regions,
  () => { activeIndex.value = null; },
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

/* ─── Circles ─── */
.detection-overlay__pulse-outer {
  fill: none;
  stroke-width: 0.4;
  vector-effect: non-scaling-stroke;
  opacity: 0.3;
  animation: detection-pulse-outer 2.8s ease-out infinite;
}

.detection-overlay__pulse {
  fill: none;
  stroke-width: 0.6;
  vector-effect: non-scaling-stroke;
  opacity: 0.6;
  animation: detection-pulse-ring 2.2s ease-out infinite;
}

.detection-overlay__ring {
  fill: none;
  stroke-width: 0.9;
  stroke-dasharray: 3.5 2;
  vector-effect: non-scaling-stroke;
  opacity: 1;
}

.detection-overlay__core {
  stroke-width: 0.7;
  vector-effect: non-scaling-stroke;
}

.detection-overlay__reticle {
  vector-effect: non-scaling-stroke;
  animation: detection-pulse-dot 2.2s ease-in-out infinite;
}

.detection-overlay__crosshair {
  stroke-width: 0.45;
  vector-effect: non-scaling-stroke;
  opacity: 0.9;
}

.detection-overlay__hit {
  fill: transparent;
  stroke: transparent;
  cursor: pointer;
  pointer-events: all;
}

.detection-overlay__target--active .detection-overlay__ring {
  stroke-width: 1.2;
  stroke-dasharray: none;
}

.detection-overlay__target--active .detection-overlay__core {
  stroke-width: 1;
}

/* ─── Info popup ─── */
.detection-overlay__info {
  position: absolute;
  z-index: 3;
  display: grid;
  gap: var(--space-2);
  width: min(15rem, 74%);
  border: 1px solid color-mix(in srgb, var(--tone) 45%, rgba(255, 255, 255, 0.08));
  border-radius: var(--radius-md);
  background: rgba(4, 6, 10, 0.96);
  color: #fff;
  backdrop-filter: blur(16px) saturate(1.4);
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--tone) 28%, transparent),
    0 0 28px color-mix(in srgb, var(--tone) 38%, transparent),
    0 0 60px color-mix(in srgb, var(--tone) 18%, transparent),
    0 28px 56px rgba(0, 0, 0, 0.7);
  transform: translate(-50%, -100%);
  pointer-events: all;
  overflow: hidden;
}

.detection-overlay__info-accent {
  height: 3px;
  width: 100%;
  margin-bottom: calc(var(--space-2) * -1 + 2px);
  opacity: 0.9;
  box-shadow: 0 0 10px currentColor;
}

.detection-overlay__info-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-3) 0;
}

.detection-overlay__info-badge {
  padding: 0.18rem 0.6rem;
  border: 1px solid color-mix(in srgb, var(--tone) 55%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--tone) 22%, transparent);
  color: color-mix(in srgb, var(--tone) 90%, #fff);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detection-overlay__info-close {
  display: grid;
  place-items: center;
  width: 1.4rem;
  height: 1.4rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: background var(--motion-fast) ease, color var(--motion-fast) ease;
  flex-shrink: 0;
}

.detection-overlay__info-close:hover {
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
}

.detection-overlay__info-title {
  padding: 0 var(--space-3);
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: #fff;
}

.detection-overlay__info-conf {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0 var(--space-3);
}

.detection-overlay__info-conf-track {
  flex: 1;
  height: 3px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.detection-overlay__info-conf-fill {
  display: block;
  height: 100%;
  border-radius: 999px;
  box-shadow: 0 0 6px currentColor;
}

.detection-overlay__info-conf-val {
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.detection-overlay__info-copy {
  margin: 0;
  padding: 0 var(--space-3);
  color: rgba(255, 255, 255, 0.75);
  font-size: var(--text-xs);
  line-height: 1.5;
}

.detection-overlay__info-note {
  margin: 0;
  padding: var(--space-2) var(--space-3) var(--space-3);
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.6rem;
  line-height: 1.35;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

/* ─── Animations ─── */
@keyframes detection-pulse-outer {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0; transform: scale(1.06); }
}

@keyframes detection-pulse-ring {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.1; }
}

@keyframes detection-pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (prefers-reduced-motion: reduce) {
  .detection-overlay__pulse,
  .detection-overlay__pulse-outer,
  .detection-overlay__reticle {
    animation: none;
  }
}
</style>
