<template>
  <AppCard class="street-view-panel stack" :class="{ 'street-view-panel--compact': compact }" variant="command">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
        <p>{{ subtitle }}</p>
      </div>
    </div>

    <StreetViewFallbackPanel
      v-if="fallbackReason"
      :description="fallbackDescription"
      :coordinates="targetCoordinates"
      :reason="fallbackReason"
      :target-label="targetLabel"
      :title="fallbackTitle"
    />

    <template v-else>
      <div ref="panoramaElement" class="street-view-panel__canvas" :aria-label="ariaLabel" />

      <div v-if="statusMessage" class="street-view-panel__notice" role="status">
        {{ statusMessage }}
      </div>

      <StreetViewRecordSummary :target="target" />
    </template>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, shallowRef, watch } from 'vue';
import AppCard from '@/components/common/AppCard.vue';
import StreetViewFallbackPanel from '@/components/streetview/StreetViewFallbackPanel.vue';
import StreetViewRecordSummary from '@/components/streetview/StreetViewRecordSummary.vue';
import type { StreetViewTarget, StreetViewCurrentView } from '@/types/streetView';
import { loadGoogleMaps } from '@/utils/googleMaps';
import { formatCoordinates } from '@/utils/reportFormatting';
import {
  getStreetViewPov,
  hasValidCoordinates,
  STREET_VIEW_FALLBACK_RADIUS_METERS,
  STREET_VIEW_SEARCH_RADIUS_METERS,
} from '@/utils/streetView';

const props = withDefaults(
  defineProps<{
    target: StreetViewTarget | null;
    isLoading?: boolean;
    eyebrow?: string;
    title?: string;
    recordCount?: number;
    compact?: boolean;
    trackViewChanges?: boolean;
  }>(),
  {
    isLoading: false,
    eyebrow: 'Street context',
    title: 'Location preview',
    recordCount: 0,
    compact: false,
    trackViewChanges: false,
  },
);

const emit = defineEmits<{
  'view-changed': [view: StreetViewCurrentView];
}>();

const panoramaElement = ref<HTMLElement | null>(null);
const panorama = shallowRef<google.maps.StreetViewPanorama | null>(null);
const streetViewService = shallowRef<google.maps.StreetViewService | null>(null);
const fallbackReason = ref<string | null>(null);
const statusMessage = ref<string | null>(null);
const currentView = ref<StreetViewCurrentView | null>(null);
let lookupToken = 0;
let viewListenerCleanup: (() => void) | null = null;

const subtitle = computed(() => {
  if (props.target) {
    return props.target.label;
  }

  if (props.recordCount > 0) {
    return `Select a record to preview (${props.recordCount} available).`;
  }

  return 'Preview loads when a geolocated record is selected.';
});

const ariaLabel = computed(() =>
  props.target
    ? `Street preview near ${props.target.label}`
    : 'Street preview panel',
);

const targetLabel = computed(() => props.target?.label ?? null);
const targetCoordinates = computed(() =>
  props.target ? formatCoordinates(props.target.latitude, props.target.longitude) : null,
);

const fallbackTitle = computed(() => {
  if (!props.target && !props.isLoading) {
    return 'Select a record to load Street View.';
  }

  return 'Street View context is unavailable.';
});

const fallbackDescription = computed(() => {
  if (props.target?.source === 'audit_suggestion') {
    return 'The suggestion remains reviewable without a street preview.';
  }

  return 'Report details remain available without a street preview.';
});

watch(
  () => props.target,
  () => {
    void loadTarget();
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  lookupToken += 1;
  detachViewListeners();
  panorama.value = null;
  streetViewService.value = null;
  currentView.value = null;
});

function detachViewListeners() {
  viewListenerCleanup?.();
  viewListenerCleanup = null;
}

function syncCurrentView(pano: google.maps.StreetViewPanorama) {
  const position = pano.getPosition();
  const pov = pano.getPov();
  if (!position || !pov) {
    return;
  }

  const view: StreetViewCurrentView = {
    latitude: position.lat(),
    longitude: position.lng(),
    heading: Math.round(pov.heading ?? 0),
    pitch: Math.round(pov.pitch ?? 0),
  };
  currentView.value = view;
  emit('view-changed', view);
}

