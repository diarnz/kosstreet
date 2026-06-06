<template>
  <Teleport to="body">
    <div v-if="open" class="location-map-picker" role="presentation" @click.self="close">
      <section
        class="location-map-picker__dialog glass-panel glass-panel--elevated"
        role="dialog"
        aria-modal="true"
        aria-labelledby="location-map-picker-title"
      >
        <header class="location-map-picker__header">
          <div>
            <p class="command-label">Map picker</p>
            <h2 id="location-map-picker-title">Pick a Street View location in Kosovo</h2>
            <p class="location-map-picker__sub">
              Map opens on Kosovo. Blue lines show Street View coverage — tap a covered street to add it to search.
            </p>
          </div>
          <button class="location-map-picker__close" type="button" aria-label="Close map" @click="close">
            ×
          </button>
        </header>

        <div ref="mapElement" class="location-map-picker__map" aria-label="Kosovo map" />

        <p v-if="statusMessage" class="location-map-picker__status" :class="{ 'location-map-picker__status--error': isError }">
          {{ statusMessage }}
        </p>

        <p v-else-if="isLoadingMap" class="location-map-picker__status">Loading map…</p>
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, shallowRef, watch } from 'vue';
import type { PlaceSelection } from '@/utils/places';
import { getKosovoMapPickerOptions, reverseGeocodeCoordinates } from '@/utils/places';
import { loadGoogleMaps, getGoogleMapsLoadHint } from '@/utils/googleMaps';
import { KOSOVO_DEFAULT_VIEWPORT } from '@/utils/map';
import { snapToStreetViewAtCoordinates } from '@/utils/streetView';

const props = defineProps<{
  open: boolean;
  latitude?: number | null;
  longitude?: number | null;
}>();

const emit = defineEmits<{
  close: [];
  select: [selection: PlaceSelection];
}>();

const mapElement = ref<HTMLElement | null>(null);
const map = shallowRef<google.maps.Map | null>(null);
const marker = shallowRef<google.maps.Marker | null>(null);
const coverageLayer = shallowRef<google.maps.StreetViewCoverageLayer | null>(null);
const clickListener = shallowRef<google.maps.MapsEventListener | null>(null);
const isLoadingMap = ref(false);
const statusMessage = ref<string | null>(null);
const isError = ref(false);
let initToken = 0;

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      void initMap();
      return;
    }
    teardownMap();
  },
);

onBeforeUnmount(() => {
  teardownMap();
});

function close() {
  emit('close');
}

async function initMap() {
  const token = (initToken += 1);
  isLoadingMap.value = true;
  statusMessage.value = null;
  isError.value = false;

  await nextTick();

  if (!props.open || token !== initToken || !mapElement.value) {
    isLoadingMap.value = false;
    return;
  }

  try {
    const maps = await loadGoogleMaps();
    if (token !== initToken || !mapElement.value) {
      return;
    }

    const instance = new maps.Map(mapElement.value, getKosovoMapPickerOptions());
    instance.getStreetView().setVisible(false);

    const coverage = new maps.StreetViewCoverageLayer();
    coverage.setMap(instance);

    clickListener.value = instance.addListener('click', (event: google.maps.MapMouseEvent) => {
      void onMapClick(event);
    });

    map.value = instance;
    coverageLayer.value = coverage;

    if (props.latitude != null && props.longitude != null) {
      placeMarker(props.latitude, props.longitude);
      instance.panTo({ lat: props.latitude, lng: props.longitude });
      instance.setZoom(15);
    } else {
      instance.setCenter({
        lat: KOSOVO_DEFAULT_VIEWPORT.center.latitude,
        lng: KOSOVO_DEFAULT_VIEWPORT.center.longitude,
      });
      instance.setZoom(10);
    }
  } catch (error) {
    statusMessage.value = getGoogleMapsLoadHint(error);
    isError.value = true;
  } finally {
    if (token === initToken) {
      isLoadingMap.value = false;
    }
  }
}

