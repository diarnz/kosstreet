<template>
  <div
    class="expand-report-card"
    :class="{
      'expand-report-card--expanded': isExpanded,
      'expand-report-card--selected': selected,
      'expand-report-card--hovered': isHovered,
    }"
    role="listitem"
    tabindex="0"
    :aria-pressed="selected"
    :aria-expanded="isExpanded"
    :aria-label="`Select ${run.route_name} audit run`"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <div class="expand-report-card__surface">
      <div class="expand-report-card__gradient" aria-hidden="true" />

      <Transition name="expand-map">
        <div v-if="isExpanded" class="expand-report-card__map-layer" aria-hidden="true">
          <svg class="expand-report-card__map-svg" preserveAspectRatio="none" viewBox="0 0 100 100">
            <line class="expand-report-card__road expand-report-card__road--main" x1="0" y1="35" x2="100" y2="35" />
            <line class="expand-report-card__road expand-report-card__road--main" x1="0" y1="65" x2="100" y2="65" />
            <line class="expand-report-card__road expand-report-card__road--mid" x1="30" y1="0" x2="30" y2="100" />
            <line class="expand-report-card__road expand-report-card__road--mid" x1="70" y1="0" x2="70" y2="100" />
            <line
              v-for="(y, index) in secondaryHorizontal"
              :key="`h-${index}`"
              class="expand-report-card__road expand-report-card__road--minor"
              x1="0"
              :y1="y"
              x2="100"
              :y2="y"
              :style="{ animationDelay: `${0.45 + index * 0.08}s` }"
            />
            <line
              v-for="(x, index) in secondaryVertical"
              :key="`v-${index}`"
              class="expand-report-card__road expand-report-card__road--minor"
              :x1="x"
              y1="0"
              :x2="x"
              y2="100"
              :style="{ animationDelay: `${0.55 + index * 0.08}s` }"
            />
          </svg>

          <span class="expand-report-card__building expand-report-card__building--1" />
          <span class="expand-report-card__building expand-report-card__building--2" />
          <span class="expand-report-card__building expand-report-card__building--3" />
          <span class="expand-report-card__building expand-report-card__building--4" />

          <div class="expand-report-card__pin">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
                :fill="pinColor"
              />
              <circle cx="12" cy="9" r="2.5" fill="var(--surface-panel-strong)" />
            </svg>
          </div>

          <div class="expand-report-card__map-fade" />
        </div>
      </Transition>

      <div class="expand-report-card__grid" aria-hidden="true">
        <svg width="100%" height="100%">
          <defs>
            <pattern :id="gridPatternId" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" stroke-width="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" :fill="`url(#${gridPatternId})`" />
        </svg>
      </div>

      <div class="expand-report-card__content">
        <div v-if="isExpanded" class="expand-report-card__map-header" aria-hidden="true">
          <span class="expand-report-card__live expand-report-card__live--floating">
            <span class="expand-report-card__live-dot" />
            {{ run.status === 'running' ? 'Live' : 'Route' }}
          </span>
        </div>

        <div v-else class="expand-report-card__top">
          <svg
            class="expand-report-card__map-icon"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
            <line x1="9" x2="9" y1="3" y2="18" />
            <line x1="15" x2="15" y1="6" y2="21" />
          </svg>

          <span class="expand-report-card__live">
            <span class="expand-report-card__live-dot" />
            {{ run.status === 'running' ? 'Live' : 'Route' }}
          </span>
        </div>

        <div
          class="expand-report-card__bottom"
          :class="{ 'expand-report-card__bottom--expanded': isExpanded }"
        >
          <div class="expand-report-card__meta-row">
            <h3 class="expand-report-card__title">{{ run.route_name }}</h3>
            <span class="expand-report-card__time">{{ formatRelativeTime(run.created_at) }}</span>
          </div>

          <div class="expand-report-card__tags">
            <AuditRunStatusPill :status="run.status" />
            <AppBadge tone="source-ai-audit" size="xs">AI audit</AppBadge>
            <AppBadge v-if="isDemoData" tone="warning" size="xs">Demo</AppBadge>
          </div>

          <Transition name="expand-coords">
            <p v-if="isExpanded" class="expand-report-card__coordinates">
              {{ coordinatesLabel }}
            </p>
          </Transition>

          <p v-if="description" class="expand-report-card__description">
            {{ description }}
          </p>

          <span class="expand-report-card__underline" aria-hidden="true" />
        </div>
      </div>
    </div>

    <p class="expand-report-card__hint">Click to expand</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AuditRunStatusPill from '@/components/audit/AuditRunStatusPill.vue';
