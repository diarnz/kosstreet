<template>
  <div v-if="src" class="detection-overlay">
    <img :src="src" :alt="alt" class="detection-overlay__image" />

    <div class="detection-overlay__markers" aria-hidden="true">
      <span
        class="detection-overlay__marker detection-overlay__marker--pulse"
        :class="`detection-overlay__marker--${severityTone}`"
        :style="markerStyle(displayCircle)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AuditSuggestionSeverity, BoundingBox } from '@/types/detection';
import {
  boundingBoxToCircle,
  getSeverityCircleTone,
  type DetectionCircle,
} from '@/utils/detectionOverlay';

const props = withDefaults(
  defineProps<{
    src?: string | null;
    alt?: string;
    boundingBox?: BoundingBox | null;
    severity?: AuditSuggestionSeverity | null;
  }>(),
  {
    src: null,
    alt: 'AI street audit evidence frame',
    severity: null,
    boundingBox: null,
  },
);

const severityTone = computed(() => getSeverityCircleTone(props.severity));

function markerStyle(circle: DetectionCircle) {
  const diameter = circle.radius * 200;
  return {
    left: `${circle.x * 100}%`,
    top: `${circle.y * 100}%`,
    width: `${diameter}%`,
    height: `${diameter}%`,
  };
}

const displayCircle = computed(() => {
  if (props.boundingBox) {
    return boundingBoxToCircle(props.boundingBox);
  }

  return {
    x: 0.5,
    y: 0.58,
    radius: props.severity === 'high' || props.severity === 'critical' ? 0.13 : 0.11,
  };
});
</script>

<style scoped>
.detection-overlay {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-md);
  background: var(--surface-map-placeholder);
  aspect-ratio: 16 / 10;
}

.detection-overlay__image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detection-overlay__markers {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.detection-overlay__marker {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.detection-overlay__marker--pulse {
  animation: pulse-ring 1.8s ease infinite;
}

.detection-overlay__marker--high {
  border-color: rgba(255, 236, 232, 0.98);
  box-shadow:
    0 0 0 1px rgba(200, 76, 58, 0.55),
    0 0 22px rgba(200, 76, 58, 0.55);
  background: rgba(200, 76, 58, 0.18);
}

.detection-overlay__marker--medium {
  border-color: rgba(255, 248, 232, 0.98);
  box-shadow:
    0 0 0 1px rgba(217, 144, 47, 0.55),
    0 0 22px rgba(217, 144, 47, 0.5);
  background: rgba(217, 144, 47, 0.16);
}

.detection-overlay__marker--low {
  border-color: rgba(236, 248, 240, 0.98);
  box-shadow:
    0 0 0 1px rgba(47, 93, 80, 0.55),
    0 0 22px rgba(47, 93, 80, 0.45);
  background: rgba(47, 93, 80, 0.16);
}

@media (prefers-reduced-motion: reduce) {
  .detection-overlay__marker--pulse {
    animation: none;
  }
}
</style>
