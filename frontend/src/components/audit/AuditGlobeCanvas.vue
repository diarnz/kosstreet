<template>
  <div class="audit-globe-canvas">
    <canvas
      ref="canvasRef"
      class="audit-globe-canvas__canvas"
      @pointerdown="onPointerDown"
      @pointerup="onPointerUp"
      @pointerout="onPointerUp"
      @mousemove="onMouseMove"
      @touchmove="onTouchMove"
    />
  </div>
</template>

<script setup lang="ts">
import createGlobe, { type COBEOptions } from 'cobe';
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useDarkMode } from '@/composables/useDarkMode';

const { isDark } = useDarkMode();

const canvasRef = ref<HTMLCanvasElement | null>(null);

let phi = 0;
let width = 0;
let globe: ReturnType<typeof createGlobe> | null = null;
let fadeTimer: number | undefined;
let animationFrame: number | undefined;

const pointerInteracting = ref<number | null>(null);
const pointerInteractionMovement = ref(0);
const dragOffset = ref(0);

const KOSOVO_MARKERS: COBEOptions['markers'] = [
  { location: [42.56, 20.92], size: 0.08 },
  { location: [42.9, 21.2], size: 0.04 },
  { location: [42.0, 20.5], size: 0.04 },
  { location: [42.4, 21.6], size: 0.05 },
  { location: [42.5, 20.2], size: 0.04 },
  { location: [42.2, 21.0], size: 0.03 },
];

function buildConfig(): COBEOptions {
  const dark = isDark.value;

  return {
    width: width * 2,
    height: width * 2,
    devicePixelRatio: 2,
    phi: 0,
    theta: 0.28,
    dark: dark ? 1 : 0,
    diffuse: 0.45,
    mapSamples: 14000,
    mapBrightness: dark ? 1.1 : 1.25,
    baseColor: dark ? [0.18, 0.24, 0.2] : [0.92, 0.95, 0.9],
    markerColor: [47 / 255, 93 / 255, 80 / 255],
    glowColor: dark ? [0.12, 0.18, 0.15] : [0.88, 0.93, 0.87],
    markers: KOSOVO_MARKERS,
  };
}

function onResize() {
  if (!canvasRef.value) {
    return;
  }
  width = canvasRef.value.offsetWidth;
  globe?.update({
    width: width * 2,
    height: width * 2,
  });
}

function stopAnimation() {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
    animationFrame = undefined;
  }
}

function animate() {
  if (!globe) {
    return;
  }

  if (pointerInteracting.value === null) {
    phi += 0.005;
  }

  globe.update({ phi: phi + dragOffset.value });
  animationFrame = requestAnimationFrame(animate);
}

function destroyGlobe() {
  stopAnimation();

  if (fadeTimer) {
    window.clearTimeout(fadeTimer);
    fadeTimer = undefined;
  }

  globe?.destroy();
  globe = null;

  if (canvasRef.value) {
    canvasRef.value.style.opacity = '0';
  }
}

function initGlobe() {
  if (!canvasRef.value) {
    return;
  }

  destroyGlobe();
  onResize();

  globe = createGlobe(canvasRef.value, buildConfig());
  animate();

  fadeTimer = window.setTimeout(() => {
    if (canvasRef.value) {
      canvasRef.value.style.opacity = '1';
    }
  }, 80);
}

function onPointerDown(event: PointerEvent) {
  pointerInteracting.value = event.clientX - pointerInteractionMovement.value;
  if (canvasRef.value) {
    canvasRef.value.style.cursor = 'grabbing';
  }
}

function onPointerUp() {
  pointerInteracting.value = null;
  if (canvasRef.value) {
    canvasRef.value.style.cursor = 'grab';
  }
}

function onMouseMove(event: MouseEvent) {
  if (pointerInteracting.value === null) {
    return;
  }
  const delta = event.clientX - pointerInteracting.value;
  pointerInteractionMovement.value = delta;
  dragOffset.value = delta / 200;
}

function onTouchMove(event: TouchEvent) {
  const touch = event.touches[0];
  if (!touch || pointerInteracting.value === null) {
    return;
  }
  const delta = touch.clientX - pointerInteracting.value;
  pointerInteractionMovement.value = delta;
  dragOffset.value = delta / 200;
}

onMounted(() => {
  initGlobe();
  window.addEventListener('resize', onResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', onResize);
  destroyGlobe();
});

watch(isDark, () => {
  initGlobe();
});
</script>

<style scoped>
.audit-globe-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  max-width: 28rem;
  margin-inline: auto;
  aspect-ratio: 1;
  pointer-events: auto;
}

.audit-globe-canvas__canvas {
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: grab;
  contain: layout paint size;
  transition: opacity 500ms ease;
}
</style>