import type { AuditRunSummary } from '@/types/audit';
import { formatRelativeTime } from '@/utils/reportFormatting';

const props = defineProps<{
  run: AuditRunSummary;
  selected: boolean;
  isDemoData?: boolean;
}>();

const emit = defineEmits<{
  select: [runId: string];
}>();

const secondaryHorizontal = [20, 50, 80];
const secondaryVertical = [15, 45, 55, 85];

const isHovered = ref(false);
const isExpanded = ref(false);

const pinColor = computed(() => {
  if (props.run.status === 'running') return 'var(--color-amber-signal)';
  if (props.run.status === 'failed') return 'var(--color-repair-red)';
  return 'var(--color-municipal-green)';
});

const gridPatternId = computed(() => `expand-audit-grid-${props.run.id}`);

const hasCoordinates = computed(
  () =>
    props.run.scan_latitude != null &&
    props.run.scan_longitude != null &&
    props.run.scan_latitude >= -90 &&
    props.run.scan_latitude <= 90 &&
    props.run.scan_longitude >= -180 &&
    props.run.scan_longitude <= 180,
);

const coordinatesLabel = computed(() => {
  if (!hasCoordinates.value) {
    return 'Coordinates unavailable';
  }

  const latitude = props.run.scan_latitude!;
  const longitude = props.run.scan_longitude!;
  const latDir = latitude >= 0 ? 'N' : 'S';
  const lngDir = longitude >= 0 ? 'E' : 'W';
  return `${Math.abs(latitude).toFixed(4)}° ${latDir}, ${Math.abs(longitude).toFixed(4)}° ${lngDir}`;
});

const description = computed(() => {
  if (props.run.notes?.trim()) {
    return props.run.notes.trim();
  }

  if (props.run.status === 'running' && props.run.frames_total > 0) {
    return `Analyzing frame ${props.run.frames_done} of ${props.run.frames_total} along ${props.run.municipality}.`;
  }

  if (props.run.status === 'running') {
    return `Street scan in progress across ${props.run.municipality}.`;
  }

  if (props.run.status === 'completed') {
    return `Route scan complete in ${props.run.municipality}. Review AI detections in the workspace.`;
  }

  if (props.run.status === 'queued') {
    return `Scan queued for ${props.run.municipality}. Waiting to start.`;
  }

  if (props.run.status === 'failed') {
    return `Scan failed for ${props.run.route_name}. Launch a new scan to retry.`;
  }

  return `${props.run.municipality} street audit route.`;
});

watch(
  () => props.selected,
  (selected) => {
    if (!selected) {
      isExpanded.value = false;
    }
  },
);

function handleClick() {
  emit('select', props.run.id);
  isExpanded.value = props.selected ? !isExpanded.value : true;
}
</script>

<style scoped>
.expand-report-card {
  position: relative;
  width: 100%;
  cursor: pointer;
  user-select: none;
}

.expand-report-card__surface {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--status-new-border);
  border-radius: var(--radius-lg);
  background: var(--surface-panel-strong);
  box-shadow: var(--shadow-card);
  transition:
    min-height 360ms cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow var(--motion-fast) ease,
    border-color var(--motion-fast) ease;
}

.expand-report-card--expanded .expand-report-card__surface {
  min-height: 13.5rem;
}

.expand-report-card:not(.expand-report-card--expanded) .expand-report-card__surface {
  min-height: 5.75rem;
}

.expand-report-card--selected .expand-report-card__surface {
  border-color: color-mix(in srgb, var(--color-municipal-green) 45%, var(--status-new-border));
  box-shadow:
    var(--shadow-card),
    0 0 0 1px color-mix(in srgb, var(--color-municipal-green) 18%, transparent);
}

.expand-report-card--hovered .expand-report-card__surface {
  box-shadow:
    0 14px 28px rgba(16, 20, 18, 0.12),
    0 0 0 1px color-mix(in srgb, var(--color-municipal-green) 12%, transparent);
}

