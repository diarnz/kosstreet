<template>
  <svg
    aria-label="AI-estimated issue regions"
    class="severity-region-overlay"
    preserveAspectRatio="none"
    role="group"
    viewBox="0 0 1 1"
  >
    <template v-if="isNeon">
      <g
        v-for="(region, index) in regions"
        :key="`neon-region-${index}`"
        :aria-label="ariaLabel"
        class="severity-region-overlay__group"
        :class="{ 'severity-region-overlay__group--active': activeIndex === index }"
        tabindex="0"
        @blur="emit('clear-active')"
        @focus="emit('set-active', index)"
        @mouseenter="emit('set-active', index)"
      >
        <circle
          class="severity-region-overlay__disk"
          :cx="region.center_x"
          :cy="region.center_y"
          :fill="neonStyle.fill"
          :fill-opacity="neonStyle.fillOpacity"
          :r="region.radius"
          stroke="none"
        >
          <animate
            attributeName="r"
            :begin="`${index * 0.35}s`"
            calcMode="spline"
            :dur="`${neonStyle.breatheDuration}s`"
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            keyTimes="0;0.5;1"
            repeatCount="indefinite"
            :values="`${region.radius * neonStyle.breatheMinScale};${region.radius * neonStyle.breatheMaxScale};${region.radius * neonStyle.breatheMinScale}`"
          />
          <animate
            attributeName="fill-opacity"
            :begin="`${index * 0.35}s`"
            calcMode="spline"
            :dur="`${neonStyle.breatheDuration}s`"
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            keyTimes="0;0.5;1"
            repeatCount="indefinite"
            :values="`${neonStyle.breatheMinOpacity};${neonStyle.breatheMaxOpacity};${neonStyle.breatheMinOpacity}`"
          />
        </circle>
      </g>
    </template>

    <template v-else>
      <circle
        v-for="(region, index) in regions"
        :key="`classic-region-${index}`"
        :aria-label="ariaLabel"
        class="severity-region-overlay__classic"
        :class="{ 'severity-region-overlay__classic--active': activeIndex === index }"
        :cx="region.center_x"
        :cy="region.center_y"
        :fill="classicStyle.fill"
        :r="region.radius"
        :stroke="classicStyle.stroke"
        stroke-width="0.012"
        tabindex="0"
        @blur="emit('clear-active')"
        @focus="emit('set-active', index)"
        @mouseenter="emit('set-active', index)"
      />
    </template>
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import {
  DEFAULT_REGION_OVERLAY_VARIANT,
  getNeonSeverityCircleStyle,
  getSeverityCircleStyle,
  type RegionOverlayVariant,
} from '@/utils/detectionRegions';

const props = withDefaults(
  defineProps<{
    regions: DetectionRegion[];
    severity?: AuditSuggestionSeverity | null;
    variant?: RegionOverlayVariant;
    activeIndex?: number | null;
    ariaLabel: string;
  }>(),
  {
    severity: null,
    variant: DEFAULT_REGION_OVERLAY_VARIANT,
    activeIndex: null,
  },
);

const emit = defineEmits<{
  'set-active': [index: number];
  'clear-active': [];
}>();

const isNeon = computed(() => props.variant === 'neon');
const neonStyle = computed(() => getNeonSeverityCircleStyle(props.severity));
const classicStyle = computed(() => getSeverityCircleStyle(props.severity, 'classic'));
</script>

<style scoped>
.severity-region-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.severity-region-overlay__group,
.severity-region-overlay__classic {
  pointer-events: auto;
  cursor: help;
  outline: none;
}

.severity-region-overlay__disk {
  pointer-events: visiblePainted;
}

.severity-region-overlay__group--active .severity-region-overlay__disk,
.severity-region-overlay__group:focus-visible .severity-region-overlay__disk {
  filter: brightness(1.08);
}
</style>
