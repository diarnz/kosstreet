<template>
  <section class="report-queue">
    <div class="report-queue__head">
      <span class="report-queue__count">{{ reports.length }}</span>
    </div>

    <AppLoading v-if="isLoading" label="Loading" />

    <AppEmptyState
      v-else-if="reports.length === 0"
      tone="dashboard"
      title="No reports"
      description="Clear filters or create a new report."
    />

    <div v-else class="report-queue__list" role="list">
      <button
        v-for="report in reports"
        :key="report.id"
        class="report-queue__item"
        :class="[
          `report-queue__item--${report.status}`,
          { 'report-queue__item--selected': report.id === selectedReportId },
        ]"
        :style="tiltStyle(report.id)"
        type="button"
        role="listitem"
        :aria-pressed="report.id === selectedReportId"
        :aria-label="`Select ${categoryLabels[report.category]} report`"
        @click="$emit('select', report.id)"
        @mousemove="handlePointerMove($event, report.id)"
        @mouseleave="resetTilt(report.id)"
        @blur="resetTilt(report.id)"
      >
        <span class="report-queue__accent" aria-hidden="true" />

        <div class="report-queue__visual" aria-hidden="true">
          <div class="report-queue__gradient" />
          <div class="report-queue__grid" />

          <div v-if="report.id === selectedReportId" class="report-queue__map">
            <svg class="report-queue__roads" viewBox="0 0 320 170" preserveAspectRatio="none">
              <path class="report-queue__road report-queue__road--main" d="M0 58 H320" />
              <path class="report-queue__road report-queue__road--main" d="M0 116 H320" />
              <path class="report-queue__road" d="M95 0 V170" />
              <path class="report-queue__road" d="M224 0 V170" />
              <path class="report-queue__street" d="M0 31 H320 M0 85 H320 M0 143 H320" />
              <path class="report-queue__street" d="M48 0 V170 M144 0 V170 M176 0 V170 M272 0 V170" />
            </svg>

            <span class="report-queue__building report-queue__building--one" />
            <span class="report-queue__building report-queue__building--two" />
            <span class="report-queue__building report-queue__building--three" />
            <span class="report-queue__building report-queue__building--four" />

            <svg class="report-queue__pin" viewBox="0 0 24 24">
              <path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7Z" />
              <circle cx="12" cy="9" r="2.5" />
            </svg>
          </div>
        </div>

        <div class="report-queue__content">
          <div class="report-queue__topline">
            <svg class="report-queue__map-icon" viewBox="0 0 24 24" fill="none">
              <path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z" />
              <path d="M9 3v15M15 6v15" />
            </svg>

            <span class="report-queue__live">
              <span class="report-queue__live-dot" />
              Live
            </span>
          </div>

          <div class="report-queue__details">
            <div class="report-queue__row">
              <strong class="report-queue__title">{{ categoryLabels[report.category] }}</strong>
              <span class="report-queue__time">{{ formatRelativeTime(report.created_at) }}</span>
            </div>

            <p v-if="report.id === selectedReportId" class="report-queue__coordinates">
              {{ formatCoordinates(report.latitude, report.longitude) }}
            </p>

            <div class="report-queue__tags">
              <StatusPill :status="report.status" />
              <ReportSourceBadge compact :source="report.source" />
              <AppBadge v-if="isDemoData" tone="warning" size="xs">Demo</AppBadge>
            </div>

            <p v-if="report.description" class="report-queue__description">
              {{ report.description }}
            </p>

            <span class="report-queue__underline" />
          </div>
        </div>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type { ReportSummary } from '@/types/report';
import { categoryLabels, formatCoordinates, formatRelativeTime } from '@/utils/reportFormatting';

defineProps<{
  reports: ReportSummary[];
  selectedReportId: string | null;
  isLoading: boolean;
  isDemoData?: boolean;
}>();

defineEmits<{
  select: [reportId: string];
}>();

const tiltByReport = reactive<Record<string, { x: number; y: number }>>({});

function handlePointerMove(event: MouseEvent, reportId: string) {
  const target = event.currentTarget as HTMLElement;
  const rect = target.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width - 0.5;
  const y = (event.clientY - rect.top) / rect.height - 0.5;

  tiltByReport[reportId] = {
    x: Math.max(-3, Math.min(3, y * -6)),
    y: Math.max(-3, Math.min(3, x * 6)),
  };
}

