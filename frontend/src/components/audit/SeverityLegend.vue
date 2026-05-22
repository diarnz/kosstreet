<template>
  <div
    aria-label="Severity overlay legend"
    class="severity-legend"
    :class="{ 'severity-legend--neon': isNeon }"
    role="list"
  >
    <div
      v-for="item in SEVERITY_LEGEND_ITEMS"
      :key="item.severity"
      class="severity-legend__item"
      role="listitem"
    >
      <span
        aria-hidden="true"
        class="severity-legend__swatch"
        :class="{ 'severity-legend__swatch--neon': isNeon }"
        :style="swatchStyle(item.severity)"
      />
      <div>
        <strong>{{ item.label }}</strong>
        <p>{{ item.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AuditSuggestionSeverity } from '@/types/detection';
import {
  CLASSIC_SEVERITY_CIRCLE_STYLES,
  DEFAULT_REGION_OVERLAY_VARIANT,
  getSeverityCircleStyle,
  neonLegendSwatchStyle,
  SEVERITY_LEGEND_ITEMS,
  type RegionOverlayVariant,
} from '@/utils/detectionRegions';

const props = withDefaults(
  defineProps<{
    variant?: RegionOverlayVariant;
  }>(),
  {
    variant: DEFAULT_REGION_OVERLAY_VARIANT,
  },
);

const isNeon = computed(() => props.variant === 'neon');

function swatchStyle(severity: AuditSuggestionSeverity): Record<string, string> {
  if (props.variant === 'neon') {
    return neonLegendSwatchStyle(severity);
  }

  const classic = getSeverityCircleStyle(severity, 'classic');
  return {
    borderColor: classic.stroke,
    backgroundColor: CLASSIC_SEVERITY_CIRCLE_STYLES[severity].fill,
  };
}
</script>

<style scoped>
.severity-legend {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
  gap: var(--space-3);
}

.severity-legend--neon .severity-legend__item {
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.02), rgba(15, 23, 42, 0.05)),
    rgba(255, 253, 247, 0.72);
}

.severity-legend__item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--space-3);
  align-items: start;
  padding: var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-sm);
  background: rgba(255, 253, 247, 0.72);
}

.severity-legend__swatch {
  width: 1.25rem;
  height: 1.25rem;
  border: 3px solid;
  border-radius: 999px;
  margin-top: 0.15rem;
}

.severity-legend__swatch--neon {
  border: none;
  transform-origin: center;
  animation: severity-legend-breathe 3.2s ease-in-out infinite;
}

@keyframes severity-legend-breathe {
  0%,
  100% {
    opacity: 0.72;
    transform: scale(0.94);
  }

  50% {
    opacity: 1;
    transform: scale(1.06);
  }
}

.severity-legend__item strong {
  display: block;
  color: var(--text-primary);
}

.severity-legend__item p {
  margin: var(--space-1) 0 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>