.expand-report-card__gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--text-primary) 4%, transparent),
    transparent 45%,
    color-mix(in srgb, var(--text-primary) 8%, transparent)
  );
  pointer-events: none;
}

.expand-report-card--expanded .expand-report-card__gradient {
  display: none;
}

.expand-report-card__map-layer {
  position: absolute;
  inset: 0;
  background: var(--surface-muted);
  pointer-events: none;
}

.expand-report-card--expanded .expand-report-card__map-layer {
  inset: 0 0 auto 0;
  height: 5.35rem;
  border-bottom: 1px solid var(--status-new-border);
  background: color-mix(in srgb, var(--surface-muted) 88%, var(--surface-panel-strong));
}

.expand-report-card__map-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  color: var(--text-primary);
}

.expand-report-card__road {
  stroke: currentColor;
  stroke-linecap: round;
  opacity: 0;
  animation: expand-road-draw 0.7s ease forwards;
}

.expand-report-card__road--main {
  stroke-width: 0.55;
  opacity: 0.16;
  animation-delay: 0.12s;
}

.expand-report-card__road--mid {
  stroke-width: 0.42;
  opacity: 0.12;
  animation-delay: 0.22s;
}

.expand-report-card__road--minor {
  stroke-width: 0.28;
  opacity: 0.08;
}

.expand-report-card__building {
  position: absolute;
  border-radius: 2px;
  border: 1px solid color-mix(in srgb, var(--text-primary) 14%, transparent);
  background: color-mix(in srgb, var(--text-primary) 18%, transparent);
  opacity: 0;
  animation: expand-building-in 0.45s ease forwards;
}

.expand-report-card__building--1 {
  top: 40%;
  left: 10%;
  width: 15%;
  height: 20%;
  animation-delay: 0.28s;
}

.expand-report-card__building--2 {
  top: 15%;
  left: 35%;
  width: 12%;
  height: 15%;
  animation-delay: 0.34s;
}

.expand-report-card__building--3 {
  top: 70%;
  left: 75%;
  width: 18%;
  height: 18%;
  animation-delay: 0.4s;
}

.expand-report-card__building--4 {
  top: 20%;
  right: 10%;
  width: 10%;
  height: 25%;
  animation-delay: 0.31s;
}

.expand-report-card__pin {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  filter: drop-shadow(0 0 10px color-mix(in srgb, var(--color-municipal-green) 55%, transparent));
  animation: expand-pin-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) 0.18s both;
}

.expand-report-card__map-fade {
  display: none;
}

.expand-report-card__grid {
  position: absolute;
  inset: 0;
  color: var(--text-primary);
  opacity: 0.03;
  transition: opacity 240ms ease;
  pointer-events: none;
}

.expand-report-card--expanded .expand-report-card__grid {
  opacity: 0;
}

.expand-report-card__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.65rem;
  min-height: inherit;
  padding: 0.85rem 0.95rem;
}

.expand-report-card--expanded .expand-report-card__content {
  justify-content: flex-start;
  gap: 0;
  padding: 0;
  min-height: 13.5rem;
}

.expand-report-card__map-header {
  position: relative;
  flex: 0 0 5.35rem;
  width: 100%;
  pointer-events: none;
}

.expand-report-card__live--floating {
  position: absolute;
  top: 0.55rem;
  right: 0.55rem;
  background: color-mix(in srgb, var(--surface-panel-strong) 82%, transparent);
  border: 1px solid var(--status-new-border);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.expand-report-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.expand-report-card__map-icon {
  color: #34d399;
  filter: drop-shadow(0 0 4px rgba(52, 211, 153, 0.35));
  transition: filter 240ms ease;
}

.expand-report-card--hovered .expand-report-card__map-icon {
  filter: drop-shadow(0 0 8px rgba(52, 211, 153, 0.55));
}

.expand-report-card__live {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.18rem 0.45rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--text-primary) 6%, transparent);
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-shadow: 0 1px 2px rgba(16, 20, 18, 0.28);
  transition: background 180ms ease;
}

.expand-report-card--hovered .expand-report-card__live {
  background: color-mix(in srgb, var(--text-primary) 9%, transparent);
}