function resetTilt(reportId: string) {
  tiltByReport[reportId] = { x: 0, y: 0 };
}

function tiltStyle(reportId: string) {
  const tilt = tiltByReport[reportId] ?? { x: 0, y: 0 };
  return {
    '--tilt-x': `${tilt.x}deg`,
    '--tilt-y': `${tilt.y}deg`,
  };
}
</script>

<style scoped>
.report-queue {
  display: grid;
  gap: var(--space-2);
}

.report-queue__head {
  display: flex;
  justify-content: flex-end;
}

.report-queue__count {
  display: grid;
  place-items: center;
  min-width: 1.75rem;
  height: 1.75rem;
  padding: 0 0.45rem;
  border-radius: var(--radius-pill);
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.1);
  font-size: 0.72rem;
  font-weight: 900;
}

.report-queue__list {
  display: grid;
  gap: var(--space-2);
  max-height: 42rem;
  padding: 2px;
  overflow: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(47, 93, 80, 0.15) transparent;
  perspective: 900px;
}

.report-queue__item {
  --tilt-x: 0deg;
  --tilt-y: 0deg;
  position: relative;
  display: block;
  width: 100%;
  min-height: 8.5rem;
  padding: 0;
  overflow: hidden;
  border: var(--border-soft);
  border-radius: var(--radius-md);
  color: inherit;
  background: var(--surface-panel-strong);
  box-shadow: var(--shadow-inset);
  text-align: left;
  cursor: pointer;
  transform: rotateX(var(--tilt-x)) rotateY(var(--tilt-y));
  transform-style: preserve-3d;
  transition:
    min-height var(--motion-slow) var(--ease-out-expo),
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-base) ease,
    transform 100ms ease-out;
}

.report-queue__item:hover {
  border-color: rgba(47, 93, 80, 0.26);
  box-shadow: var(--shadow-card);
}

.report-queue__item:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus), var(--shadow-card);
}

.report-queue__item--selected {
  min-height: 17.5rem;
  border-color: rgba(47, 93, 80, 0.38);
  box-shadow: var(--shadow-card), 0 0 24px rgba(47, 93, 80, 0.1);
}

.report-queue__accent {
  position: absolute;
  z-index: 4;
  inset: 0 auto 0 0;
  width: 3px;
  background: rgba(23, 33, 26, 0.12);
  transition: background var(--motion-fast) ease, box-shadow var(--motion-fast) ease;
}