function attachViewListeners(pano: google.maps.StreetViewPanorama) {
  detachViewListeners();
  if (!props.trackViewChanges) {
    return;
  }

  const positionListener = pano.addListener('position_changed', () => syncCurrentView(pano));
  const povListener = pano.addListener('pov_changed', () => syncCurrentView(pano));
  viewListenerCleanup = () => {
    positionListener.remove();
    povListener.remove();
  };
  syncCurrentView(pano);
}

defineExpose({
  getCurrentView: () => currentView.value,
});

async function ensureGoogleMaps() {
  const maps = await loadGoogleMaps();
  if (!streetViewService.value) {
    streetViewService.value = new maps.StreetViewService();
  }

  if (!panorama.value && panoramaElement.value) {
    panorama.value = new maps.StreetViewPanorama(panoramaElement.value, {
      addressControl: false,
      clickToGo: true,
      fullscreenControl: true,
      linksControl: true,
      motionTracking: false,
      panControl: true,
      showRoadLabels: true,
      visible: true,
      zoomControl: true,
    });
  }

  return maps;
}

async function loadTarget() {
  const token = (lookupToken += 1);
  fallbackReason.value = null;
  statusMessage.value = null;

  if (!props.target) {
    panorama.value = null;
    fallbackReason.value = props.isLoading ? null : 'No report or AI suggestion is selected yet.';
    return;
  }

  if (!hasValidCoordinates(props.target)) {
    panorama.value = null;
    fallbackReason.value = 'The selected record does not have valid latitude and longitude.';
    return;
  }

  await nextTick();

  try {
    const maps = await ensureGoogleMaps();
    if (token !== lookupToken || !streetViewService.value || !panorama.value) {
      return;
    }

    statusMessage.value = 'Loading street preview…';
    const result = await findPanorama(
      maps,
      props.target,
      STREET_VIEW_SEARCH_RADIUS_METERS,
      maps.StreetViewSource.OUTDOOR,
    );
    const panoramaResult =
      result ??
      (await findPanorama(
        maps,
        props.target,
        STREET_VIEW_FALLBACK_RADIUS_METERS,
        maps.StreetViewSource.DEFAULT,
      ));

    if (token !== lookupToken) {
      return;
    }

    if (!panoramaResult) {
      panorama.value = null;
      fallbackReason.value =
        `No street preview found within ${STREET_VIEW_FALLBACK_RADIUS_METERS}m of this location.`;
      statusMessage.value = null;
      return;
    }

    panorama.value.setPano(panoramaResult.location?.pano ?? '');
    const pov = getStreetViewPov(props.target);
    if (pov) {
      panorama.value.setPov(pov);
    }
    panorama.value.setVisible(true);
    attachViewListeners(panorama.value);
    statusMessage.value = panoramaResult.location?.description ?? 'Street preview loaded.';
  } catch (error) {
    if (token !== lookupToken) {
      return;
    }
    fallbackReason.value =
      error instanceof Error ? error.message : 'Street preview could not load.';
    panorama.value = null;
    statusMessage.value = null;
  }
}

function findPanorama(
  maps: typeof google.maps,
  target: StreetViewTarget,
  radius: number,
  source: google.maps.StreetViewSource,
): Promise<google.maps.StreetViewPanoramaData | null> {
  return new Promise((resolve) => {
    streetViewService.value?.getPanorama(
      {
        location: { lat: target.latitude, lng: target.longitude },
        preference: maps.StreetViewPreference.NEAREST,
        radius,
        source,
      },
      (data, status) => {
        resolve(status === maps.StreetViewStatus.OK && data ? data : null);
      },
    );
  });
}
</script>

<style scoped>
.street-view-panel h2,
.street-view-panel p {
  margin: 0;
}

.street-view-panel p:not(.eyebrow) {
  color: var(--text-secondary);
}

.street-view-panel__canvas {
  position: relative;
  min-height: 32rem;
  overflow: hidden;
  border: var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-map-placeholder);
}

.street-view-panel--compact .street-view-panel__canvas {
  min-height: 22rem;
}

.street-view-panel__notice {
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.72);
  font-size: var(--text-sm);
  font-weight: 750;
}

@media (max-width: 980px) {
  .street-view-panel__canvas {
    min-height: 26rem;
  }
}

@media (max-width: 620px) {
  .street-view-panel__canvas {
    min-height: 22rem;
  }
}
</style>
