<template>
  <AppCard class="location-field stack-lg animate-scale-in" variant="default">
    <div class="location-field__head">
      <div>
        <h2>Location</h2>
        <p class="location-field__sub muted">Search or use GPS to pin where the issue is.</p>
      </div>
      <AppBadge :tone="hasValidLocation ? 'success' : 'warning'" size="xs">
        {{ hasValidLocation ? 'Ready' : 'Required' }}
      </AppBadge>
    </div>

    <LocationSearchField
      v-model:latitude="latitudeProxy"
      v-model:longitude="longitudeProxy"
      v-model:location-label="locationLabelProxy"
      hint=""
    />

    <div class="location-field__gps-row">
      <GpsLocateButton @error="geoError = $event" @located="onGpsLocated" />
    </div>

    <div v-if="hasValidLocation" class="location-field__confirmed animate-fade-in">
      <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path
          d="M3.5 8.2l2.8 2.8 6.2-6.4"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <div>
        <strong>{{ locationLabelProxy || 'Location selected' }}</strong>
        <span>{{ latitudeProxy }}, {{ longitudeProxy }}</span>
        <span v-if="accuracy">± {{ Math.round(accuracy) }}m accuracy</span>
      </div>
    </div>

    <p v-if="geoError" class="location-field__error">{{ geoError }}</p>

    <button class="location-field__advanced-toggle" type="button" @click="showAdvanced = !showAdvanced">
      {{ showAdvanced ? 'Hide manual coordinates' : 'Enter coordinates manually' }}
    </button>

    <div v-if="showAdvanced" class="location-field__grid animate-fade-in">
      <AppField label="Latitude" :error="latitudeError">
        <AppInput
          :model-value="latitudeText"
          aria-label="Latitude"
          placeholder="42.2139"
          type="number"
          @update:model-value="updateLatitude"
        />
      </AppField>

      <AppField label="Longitude" :error="longitudeError">
        <AppInput
          :model-value="longitudeText"
          aria-label="Longitude"
          placeholder="20.7397"
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
import AppCard from '@/components/common/AppCard.vue';
import AppField from '@/components/common/AppField.vue';
import AppInput from '@/components/common/AppInput.vue';
import GpsLocateButton from '@/components/maps/GpsLocateButton.vue';
import LocationSearchField from '@/components/maps/LocationSearchField.vue';

const props = defineProps<{
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  locationLabel?: string | null;
}>();

const emit = defineEmits<{
  'update:latitude': [value: number | null];
  'update:longitude': [value: number | null];
  'update:accuracy': [value: number | null];
  'update:locationLabel': [value: string | null];
}>();

const geoError = ref<string | null>(null);
const showAdvanced = ref(false);

const latitudeProxy = computed({
  get: () => props.latitude,
  set: (value) => emit('update:latitude', value),
});
const longitudeProxy = computed({
  get: () => props.longitude,
  set: (value) => emit('update:longitude', value),
});
const locationLabelProxy = computed({
  get: () => props.locationLabel ?? null,
  set: (value) => emit('update:locationLabel', value),
});

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
  () =>
    props.latitude !== null &&
    props.longitude !== null &&
    !latitudeError.value &&
    !longitudeError.value,
);

function onGpsLocated(payload: {
  latitude: number;
  longitude: number;
  accuracy: number;
  label: string;
}) {
  geoError.value = null;
  emit('update:latitude', payload.latitude);
  emit('update:longitude', payload.longitude);
  emit('update:accuracy', payload.accuracy);
  emit('update:locationLabel', payload.label);
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
  margin: 0;
}

.location-field__gps-row {
  display: flex;
  justify-content: center;
  padding: var(--space-2) 0 var(--space-6);
}

.location-field__confirmed {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  padding: var(--space-4);
  border: 1px solid rgba(47, 93, 80, 0.22);
  border-radius: var(--radius-md);
  background: rgba(221, 232, 213, 0.42);
}

.location-field__confirmed svg {
  flex-shrink: 0;
  width: 1.1rem;
  height: 1.1rem;
  margin-top: 0.15rem;
  color: var(--color-municipal-green);
}

.location-field__confirmed div {
  display: grid;
  gap: 0.2rem;
}

.location-field__confirmed strong {
  color: var(--text-primary);
}

.location-field__head {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: flex-start;
  justify-content: space-between;
}

.location-field h2 {
  margin: 0;
  font-size: var(--text-lg);
}

.location-field__sub {
  margin: 0.2rem 0 0;
  font-size: var(--text-xs);
}

.location-field__confirmed span {
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.location-field__error {
  color: var(--color-repair-red);
  font-weight: 800;
}

.location-field__advanced-toggle {
  justify-self: start;
  padding: 0;
  border: 0;
  color: var(--color-municipal-green);
  background: transparent;
  font-size: var(--text-sm);
  font-weight: 850;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.location-field__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

@media (max-width: 640px) {
  .location-field__gps-row {
    padding: var(--space-2) 0 var(--space-4);
  }

  .location-field__confirmed {
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-3);
  }

  .location-field__confirmed strong,
  .location-field__confirmed span {
    overflow-wrap: anywhere;
  }

  .location-field__grid {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }
}
</style>
