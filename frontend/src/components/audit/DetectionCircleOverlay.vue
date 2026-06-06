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
      :class="severity ? `detection-overlay__info--${severity}` : null"
      :style="{ '--tone': severityColor, ...infoPanelStyle(activeRegion) }"
      role="dialog"
      aria-label="Detection details"
      @click.stop
    >
      <span class="detection-overlay__info-pointer" aria-hidden="true" />

      <div class="detection-overlay__info-shell">
        <header class="detection-overlay__info-head">
          <span class="detection-overlay__info-badge">{{ severityLabel }}</span>
          <button type="button" class="detection-overlay__info-close" aria-label="Close" @click="activeIndex = null">
            <svg viewBox="0 0 16 16" fill="none" width="11" height="11" aria-hidden="true">
              <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>
        </header>

        <div class="detection-overlay__info-main">
          <h3 class="detection-overlay__info-title">{{ categoryLabel }}</h3>
          <div v-if="confidence != null" class="detection-overlay__info-score" aria-label="Model confidence">
            <span class="detection-overlay__info-score-value">{{ confidenceLabel }}</span>
            <span class="detection-overlay__info-score-label">confidence</span>
          </div>
        </div>

        <div v-if="confidence != null" class="detection-overlay__info-meter" aria-hidden="true">
          <span
            class="detection-overlay__info-meter-fill"
            :style="{ width: `${confidence * 100}%` }"
          />
        </div>

        <p class="detection-overlay__info-copy">
          {{ description ?? 'The model flagged an issue in this area of the frame.' }}
        </p>

        <footer class="detection-overlay__info-foot">
          <svg class="detection-overlay__info-foot-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <circle cx="8" cy="8" r="6.25" stroke="currentColor" stroke-width="1.2" />
            <path d="M8 7.2v3.6M8 5.4h.01" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
          </svg>
          <span>AI-estimated location — approximate, not survey-grade.</span>
        </footer>
      </div>
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
  --info-bg: rgba(8, 12, 10, 0.92);
  --info-border: color-mix(in srgb, var(--tone) 32%, rgba(255, 255, 255, 0.1));

  position: absolute;
  z-index: 3;
  width: min(16.5rem, 78%);
  transform: translate(-50%, calc(-100% - 0.65rem));
  pointer-events: all;
  filter: drop-shadow(0 16px 32px rgba(0, 0, 0, 0.45));
}

.detection-overlay__info-pointer {
  position: absolute;
  left: 50%;
  bottom: -0.35rem;
  width: 0.7rem;
  height: 0.7rem;
  border-right: 1px solid var(--info-border);
  border-bottom: 1px solid var(--info-border);
  background: var(--info-bg);
  transform: translateX(-50%) rotate(45deg);
}

.detection-overlay__info-shell {
  display: grid;
  gap: 0.55rem;
  padding: 0.7rem 0.8rem 0.75rem;
  border: 1px solid var(--info-border);
  border-radius: calc(var(--radius-md) + 2px);
  background:
    linear-gradient(145deg, color-mix(in srgb, var(--tone) 10%, transparent), transparent 42%),
    var(--info-bg);
  color: #fff;
  backdrop-filter: blur(18px) saturate(1.35);
  -webkit-backdrop-filter: blur(18px) saturate(1.35);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 0 0 1px rgba(0, 0, 0, 0.22),
    0 0 24px color-mix(in srgb, var(--tone) 22%, transparent);
}

.detection-overlay__info-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.detection-overlay__info-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.35rem;
  padding: 0.15rem 0.55rem;
  border: 1px solid color-mix(in srgb, var(--tone) 48%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--tone) 18%, rgba(255, 255, 255, 0.04));
  color: color-mix(in srgb, var(--tone) 82%, #fff);
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.detection-overlay__info-close {
  display: grid;
  place-items: center;
  width: 1.5rem;
  height: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.62);
  cursor: pointer;
  transition:
    background var(--motion-fast) ease,
    color var(--motion-fast) ease,
    border-color var(--motion-fast) ease;
  flex-shrink: 0;
}

.detection-overlay__info-close:hover {
  border-color: rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.detection-overlay__info-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.65rem;
}

.detection-overlay__info-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.15;
  color: #fff;
}

.detection-overlay__info-score {
  display: grid;
  justify-items: end;
  gap: 0.05rem;
  flex-shrink: 0;
  padding-left: 0.35rem;
}

.detection-overlay__info-score-value {
  font-size: 0.95rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  line-height: 1;
  color: color-mix(in srgb, var(--tone) 75%, #fff);
}

.detection-overlay__info-score-label {
  color: rgba(255, 255, 255, 0.42);
  font-size: 0.52rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detection-overlay__info-meter {
  height: 0.22rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.detection-overlay__info-meter-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--tone) 70%, #fff),
    var(--tone)
  );
  box-shadow: 0 0 10px color-mix(in srgb, var(--tone) 55%, transparent);
}

.detection-overlay__info-copy {
  margin: 0;
  padding: 0.45rem 0.5rem;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.68rem;
  line-height: 1.5;
}

.detection-overlay__info-foot {
  display: flex;
  align-items: flex-start;
  gap: 0.35rem;
  margin-top: 0.1rem;
  padding-top: 0.45rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.38);
  font-size: 0.56rem;
  line-height: 1.4;
}

.detection-overlay__info-foot-icon {
  width: 0.75rem;
  height: 0.75rem;
  margin-top: 0.05rem;
  flex-shrink: 0;
  opacity: 0.75;
}

.detection-overlay__info--medium {
  --info-bg: rgba(12, 10, 6, 0.92);
}

.detection-overlay__info--high,
.detection-overlay__info--critical {
  --info-bg: rgba(14, 8, 8, 0.94);
}

@media (max-width: 640px) {
  .detection-overlay__info {
    width: min(15rem, 86%);
  }

  .detection-overlay__info-copy {
    font-size: 0.64rem;
  }
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
