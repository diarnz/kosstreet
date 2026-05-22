<template>
  <AppCard class="report-map stack" variant="command">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Geospatial view</p>
        <h2>Prishtina report map</h2>
        <p>
          {{ mappableReports.length }} mapped report{{ mappableReports.length === 1 ? '' : 's' }}
          from the current filtered dashboard view.
        </p>
      </div>
      <AppBadge tone="info">Leaflet / OSM</AppBadge>
    </div>

    <MapFallbackPanel
      v-if="mapError"
      :reason="mapError"
      :report-count="reports.length"
    />

    <template v-else>
      <div
        ref="mapElement"
        class="report-map__canvas"
        aria-label="Interactive Prishtina map of real civic reports"
      />

      <div v-if="tileWarning" class="report-map__notice" role="status">
        {{ tileWarning }}
      </div>

      <div v-if="!isLoading && reports.length === 0" class="report-map__notice" role="status">
        No reports are available yet. The map is centered on Prishtina until real reports exist.
      </div>

      <div v-else-if="!isLoading && mappableReports.length === 0" class="report-map__notice" role="status">
        The current reports do not have valid coordinates, so no markers can be mapped.
      </div>

      <div v-else-if="hiddenReportCount > 0" class="report-map__notice" role="status">
        {{ hiddenReportCount }} report{{ hiddenReportCount === 1 ? '' : 's' }} in this view
        {{ hiddenReportCount === 1 ? 'has' : 'have' }} invalid coordinates and remain available in the queue.
      </div>

      <ReportMapPopup :report="selectedMappableReport" />
      <MapLegend />
    </template>
  </AppCard>
</template>

<script setup lang="ts">
import L, { type DivIcon, type LayerGroup, type Map as LeafletMap, type Marker } from 'leaflet';
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import MapFallbackPanel from './MapFallbackPanel.vue';
import MapLegend from './MapLegend.vue';
import ReportMapPopup from './ReportMapPopup.vue';
import type { ReportSummary } from '@/types/report';
import {
  categoryLabels,
  formatConfidence,
  formatCoordinates,
  formatDateTime,
  sourceLabels,
  statusLabels,
} from '@/utils/reportFormatting';
import { escapeHtml, getHiddenMapReportCount, getMappableReports, PRISHTINA_VIEWPORT } from '@/utils/map';

const props = withDefaults(
  defineProps<{
    reports: ReportSummary[];
    selectedReportId: string | null;
    isLoading?: boolean;
  }>(),
  {
    isLoading: false,
  },
);

const emit = defineEmits<{
  select: [reportId: string];
}>();

const mapElement = ref<HTMLElement | null>(null);
const map = shallowRef<LeafletMap | null>(null);
const markerLayer = shallowRef<LayerGroup | null>(null);
const mapError = ref<string | null>(null);
const tileWarning = ref<string | null>(null);

const mappableReports = computed(() => getMappableReports(props.reports));
const hiddenReportCount = computed(() => getHiddenMapReportCount(props.reports));
const selectedMappableReport = computed(
  () => mappableReports.value.find((report) => report.id === props.selectedReportId) ?? null,
);

onMounted(async () => {
  await nextTick();
  initializeMap();
  renderMarkers();
});

onBeforeUnmount(() => {
  map.value?.remove();
  map.value = null;
});

watch(
  () => [props.reports, props.selectedReportId] as const,
  () => {
    renderMarkers();
  },
  { deep: true },
);

function initializeMap() {
  if (!mapElement.value || map.value) {
    return;
  }

  try {
    map.value = L.map(mapElement.value, {
      center: [PRISHTINA_VIEWPORT.center.latitude, PRISHTINA_VIEWPORT.center.longitude],
      zoom: PRISHTINA_VIEWPORT.zoom,
      scrollWheelZoom: false,
    });

    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    });

    tiles.on('tileerror', () => {
      tileWarning.value = 'Map tiles could not fully load. The report queue and details remain available.';
    });

    tiles.addTo(map.value);
    markerLayer.value = L.layerGroup().addTo(map.value);
  } catch (error) {
    mapError.value =
      error instanceof Error ? error.message : 'The map could not initialize in this browser session.';
  }
}

function renderMarkers() {
  if (!map.value || !markerLayer.value) {
    return;
  }

  markerLayer.value.clearLayers();

  const markers: Marker[] = mappableReports.value.map((report) => {
    const isSelected = report.id === props.selectedReportId;
    const marker = L.marker([report.latitude, report.longitude], {
      icon: createReportIcon(report, isSelected),
      title: `${categoryLabels[report.category]} ${formatCoordinates(report.latitude, report.longitude)}`,
      zIndexOffset: isSelected ? 1000 : 0,
    });

    marker.bindPopup(createPopupHtml(report));
    marker.on('click', () => {
      emit('select', report.id);
    });
    marker.addTo(markerLayer.value as LayerGroup);

    return marker;
  });

  fitMapToMarkers(markers);
}

