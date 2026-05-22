<template>
  <div
    v-if="visible"
    class="audit-analyzing-overlay"
    role="status"
    aria-live="polite"
    :aria-label="title"
  >
    <div class="audit-analyzing-overlay__panel">
      <div
        class="audit-analyzing-overlay__spinner"
        :class="{ 'audit-analyzing-overlay__spinner--static': prefersReducedMotion }"
        aria-hidden="true"
      />

      <p class="audit-analyzing-overlay__title">{{ title }}</p>
      <p v-if="subtitle" class="audit-analyzing-overlay__subtitle">{{ subtitle }}</p>

      <div v-if="progress != null" class="audit-analyzing-overlay__progress" aria-hidden="true">
        <div class="audit-analyzing-overlay__progress-bar" :style="{ width: `${progress}%` }" />
      </div>
      <p v-if="progressLabel" class="audit-analyzing-overlay__progress-label">{{ progressLabel }}</p>

      <AppButton
        v-if="showCancel"
        class="audit-analyzing-overlay__cancel"
        size="sm"
        type="button"
        variant="secondary"
        @click="emit('cancel')"
      >
        Cancel
      </AppButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import AppButton from '@/components/common/AppButton.vue';

defineProps<{
  visible: boolean;
  title: string;
  subtitle?: string | null;
  progress?: number | null;
  progressLabel?: string | null;
  showCancel?: boolean;
}>();

const emit = defineEmits<{
  cancel: [];
}>();

const prefersReducedMotion = ref(false);
let mediaQuery: MediaQueryList | null = null;

function syncReducedMotion() {
  prefersReducedMotion.value = mediaQuery?.matches ?? false;
}

onMounted(() => {
  mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  syncReducedMotion();
  mediaQuery.addEventListener('change', syncReducedMotion);
});

onUnmounted(() => {
  mediaQuery?.removeEventListener('change', syncReducedMotion);
});
</script>

<style scoped>
.audit-analyzing-overlay {
  position: absolute;
  inset: 0;
  z-index: 5;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: rgba(12, 18, 14, 0.78);
  backdrop-filter: blur(6px);
}

.audit-analyzing-overlay__panel {
  display: grid;
  justify-items: center;
  gap: var(--space-3);
  width: min(100%, 22rem);
  padding: var(--space-5);
  border: 1px solid rgba(255, 253, 247, 0.14);
  border-radius: var(--radius-lg);
  color: #fff;
  text-align: center;
  background: rgba(23, 33, 26, 0.88);
}

.audit-analyzing-overlay__spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid rgba(255, 253, 247, 0.18);
  border-top-color: #86efac;
  border-radius: 50%;
  animation: audit-analyzing-spin 900ms linear infinite;
}

.audit-analyzing-overlay__spinner--static {
  animation: none;
  border-top-color: rgba(255, 253, 247, 0.18);
}

.audit-analyzing-overlay__title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 850;
}

.audit-analyzing-overlay__subtitle {
  margin: 0;
  color: rgba(255, 253, 247, 0.78);
  font-size: var(--text-sm);
  line-height: 1.45;
}

.audit-analyzing-overlay__progress {
  width: 100%;
  height: 0.45rem;
  overflow: hidden;
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.14);
}

.audit-analyzing-overlay__progress-bar {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  transition: width 240ms ease;
}

.audit-analyzing-overlay__progress-label {
  margin: 0;
  color: rgba(255, 253, 247, 0.82);
  font-size: var(--text-xs);
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.audit-analyzing-overlay__cancel {
  margin-top: var(--space-1);
}

@keyframes audit-analyzing-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .audit-analyzing-overlay__spinner {
    animation: none;
  }

  .audit-analyzing-overlay__progress-bar {
    transition: none;
  }
}
</style>