async function onMapClick(event: google.maps.MapMouseEvent) {
  const latLng = event.latLng;
  if (!latLng || !map.value) {
    return;
  }

  isError.value = false;
  statusMessage.value = 'Checking Street View coverage…';

  const snapped = await snapToStreetViewAtCoordinates(latLng.lat(), latLng.lng());
  if (!snapped) {
    statusMessage.value = 'No Street View here. Tap a blue-covered street in Kosovo.';
    isError.value = true;
    return;
  }

  placeMarker(snapped.latitude, snapped.longitude);

  try {
    const label =
      snapped.description?.trim() ||
      (await reverseGeocodeCoordinates(snapped.latitude, snapped.longitude));

    emit('select', {
      latitude: snapped.latitude,
      longitude: snapped.longitude,
      label,
    });
    statusMessage.value = 'Location added to search.';
    window.setTimeout(close, 350);
  } catch {
    emit('select', {
      latitude: snapped.latitude,
      longitude: snapped.longitude,
      label: `${snapped.latitude.toFixed(5)}, ${snapped.longitude.toFixed(5)}`,
    });
    window.setTimeout(close, 350);
  }
}

function placeMarker(latitude: number, longitude: number) {
  if (!map.value) {
    return;
  }

  const position = { lat: latitude, lng: longitude };
  if (marker.value) {
    marker.value.setPosition(position);
    return;
  }

  marker.value = new google.maps.Marker({
    map: map.value,
    position,
  });
}

function teardownMap() {
  initToken += 1;
  clickListener.value?.remove();
  clickListener.value = null;
  marker.value?.setMap(null);
  marker.value = null;
  coverageLayer.value?.setMap(null);
  coverageLayer.value = null;
  map.value = null;
  statusMessage.value = null;
  isError.value = false;
  isLoadingMap.value = false;
}
</script>

<style scoped>
.location-map-picker {
  position: fixed;
  inset: 0;
  z-index: calc(var(--z-overlay) + 10);
  display: grid;
  place-items: center;
  padding: clamp(1rem, 4vw, 2rem);
  background: rgba(23, 33, 26, 0.45);
  backdrop-filter: blur(6px);
}

.location-map-picker__dialog {
  display: grid;
  gap: var(--space-3);
  width: min(100%, 56rem);
  max-height: min(92vh, 44rem);
  padding: var(--space-4);
}

.location-map-picker__header {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  justify-content: space-between;
}

.location-map-picker__header h2 {
  margin: 0.15rem 0 0;
  font-size: 1.05rem;
  font-weight: 850;
  letter-spacing: -0.02em;
}

.location-map-picker__sub {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: var(--text-xs);
  line-height: 1.45;
}

.location-map-picker__close {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border: 0;
  border-radius: 50%;
  color: var(--text-muted);
  background: rgba(23, 33, 26, 0.06);
  font-size: 1.35rem;
  line-height: 1;
  cursor: pointer;
}

.location-map-picker__close:hover {
  color: var(--text-primary);
  background: rgba(23, 33, 26, 0.1);
}

.location-map-picker__map {
  width: 100%;
  min-height: min(58vh, 28rem);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-map-placeholder);
}

.location-map-picker__status {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 750;
}

.location-map-picker__status--error {
  color: var(--color-repair-red);
}

@media (max-width: 640px) {
  .location-map-picker {
    padding:
      max(0.5rem, env(safe-area-inset-top, 0px))
      max(0.5rem, env(safe-area-inset-right, 0px))
      max(0.5rem, env(safe-area-inset-bottom, 0px))
      max(0.5rem, env(safe-area-inset-left, 0px));
    place-items: stretch;
  }

  .location-map-picker__dialog {
    width: 100%;
    max-height: calc(100dvh - 1rem);
    padding: var(--space-3);
  }

  .location-map-picker__header h2 {
    font-size: 0.95rem;
  }

  .location-map-picker__map {
    min-height: min(52dvh, 22rem);
    flex: 1;
  }
}
</style>
