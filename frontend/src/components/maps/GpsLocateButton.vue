<template>
  <button
    class="gps-locate"
    :class="{
      'gps-locate--compact': compact,
      'gps-locate--loading': isLoading,
      'gps-locate--success': showSuccess,
    }"
    :aria-label="isLoading ? 'Getting location' : 'Use my current location'"
    :disabled="disabled || isLoading"
    type="button"
    @click="capture"
  >
    <span class="gps-locate__ring" aria-hidden="true" />
    <svg class="gps-locate__icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" />
      <path
        d="M12 2v3M12 19v3M2 12h3M19 12h3"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
      />
    </svg>
    <span class="gps-locate__label">{{ isLoading ? 'Locating…' : 'My location' }}</span>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { getCurrentLocation } from '@/composables/useGeolocation';

withDefaults(
  defineProps<{
    disabled?: boolean;
    compact?: boolean;
  }>(),
  {
    compact: false,
  },
);

const emit = defineEmits<{
  located: [payload: { latitude: number; longitude: number; accuracy: number; label: string }];
  error: [message: string];
}>();

const isLoading = ref(false);
const showSuccess = ref(false);

async function capture() {
  isLoading.value = true;
  showSuccess.value = false;

  try {
    const location = await getCurrentLocation();
    showSuccess.value = true;
    emit('located', {
      latitude: Number(location.latitude.toFixed(6)),
      longitude: Number(location.longitude.toFixed(6)),
      accuracy: location.accuracy,
      label: 'Current location',
    });
    window.setTimeout(() => {
      showSuccess.value = false;
    }, 1400);
  } catch {
    emit('error', 'Could not access your location. Try the search field instead.');
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.gps-locate {
  position: relative;
  display: inline-flex;
  flex-direction: row;
  gap: 0.45rem;
  align-items: center;
  justify-content: center;
  height: 2.65rem;
  padding: 0 1rem;
  border: 1.5px solid rgba(47, 93, 80, 0.28);
  border-radius: var(--radius-pill);
  background: rgba(47, 93, 80, 0.06);
  color: var(--color-municipal-green);
  font-size: var(--text-sm);
  font-weight: 850;
  white-space: nowrap;
  flex-shrink: 0;
  transition:
    background var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease,
    transform var(--motion-fast) var(--ease-out-expo),
    color var(--motion-fast) ease;
}

.gps-locate:hover:not(:disabled) {
  background: rgba(47, 93, 80, 0.12);
  border-color: rgba(47, 93, 80, 0.5);
  box-shadow: 0 4px 14px rgba(47, 93, 80, 0.18);
  transform: translateY(-1px);
}

.gps-locate:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.gps-locate__ring {
  position: absolute;
  inset: -4px;
  border-radius: var(--radius-pill);
  opacity: 0;
}

.gps-locate--loading .gps-locate__ring {
  opacity: 1;
  animation: pulse-ring 1.4s ease infinite;
}

.gps-locate--success {
  color: #fff;
  background: var(--color-municipal-green);
  border-color: var(--color-municipal-green);
  box-shadow: 0 0 0 3px rgba(47, 93, 80, 0.2), 0 4px 16px rgba(47, 93, 80, 0.3);
}

.gps-locate__icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.gps-locate__label {
  line-height: 1;
}

.gps-locate--compact {
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  box-shadow: none;
}

.gps-locate--compact:hover:not(:disabled) {
  transform: none;
  background: rgba(47, 93, 80, 0.07);
  color: var(--text-primary);
  box-shadow: none;
}

.gps-locate--compact .gps-locate__label {
  display: none;
}

.gps-locate--compact.gps-locate--success {
  color: #fff;
  background: var(--color-municipal-green);
}
</style>
