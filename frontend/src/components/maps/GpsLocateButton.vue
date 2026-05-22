<template>
  <button
    class="gps-locate"
    :class="{
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
    <span class="gps-locate__label">{{ isLoading ? 'Locating…' : 'Use my location' }}</span>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { getCurrentLocation } from '@/composables/useGeolocation';

defineProps<{
  disabled?: boolean;
}>();

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
  flex-direction: column;
  gap: var(--space-2);
  align-items: center;
  justify-content: center;
  width: 5.5rem;
  height: 5.5rem;
  padding: 0;
  border: var(--border-soft);
  border-radius: 50%;
  color: var(--color-municipal-green);
  background: rgba(255, 253, 247, 0.82);
  box-shadow: var(--shadow-card);
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    box-shadow var(--motion-fast) ease,
    border-color var(--motion-fast) ease;
}

.gps-locate:hover:not(:disabled) {
  transform: translateY(-2px);
  border-color: rgba(47, 93, 80, 0.32);
  box-shadow: var(--shadow-command);
}

.gps-locate:disabled {
  opacity: 0.55;
}

.gps-locate__ring {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  opacity: 0;
}

.gps-locate--loading .gps-locate__ring {
  opacity: 1;
  animation: pulse-ring 1.4s ease infinite;
}

.gps-locate--success {
  color: var(--text-inverse);
  background: var(--action-primary);
  border-color: transparent;
}

.gps-locate__icon {
  width: 1.5rem;
  height: 1.5rem;
}

.gps-locate__label {
  position: absolute;
  bottom: -1.65rem;
  width: max-content;
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.02em;
}
</style>
