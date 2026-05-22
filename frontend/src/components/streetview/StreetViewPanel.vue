<template>
  <AppCard class="street-view-panel stack" :class="{ 'street-view-panel--compact': compact }" variant="command">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
        <p>{{ subtitle }}</p>
      </div>
      <AppBadge tone="source-ai-audit">Google Street View</AppBadge>
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
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import StreetViewFallbackPanel from '@/components/streetview/StreetViewFallbackPanel.vue';
import StreetViewRecordSummary from '@/components/streetview/StreetViewRecordSummary.vue';
import type { StreetViewTarget } from '@/types/streetView';
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
  }>(),
  {
    isLoading: false,
    eyebrow: 'Street-level evidence',
    title: 'Google Street View context',
    recordCount: 0,
    compact: false,
  },
);

const panoramaElement = ref<HTMLElement | null>(null);
const panorama = shallowRef<google.maps.StreetViewPanorama | null>(null);
const streetViewService = shallowRef<google.maps.StreetViewService | null>(null);
const fallbackReason = ref<string | null>(null);
const statusMessage = ref<string | null>(null);
let lookupToken = 0;

const subtitle = computed(() => {
  if (props.target) {
    return `Showing the nearest panorama for ${props.target.label}.`;
  }

  if (props.recordCount > 0) {
    return `${props.recordCount} record${props.recordCount === 1 ? '' : 's'} available. Select one to load Street View.`;
  }

  return 'Street View appears when a report or AI suggestion with valid coordinates is selected.';
});

const ariaLabel = computed(() =>
  props.target
    ? `Google Street View panorama near ${props.target.label}`
    : 'Google Street View panorama panel',
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
    return 'The AI suggestion remains reviewable even when nearby Google Street View imagery is unavailable.';
  }

  return 'The report queue and detail panel remain available even when nearby Google Street View imagery is unavailable.';
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
  panorama.value = null;
  streetViewService.value = null;
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

    statusMessage.value = 'Searching for nearby Google Street View imagery...';
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
        `Google did not return a Street View panorama within ${STREET_VIEW_FALLBACK_RADIUS_METERS} meters of this selected record.`;
      statusMessage.value = null;
      return;
    }

    panorama.value.setPano(panoramaResult.location?.pano ?? '');
    const pov = getStreetViewPov(props.target);
    if (pov) {
      panorama.value.setPov(pov);
    }
    panorama.value.setVisible(true);
    statusMessage.value =
      panoramaResult.location?.description ?? 'Nearest Google Street View panorama loaded.';
  } catch (error) {
    if (token !== lookupToken) {
      return;
    }
    fallbackReason.value =
      error instanceof Error ? error.message : 'Google Street View could not initialize.';
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