.report-queue__item--new .report-queue__accent { background: var(--color-road-graphite); }
.report-queue__item--verified .report-queue__accent { background: var(--color-resolved-blue); }
.report-queue__item--assigned .report-queue__accent { background: var(--color-municipal-green); }
.report-queue__item--in_progress .report-queue__accent { background: var(--color-amber-signal); }
.report-queue__item--resolved .report-queue__accent { background: #245143; }
.report-queue__item--rejected .report-queue__accent { background: var(--color-repair-red); }

.report-queue__item--selected .report-queue__accent {
  box-shadow: 0 0 9px currentColor;
}

.report-queue__visual,
.report-queue__gradient,
.report-queue__grid,
.report-queue__map {
  position: absolute;
  inset: 0;
}

.report-queue__visual {
  background: var(--surface-panel-strong);
}

.report-queue__gradient {
  background: linear-gradient(145deg, rgba(47, 93, 80, 0.03), transparent 45%, rgba(47, 93, 80, 0.1));
}

.report-queue__grid {
  opacity: 0.14;
  background-image:
    linear-gradient(rgba(47, 93, 80, 0.18) 1px, transparent 1px),
    linear-gradient(90deg, rgba(47, 93, 80, 0.18) 1px, transparent 1px);
  background-size: 20px 20px;
  transition: opacity var(--motion-base) ease;
}

.report-queue__item--selected .report-queue__grid {
  opacity: 0;
}

.report-queue__map {
  overflow: hidden;
  background: var(--surface-muted);
  animation: map-reveal var(--motion-slow) ease both;
}

.report-queue__map::after {
  content: '';
  position: absolute;
  inset: 35% 0 0;
  background: linear-gradient(transparent, var(--surface-panel-strong));
}

.report-queue__roads {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.report-queue__road,
.report-queue__street {
  fill: none;
  stroke: var(--text-primary);
  vector-effect: non-scaling-stroke;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: draw-road 700ms var(--ease-out-expo) forwards;
}

.report-queue__road { stroke-width: 2; opacity: 0.16; }
.report-queue__road--main { stroke-width: 4; opacity: 0.22; }
.report-queue__street { stroke-width: 1; opacity: 0.09; animation-delay: 120ms; }

.report-queue__building {
  position: absolute;
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: 3px;
  background: rgba(47, 93, 80, 0.16);
  animation: building-in 300ms ease both;
}

.report-queue__building--one { top: 24%; left: 8%; width: 17%; height: 18%; animation-delay: 180ms; }
.report-queue__building--two { top: 10%; left: 36%; width: 12%; height: 17%; animation-delay: 230ms; }
.report-queue__building--three { top: 42%; right: 7%; width: 18%; height: 20%; animation-delay: 280ms; }
.report-queue__building--four { top: 14%; right: 11%; width: 10%; height: 23%; animation-delay: 320ms; }

.report-queue__pin {
  position: absolute;
  z-index: 2;
  top: 27%;
  left: 50%;
  width: 2rem;
  height: 2rem;
  overflow: visible;
  filter: drop-shadow(0 0 8px rgba(47, 93, 80, 0.45));
  transform: translate(-50%, -50%);
  animation: pin-in 380ms var(--ease-spring) 180ms both;
}

.report-queue__pin path { fill: var(--color-municipal-green); }
.report-queue__pin circle { fill: var(--surface-panel-strong); }

.report-queue__content {
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: inherit;
  padding: 0.85rem 0.9rem 0.8rem 1rem;
  transform: translateZ(12px);
}

.report-queue__topline,
.report-queue__row,
.report-queue__tags {
  display: flex;
  align-items: center;
}

.report-queue__topline,
.report-queue__row {
  justify-content: space-between;
}

.report-queue__map-icon {
  width: 1.1rem;
  height: 1.1rem;
  stroke: var(--color-municipal-green);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: filter var(--motion-fast) ease, opacity var(--motion-base) ease;
}

.report-queue__item:hover .report-queue__map-icon {
  filter: drop-shadow(0 0 6px rgba(47, 93, 80, 0.55));
}

.report-queue__item--selected .report-queue__map-icon { opacity: 0; }

.report-queue__live {
  display: inline-flex;
  gap: 0.35rem;
  align-items: center;
  padding: 0.25rem 0.45rem;
  border-radius: var(--radius-pill);
  color: var(--text-muted);
  background: rgba(47, 93, 80, 0.08);
  font-size: 0.58rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.report-queue__live-dot {
  width: 0.38rem;
  height: 0.38rem;
  border-radius: 50%;
  background: #34a875;
  box-shadow: 0 0 6px rgba(52, 168, 117, 0.6);
}

.report-queue__details {
  display: grid;
  gap: 0.35rem;
}

.report-queue__row { gap: var(--space-2); align-items: baseline; }

.report-queue__title {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 850;
  letter-spacing: -0.01em;
  transition: transform var(--motion-fast) var(--ease-out-expo);
}

.report-queue__item:hover .report-queue__title { transform: translateX(3px); }

.report-queue__time {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 750;
}

.report-queue__coordinates {
  margin: 0;
  color: var(--text-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.65rem;
  animation: content-in var(--motion-base) ease both;
}

.report-queue__tags { flex-wrap: wrap; gap: 0.28rem; }

.report-queue__description {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.report-queue__item--selected .report-queue__description { -webkit-line-clamp: 2; }

.report-queue__underline {
  display: block;
  width: 30%;
  height: 1px;
  background: linear-gradient(90deg, var(--color-municipal-green), transparent);
  transform-origin: left;
  transition: width var(--motion-slow) var(--ease-out-expo);
}

.report-queue__item:hover .report-queue__underline,
.report-queue__item--selected .report-queue__underline { width: 100%; }

@keyframes map-reveal {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes draw-road { to { stroke-dashoffset: 0; } }

@keyframes building-in {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes pin-in {
  from { opacity: 0; transform: translate(-50%, -80%) scale(0); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

@keyframes content-in {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (hover: none) {
  .report-queue__item { transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .report-queue__item,
  .report-queue__map-icon,
  .report-queue__title,
  .report-queue__underline {
    transition: none;
  }

  .report-queue__map,
  .report-queue__road,
  .report-queue__street,
  .report-queue__building,
  .report-queue__pin,
  .report-queue__coordinates {
    animation: none;
  }
}
</style>
