<template>
  <div class="location-search">
    <label v-if="label" class="location-search__label">{{ label }}</label>
    <div
      class="location-search__shell"
      :class="{ 'location-search__shell--disabled': disabled, 'location-search__shell--busy': isSearching }"
    >
      <svg class="location-search__icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
        <path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </svg>
      <div ref="hostRef" class="location-search__host" @keydown.enter.prevent="onEnter" />
      <button
        class="location-search__map-btn"
        type="button"
        aria-label="Pick location on map"
        :disabled="disabled"
        @click="mapPickerOpen = true"
      >
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7Z"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linejoin="round"
          />
          <circle cx="12" cy="9" r="2.5" stroke="currentColor" stroke-width="1.8" />
        </svg>
      </button>
    </div>
    <p v-if="loadError" class="location-search__hint location-search__hint--warn">{{ loadError }}</p>

    <LocationMapPicker
      :open="mapPickerOpen"
      :latitude="latitude"
      :longitude="longitude"
      @close="mapPickerOpen = false"
      @select="onMapSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import LocationMapPicker from '@/components/maps/LocationMapPicker.vue';
import { usePlacesAutocomplete } from '@/composables/usePlacesAutocomplete';
import type { PlaceSelection } from '@/utils/places';
import { snapToStreetViewAtCoordinates } from '@/utils/streetView';

const props = withDefaults(
  defineProps<{
    latitude: number | null;
    longitude: number | null;
    label?: string;
    locationLabel?: string | null;
    placeholder?: string;
    hint?: string;
    disabled?: boolean;
  }>(),
  {
    label: '',
    locationLabel: null,
    placeholder: 'Search streets, landmarks, or neighborhoods in Prizren',
    hint: '',
    disabled: false,
  },
);

const emit = defineEmits<{
  'update:latitude': [value: number | null];
  'update:longitude': [value: number | null];
  'update:locationLabel': [value: string | null];
}>();

const hostRef = ref<HTMLElement | null>(null);
const manualQuery = ref('');
const mapPickerOpen = ref(false);
const { initialize, searchQuery, setPlaceholder, setDisabled, isSearching, loadError } =
  usePlacesAutocomplete(hostRef);

function applySelection(selection: PlaceSelection) {
  void applySnappedSelection(selection);
}

async function applySnappedSelection(selection: PlaceSelection) {
  const snapped = await snapToStreetViewAtCoordinates(selection.latitude, selection.longitude);
  const resolved = snapped
    ? {
        latitude: snapped.latitude,
        longitude: snapped.longitude,
        label: snapped.description?.trim() || selection.label,
      }
    : selection;

  manualQuery.value = resolved.label;
  emit('update:latitude', resolved.latitude);
  emit('update:longitude', resolved.longitude);
  emit('update:locationLabel', resolved.label);

  const input = hostRef.value?.querySelector('input');
  if (input) {
    input.value = resolved.label;
  }
}

function onMapSelect(selection: PlaceSelection) {
  applySelection(selection);
  mapPickerOpen.value = false;
}

function bindInputListener() {
  const input = hostRef.value?.querySelector('input');
  if (!input || input.dataset.bound === '1') {
    return;
  }
  input.dataset.bound = '1';
  input.addEventListener('input', () => {
    manualQuery.value = input.value;
  });
}

onMounted(async () => {
  await initialize(applySelection);
  setPlaceholder(props.placeholder);
  setDisabled(props.disabled);
  bindInputListener();
  window.setTimeout(bindInputListener, 100);
});

watch(
  () => props.placeholder,
  (value) => setPlaceholder(value),
);

watch(
  () => props.disabled,
  (value) => setDisabled(value),
);

watch(
  () => props.locationLabel,
  (value) => {
    if (value) {
      manualQuery.value = value;
      const input = hostRef.value?.querySelector('input');
      if (input && input.value !== value) {
        input.value = value;
      }
    }
  },
  { immediate: true },
);

async function onEnter() {
  const input = hostRef.value?.querySelector('input');
  const query = input?.value?.trim() || manualQuery.value.trim();
  if (!query) {
    return;
  }
  manualQuery.value = query;
  await searchQuery(query);
}
</script>

<style scoped>
.location-search {
  display: grid;
  gap: var(--space-2);
}

.location-search__label {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.location-search__shell {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 3rem;
  padding: 0 0.35rem 0 1rem;
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-pill);
  background: #fff;
  box-shadow: 0 1px 6px rgba(23, 33, 26, 0.05);
  transition:
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

.location-search__shell:focus-within {
  border-color: rgba(47, 93, 80, 0.35);
  box-shadow:
    0 1px 6px rgba(23, 33, 26, 0.05),
    0 0 0 3px rgba(47, 93, 80, 0.1);
}

.location-search__shell--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.location-search__shell--busy {
  opacity: 0.85;
}

.location-search__icon {
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
  color: var(--color-municipal-green);
  pointer-events: none;
}

.location-search__host {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
}

.location-search__map-btn {
  display: grid;
  flex-shrink: 0;
  place-items: center;
  width: 2.35rem;
  height: 2.35rem;
  border: 0;
  border-radius: 50%;
  color: var(--color-municipal-green);
  background: rgba(47, 93, 80, 0.1);
  cursor: pointer;
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    background var(--motion-fast) ease;
}

.location-search__map-btn svg {
  width: 1.1rem;
  height: 1.1rem;
}

.location-search__map-btn:hover:not(:disabled) {
  transform: scale(1.04);
  background: rgba(47, 93, 80, 0.16);
}

.location-search__map-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.location-search__host :deep(gmp-place-autocomplete) {
  display: block;
  width: 100%;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.location-search__host :deep(.location-search__legacy-input),
.location-search__host :deep(input) {
  width: 100%;
  min-height: 2.75rem;
  padding: 0;
  border: 0 !important;
  outline: none !important;
  box-shadow: none !important;
  color: var(--text-primary);
  background: transparent !important;
  font-family: var(--font-sans);
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.4;
}

.location-search__host :deep(input::placeholder) {
  color: rgba(58, 63, 59, 0.5);
}

.location-search__hint {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.location-search__hint--warn {
  color: var(--color-repair-red);
  font-weight: 750;
}
</style>
