<template>
  <AppCard class="location-field stack" variant="inset">
    <div class="cluster-between">
      <div>
        <h2>Location</h2>
        <p>Use your current location or enter coordinates manually. Location is required.</p>
      </div>
      <AppBadge :tone="hasValidLocation ? 'success' : 'warning'">
        {{ hasValidLocation ? 'Location ready' : 'Required' }}
      </AppBadge>
    </div>

    <div class="cluster">
      <AppButton :disabled="isLoading" variant="secondary" @click="captureLocation">
        {{ isLoading ? 'Getting location...' : 'Use current location' }}
      </AppButton>
      <span v-if="accuracy" class="location-field__accuracy">Accuracy: {{ Math.round(accuracy) }}m</span>
    </div>

    <p v-if="geoError" class="location-field__error">{{ geoError }}</p>

    <div class="location-field__grid">
      <AppField label="Latitude" :error="latitudeError">
        <AppInput
          :model-value="latitudeText"
          aria-label="Latitude"
          placeholder="42.6629"
          type="number"
          @update:model-value="updateLatitude"
        />
      </AppField>

      <AppField label="Longitude" :error="longitudeError">
        <AppInput
          :model-value="longitudeText"
          aria-label="Longitude"
          placeholder="21.1655"
          type="number"
          @update:model-value="updateLongitude"
        />
      </AppField>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppField from '@/components/common/AppField.vue';
import AppInput from '@/components/common/AppInput.vue';
import { getCurrentLocation } from '@/composables/useGeolocation';

const props = defineProps<{
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
}>();

const emit = defineEmits<{
  'update:latitude': [value: number | null];
  'update:longitude': [value: number | null];
  'update:accuracy': [value: number | null];
}>();

const isLoading = ref(false);
const geoError = ref<string | null>(null);

const latitudeText = computed(() => (props.latitude === null ? '' : String(props.latitude)));
const longitudeText = computed(() => (props.longitude === null ? '' : String(props.longitude)));

const latitudeError = computed(() => {
  if (props.latitude === null) return undefined;
  return props.latitude < -90 || props.latitude > 90 ? 'Latitude must be between -90 and 90.' : undefined;
});

const longitudeError = computed(() => {
  if (props.longitude === null) return undefined;
  return props.longitude < -180 || props.longitude > 180
    ? 'Longitude must be between -180 and 180.'
    : undefined;
});

const hasValidLocation = computed(
  () => props.latitude !== null && props.longitude !== null && !latitudeError.value && !longitudeError.value,
);

async function captureLocation() {
  isLoading.value = true;
  geoError.value = null;

  try {
    const location = await getCurrentLocation();
    emit('update:latitude', Number(location.latitude.toFixed(6)));
    emit('update:longitude', Number(location.longitude.toFixed(6)));
    emit('update:accuracy', location.accuracy);
  } catch {
    geoError.value = 'Could not access your location. You can enter coordinates manually.';
  } finally {
    isLoading.value = false;
  }
}

function parseCoordinate(value: string): number | null {
  if (value.trim() === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function updateLatitude(value: string) {
  emit('update:latitude', parseCoordinate(value));
  emit('update:accuracy', null);
}

function updateLongitude(value: string) {
  emit('update:longitude', parseCoordinate(value));
  emit('update:accuracy', null);
}
</script>

<style scoped>
.location-field h2 {
  margin: 0 0 var(--space-2);
}

.location-field p,
.location-field__accuracy {
  color: var(--text-secondary);
}

.location-field__error {
  color: var(--color-repair-red);
  font-weight: 800;
}

.location-field__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

@media (max-width: 620px) {
  .location-field__grid {
    grid-template-columns: 1fr;
  }
}
</style>