.expand-report-card__live-dot {
  width: 0.38rem;
  height: 0.38rem;
  border-radius: 50%;
  background: #34d399;
}

.expand-report-card__bottom {
  display: grid;
  gap: 0.35rem;
}

.expand-report-card__bottom--expanded {
  position: relative;
  z-index: 3;
  flex: 1;
  gap: 0.45rem;
  margin-top: auto;
  padding: 0.8rem 0.85rem 0.85rem;
  border-top: 1px solid var(--status-new-border);
  border-radius: 0;
  background: var(--surface-panel-strong);
  box-shadow: none;
}

.expand-report-card__meta-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.expand-report-card__title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  text-shadow:
    0 1px 2px rgba(16, 20, 18, 0.32),
    0 0 10px rgba(16, 20, 18, 0.18);
}

.expand-report-card__bottom--expanded .expand-report-card__title,
.expand-report-card__bottom--expanded .expand-report-card__time,
.expand-report-card__bottom--expanded .expand-report-card__coordinates,
.expand-report-card__bottom--expanded .expand-report-card__description {
  text-shadow: none;
}

.expand-report-card__time {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 750;
  text-shadow: 0 1px 2px rgba(16, 20, 18, 0.24);
}

.expand-report-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.28rem;
}

.expand-report-card__coordinates {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  text-shadow: 0 1px 2px rgba(16, 20, 18, 0.28);
}

.expand-report-card__bottom--expanded .expand-report-card__coordinates {
  color: var(--text-muted);
}

.expand-report-card__description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.4;
  text-shadow:
    0 1px 2px rgba(16, 20, 18, 0.3),
    0 0 8px rgba(16, 20, 18, 0.16);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

:global(html.dark) .expand-report-card__title,
:global(html.dark) .expand-report-card__description {
  text-shadow:
    0 1px 3px rgba(0, 0, 0, 0.55),
    0 0 12px rgba(0, 0, 0, 0.35);
}

:global(html.dark) .expand-report-card__time,
:global(html.dark) .expand-report-card__coordinates,
:global(html.dark) .expand-report-card__live {
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.45);
}

.expand-report-card:not(.expand-report-card--expanded) .expand-report-card__description {
  -webkit-line-clamp: 1;
}

.expand-report-card--expanded .expand-report-card__description {
  -webkit-line-clamp: unset;
  overflow: visible;
  display: block;
  color: var(--text-primary);
  font-size: 0.74rem;
  line-height: 1.5;
}

.expand-report-card--expanded .expand-report-card__underline {
  display: none;
}

.expand-report-card__underline {
  display: block;
  height: 1px;
  background: linear-gradient(
    to right,
    color-mix(in srgb, #34d399 55%, transparent),
    color-mix(in srgb, #34d399 28%, transparent),
    transparent
  );
  transform-origin: left center;
  transform: scaleX(0.3);
  transition: transform 360ms ease;
}

.expand-report-card--hovered .expand-report-card__underline,
.expand-report-card--expanded .expand-report-card__underline {
  transform: scaleX(1);
}

.expand-report-card__hint {
  position: absolute;
  left: 50%;
  bottom: -1.15rem;
  margin: 0;
  color: var(--text-muted);
  font-size: 0.58rem;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
  transition: opacity 180ms ease, transform 180ms ease;
  pointer-events: none;
}

.expand-report-card--hovered:not(.expand-report-card--expanded):not(.expand-report-card--selected) .expand-report-card__hint {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.expand-map-enter-active,
.expand-map-leave-active {
  transition: opacity 320ms ease;
}

.expand-map-enter-from,
.expand-map-leave-to {
  opacity: 0;
}

.expand-coords-enter-active,
.expand-coords-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.expand-coords-enter-from,
.expand-coords-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@keyframes expand-road-draw {
  from {
    opacity: 0;
    stroke-dasharray: 1 120;
    stroke-dashoffset: 120;
  }
  to {
    opacity: inherit;
    stroke-dasharray: 120 0;
    stroke-dashoffset: 0;
  }
}

@keyframes expand-building-in {
  from {
    opacity: 0;
    transform: scale(0.82);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes expand-pin-in {
  from {
    opacity: 0;
    transform: translate(-50%, calc(-50% - 12px)) scale(0.7);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>