function fitMapToMarkers(markers: Marker[]) {
  if (!map.value) {
    return;
  }

  const selected = selectedMappableReport.value;

  if (selected) {
    map.value.panTo([selected.latitude, selected.longitude]);
    return;
  }

  if (markers.length === 0) {
    map.value.setView(
      [PRISHTINA_VIEWPORT.center.latitude, PRISHTINA_VIEWPORT.center.longitude],
      PRISHTINA_VIEWPORT.zoom,
    );
    return;
  }

  if (markers.length === 1) {
    const position = markers[0].getLatLng();
    map.value.setView(position, Math.max(map.value.getZoom(), 15));
    return;
  }

  const bounds = L.featureGroup(markers).getBounds();
  map.value.fitBounds(bounds, { padding: [42, 42], maxZoom: 16 });
}

function createReportIcon(report: ReportSummary, isSelected: boolean): DivIcon {
  const glyph = getCategoryGlyph(report);
  const classes = [
    'kostreet-map-marker',
    `kostreet-map-marker--${report.category}`,
    `kostreet-map-marker--status-${report.status}`,
    isSelected ? 'kostreet-map-marker--selected' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return L.divIcon({
    className: 'kostreet-map-marker-shell',
    html: `<span class="${classes}" aria-hidden="true">${glyph}</span>`,
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
}

function getCategoryGlyph(report: ReportSummary): string {
  const glyphs: Record<ReportSummary['category'], string> = {
    pothole: 'P',
    garbage: 'G',
    broken_streetlight: 'L',
    blocked_sidewalk: 'S',
    damaged_sign: 'D',
    other: 'O',
  };

  return glyphs[report.category];
}

function createPopupHtml(report: ReportSummary): string {
  const description = report.description ? `<p>${escapeHtml(report.description)}</p>` : '';

  return `
    <article class="kostreet-map-popup">
      <strong>${escapeHtml(categoryLabels[report.category])}</strong>
      <span>${escapeHtml(statusLabels[report.status])} · ${escapeHtml(sourceLabels[report.source])}</span>
      ${description}
      <span>${escapeHtml(formatCoordinates(report.latitude, report.longitude))}</span>
      <span>${escapeHtml(formatDateTime(report.created_at))}</span>
      <span>Confidence: ${escapeHtml(formatConfidence(report.confidence))}</span>
    </article>
  `;
}
</script>

<style scoped>
.report-map h2,
.report-map p {
  margin: 0;
}

.report-map p:not(.eyebrow) {
  color: var(--text-secondary);
}

.report-map__canvas {
  position: relative;
  z-index: 0;
  min-height: 31rem;
  overflow: hidden;
  border: var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-map-placeholder);
}

.report-map__notice {
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.72);
  font-size: var(--text-sm);
  font-weight: 750;
}

:deep(.leaflet-container) {
  font-family: var(--font-sans);
}

:deep(.leaflet-control-attribution),
:deep(.leaflet-control-zoom a) {
  color: var(--text-secondary);
}

:deep(.kostreet-map-marker-shell) {
  width: 0;
  height: 0;
}

:deep(.kostreet-map-marker) {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border: 4px solid var(--status-new-text);
  border-radius: var(--radius-pill);
  color: var(--color-paper);
  background: var(--category-other-text);
  box-shadow: 0 12px 24px rgba(23, 33, 26, 0.28);
  font-size: 0.78rem;
  font-weight: 950;
  transform: translate(-50%, -50%);
}

:deep(.kostreet-map-marker--pothole) {
  background: var(--category-pothole-text);
}

:deep(.kostreet-map-marker--garbage) {
  background: var(--category-garbage-text);
}

:deep(.kostreet-map-marker--broken_streetlight) {
  background: var(--category-broken-streetlight-text);
}

:deep(.kostreet-map-marker--blocked_sidewalk) {
  background: var(--category-blocked-sidewalk-text);
}

:deep(.kostreet-map-marker--damaged_sign) {
  background: var(--category-damaged-sign-text);
}

:deep(.kostreet-map-marker--status-verified) {
  border-color: var(--status-verified-text);
}

:deep(.kostreet-map-marker--status-assigned),
:deep(.kostreet-map-marker--status-resolved) {
  border-color: var(--status-assigned-text);
}

:deep(.kostreet-map-marker--status-in_progress) {
  border-color: var(--status-in-progress-text);
}

:deep(.kostreet-map-marker--status-rejected) {
  border-color: var(--status-rejected-text);
}

:deep(.kostreet-map-marker--selected) {
  width: 2.65rem;
  height: 2.65rem;
  border-color: var(--color-paper);
  outline: 4px solid rgba(47, 93, 80, 0.42);
  box-shadow: 0 18px 36px rgba(23, 33, 26, 0.34);
}

:deep(.kostreet-map-popup) {
  display: grid;
  gap: 0.32rem;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: 0.82rem;
}

:deep(.kostreet-map-popup strong) {
  color: var(--text-primary);
  font-size: 0.95rem;
}

:deep(.kostreet-map-popup p) {
  max-width: 15rem;
  margin: 0;
}

@media (max-width: 980px) {
  .report-map__canvas {
    min-height: 26rem;
  }
}

@media (max-width: 620px) {
  .report-map__canvas {
    min-height: 22rem;
  }
}
</style>
