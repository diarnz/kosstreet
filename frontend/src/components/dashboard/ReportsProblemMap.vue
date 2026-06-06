<template>
  <section class="reports-problem-map" aria-label="Report locations map">
    <div class="reports-problem-map__toolbar">
      <p class="reports-problem-map__count">
        <span class="reports-problem-map__count-value">{{ mappableReports.length }}</span>
        on map
        <span v-if="hiddenCount > 0" class="reports-problem-map__hidden muted">
          · {{ hiddenCount }} without coordinates
        </span>
      </p>
      
      <ul class="reports-problem-map__legend" aria-label="Issue category legend">
        <li v-for="category in legendCategories" :key="category">
          <img
            class="reports-problem-map__legend-icon"
            :src="legendIconUrls[category]"
            :alt="`${categoryLabels[category]} marker`"
            width="18"
            height="22"
          />
          <span>{{ categoryLabels[category] }}</span>
        </li>
      </ul>
    </div>

    <div class="reports-problem-map__canvas" aria-label="Kosovo issue map">
      <div ref="mapElement" class="reports-problem-map__map" />
      <div class="reports-problem-map__controls">
        <button class="btn btn-icon" @click="fitMapToReports" title="Zoom to reports" aria-label="Fit map">
          <!-- target icon -->
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <path d="M12 8a4 4 0 100 8 4 4 0 000-8z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 12h-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5 12H3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 21v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 5V3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="btn btn-icon" @click="toggleClustering" :aria-pressed="clusterEnabled" title="Toggle clustering" aria-label="Toggle clusters">
          <!-- cluster icon -->
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="17" cy="7" r="2" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="12" cy="15" r="3" stroke="currentColor" stroke-width="1.5"/>
          </svg>
        </button>
      </div>
    </div>

    <p v-if="isLoading" class="reports-problem-map__status muted">Loading map…</p>
    <p v-else-if="loadError" class="reports-problem-map__status reports-problem-map__status--error">
      {{ loadError }}
    </p>
    <p v-else-if="mappableReports.length === 0" class="reports-problem-map__status muted">
      No reports with valid coordinates to plot yet.
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import type { IssueCategory, ReportSummary } from '@/types/report';
import { categoryLabels } from '@/utils/reportFormatting';
import {
  categoryMarkerStyles,
  getCategoryMarkerIcon,
  getCategoryMarkerSvgUrl,
} from '@/utils/categoryMapMarkers';
import { getGoogleMapsLoadHint, loadGoogleMaps } from '@/utils/googleMaps';
import { getHiddenMapReportCount, getMappableReports, escapeHtml } from '@/utils/map';
import { getKosovoMapPickerOptions } from '@/utils/places';
import { resolveApiAssetUrl } from '@/utils/apiAssets';

const props = defineProps<{
  reports: ReportSummary[];
  selectedReportId: string | null;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  select: [reportId: string];
}>();

const legendCategories = Object.keys(categoryMarkerStyles) as IssueCategory[];

const mapElement = ref<HTMLElement | null>(null);
const map = shallowRef<google.maps.Map | null>(null);
const markersById = shallowRef(new Map<string, google.maps.Marker>());
const markersByCoord = shallowRef(new Map<string, google.maps.Marker>());
const coordToReportIds = shallowRef(new Map<string, string[]>());
const clusterEnabled = ref(false);
const markerClusterer = shallowRef<any | null>(null);
let MarkerClustererModule: any = null;
const loadError = ref<string | null>(null);
const isMapReady = ref(false);
let initToken = 0;
let fitBoundsToken = 0;
const infoWindow = shallowRef<google.maps.InfoWindow | null>(null);

const mappableReports = computed(() => getMappableReports(props.reports));
const hiddenCount = computed(() => getHiddenMapReportCount(props.reports));

const legendIconUrls = Object.fromEntries(
  legendCategories.map((category) => [category, getCategoryMarkerSvgUrl(category)]),
) as Record<IssueCategory, string>;

onMounted(() => {
  void initMap();
});

onBeforeUnmount(() => {
  teardownMap();
});

watch(
  () => props.reports,
  () => {
    if (!isMapReady.value) {
      return;
    }
    syncMarkers();
    void fitMapToReports();
  },
  { deep: true },
);

watch(
  () => props.selectedReportId,
  (reportId) => {
    if (!isMapReady.value) {
      return;
    }
    updateMarkerSelection();
    if (reportId) {
      focusSelectedReport(reportId);
    }
  },
);

async function initMap() {
  const token = (initToken += 1);
  loadError.value = null;

  await nextTick();
  if (token !== initToken || !mapElement.value) {
    return;
  }

  try {
    const maps = await loadGoogleMaps();
    if (token !== initToken || !mapElement.value) {
      return;
    }

    const instance = new maps.Map(mapElement.value, {
      ...getKosovoMapPickerOptions(),
      gestureHandling: 'greedy',
      // remove all default UI controls so only the map canvas and markers appear
      disableDefaultUI: true,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
      zoomControl: false,
      keyboardShortcuts: false,
      // always load in satellite mode for the preview
      mapTypeId: 'satellite',
    });

    map.value = instance;
    isMapReady.value = true;
    syncMarkers();
    await fitMapToReports();

    if (props.selectedReportId) {
      focusSelectedReport(props.selectedReportId);
    }
  } catch (error) {
    loadError.value = getGoogleMapsLoadHint(error);
  }
}

function syncMarkers() {
  const instance = map.value;
  if (!instance) {
    return;
  }

  // Group reports by rounded coordinates to avoid duplicate markers at same location
  const groups = new Map<string, ReportSummary[]>();
  for (const report of mappableReports.value) {
    const key = `${report.latitude.toFixed(6)}:${report.longitude.toFixed(6)}`;
    const arr = groups.get(key) ?? [];
    arr.push(report);
    groups.set(key, arr);
  }

  const nextMarkers = new Map<string, google.maps.Marker>();
  const nextMarkersByCoord = new Map<string, google.maps.Marker>();

  // Create or update one marker per coordinate group
  for (const [coordKey, reports] of groups.entries()) {
    const representative = reports[0];
    const position = { lat: representative.latitude, lng: representative.longitude };
    const containsSelected = reports.some((r) => r.id === props.selectedReportId);

    let marker = markersByCoord.value.get(coordKey);
    if (marker) {
      marker.setPosition(position);
      marker.setIcon(getCategoryMarkerIcon(representative.category, containsSelected));
      marker.setZIndex(containsSelected ? 2 : 1);
    } else {
      marker = new google.maps.Marker({
        map: instance,
        position,
        icon: getCategoryMarkerIcon(representative.category, containsSelected),
        title: representative.description ? categoryLabels[representative.category] : categoryLabels[representative.category],
        zIndex: containsSelected ? 2 : 1,
      });
      marker.addListener('click', () => {
        // Emit selection of the representative report and show grouped info
        emit('select', representative.id);
        showReportInfoMultiple(reports, marker);
      });
    }

    nextMarkersByCoord.set(coordKey, marker);
    coordToReportIds.value.set(coordKey, reports.map((r) => r.id));
    // also keep mapping by a representative id for compatibility
    nextMarkers.set(representative.id, marker);
  }

  // remove markers that no longer have groups
  for (const [coord, marker] of markersByCoord.value.entries()) {
    if (!nextMarkersByCoord.has(coord)) {
      marker.setMap(null);
    }
  }

  markersByCoord.value = nextMarkersByCoord;
  markersById.value = nextMarkers;
  void updateClustering();
}

function updateMarkerSelection() {
  for (const [coordKey, marker] of markersByCoord.value.entries()) {
    const ids = coordToReportIds.value.get(coordKey) ?? [];
    const containsSelected = ids.includes(props.selectedReportId ?? '');
    // use first report to decide category for icon
    const repId = ids[0];
    const repReport = mappableReports.value.find((r) => r.id === repId);
    if (!repReport) continue;
    marker.setIcon(getCategoryMarkerIcon(repReport.category, containsSelected));
    marker.setZIndex(containsSelected ? 2 : 1);
  }
}

async function fitMapToReports() {
  const instance = map.value;
  if (!instance || mappableReports.value.length === 0) {
    return;
  }

  const token = (fitBoundsToken += 1);
  await nextTick();
  if (token !== fitBoundsToken || !map.value) {
    return;
  }

  if (mappableReports.value.length === 1) {
    const report = mappableReports.value[0];
    instance.setCenter({ lat: report.latitude, lng: report.longitude });
    instance.setZoom(15);
    return;
  }

  const bounds = new google.maps.LatLngBounds();
  for (const report of mappableReports.value) {
    bounds.extend({ lat: report.latitude, lng: report.longitude });
  }
  instance.fitBounds(bounds, 48);
}

function focusSelectedReport(reportId: string) {
  const instance = map.value;
  const report = mappableReports.value.find((item) => item.id === reportId);
  if (!instance || !report) {
    return;
  }

  instance.panTo({ lat: report.latitude, lng: report.longitude });
}

async function ensureMarkerClusterer() {
  if (MarkerClustererModule) return MarkerClustererModule;
  MarkerClustererModule = await import('@googlemaps/markerclusterer');
  return MarkerClustererModule;
}

async function updateClustering() {
  const instance = map.value;
  if (!instance) return;

  // clear existing clusterer
  if (markerClusterer.value) {
    try {
      markerClusterer.value.clearMarkers?.();
    } catch (e) {
      // ignore
    }
    markerClusterer.value = null;
  }

  if (!clusterEnabled.value) {
    // ensure all markers are on the map
    for (const marker of markersByCoord.value.values()) {
      marker.setMap(instance);
    }
    return;
  }

  try {
    const mod = await ensureMarkerClusterer();
    const MarkerClusterer = mod.MarkerClusterer || mod.default || mod;
    const markers = Array.from(markersByCoord.value.values());
    markerClusterer.value = new MarkerClusterer({ map: instance, markers });
  } catch (error) {
    // failing to load clusterer shouldn't break map
    // eslint-disable-next-line no-console
    console.warn('MarkerClusterer not available', error);
  }
}


function toggleClustering() {
  clusterEnabled.value = !clusterEnabled.value;
  void updateClustering();
}



function createInfoWindowContent(report: ReportSummary) {
  const title = categoryLabels[report.category] || 'Issue';
  const description = (report.description || '').replace(/\n/g, '<br/>');
  const thumbUrl = report.image_url ? resolveApiAssetUrl(report.image_url) : null;
  const thumb = thumbUrl ? `<img src="${thumbUrl}" style="width:120px;height:auto;border-radius:6px;margin-bottom:6px;"/>` : '';
  const status = report.status ? `<div style="font-weight:700;margin-top:6px;">Status: ${report.status}</div>` : '';
  return `<div style="max-width:240px;font-size:13px;line-height:1.2;color:#111">${thumb}<div style="font-weight:800;margin-bottom:6px;">${title}</div><div>${description}</div>${status}</div>`;
}

function showReportInfo(report: ReportSummary, marker: google.maps.Marker) {
  if (!map.value) return;
  if (!infoWindow.value) {
    infoWindow.value = new google.maps.InfoWindow();
  }
  const content = createInfoWindowContent(report);
  infoWindow.value.setContent(content);
  infoWindow.value.open({ anchor: marker, map: map.value });
}

function createInfoWindowContentForMultiple(reports: ReportSummary[]) {
  const items = reports
    .map((r) => {
      const title = escapeHtml(categoryLabels[r.category] || 'Issue');
      const desc = escapeHtml(r.description ?? '');
      const thumbUrl = r.image_url ? resolveApiAssetUrl(r.image_url) : null;
      const thumb = thumbUrl ? `<img src="${thumbUrl}" style="width:80px;height:auto;border-radius:6px;margin-right:8px;"/>` : '';
      return `<div style="display:flex;align-items:flex-start;margin-bottom:8px;">${thumb}<div style="font-size:13px;"><div style="font-weight:700">${title}</div><div style="color:#333">${desc}</div></div></div>`;
    })
    .join('');
  return `<div style="max-width:320px;font-size:13px;line-height:1.2;color:#111">${items}</div>`;
}

function showReportInfoMultiple(reports: ReportSummary[], marker: google.maps.Marker) {
  if (!map.value) return;
  if (!infoWindow.value) {
    infoWindow.value = new google.maps.InfoWindow();
  }
  const content = createInfoWindowContentForMultiple(reports);
  infoWindow.value.setContent(content);
  infoWindow.value.open({ anchor: marker, map: map.value });
}

function teardownMap() {
  initToken += 1;
  fitBoundsToken += 1;
  for (const marker of markersByCoord.value.values()) {
    marker.setMap(null);
  }
  markersByCoord.value = new Map();
  markersById.value = new Map();
  coordToReportIds.value = new Map();
  if (markerClusterer.value) {
    try {
      markerClusterer.value.clearMarkers?.();
    } catch (e) {
      // ignore
    }
    markerClusterer.value = null;
  }
  map.value = null;
  isMapReady.value = false;
  loadError.value = null;

  if (mapElement.value) {
    mapElement.value.replaceChildren();
  }
}
</script>

<style scoped>
.reports-problem-map {
  display: grid;
  gap: var(--space-3);
  min-width: 0;
}

.reports-problem-map__toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  justify-content: space-between;
}

.reports-problem-map__count {
  margin: 0;
  font-size: var(--text-xs);
  font-weight: 750;
  color: var(--text-secondary);
}

.reports-problem-map__count-value {
  color: var(--color-municipal-green);
  font-weight: 850;
}

.reports-problem-map__hidden {
  font-weight: 650;
}

.reports-problem-map__legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 0.85rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.reports-problem-map {
  position: relative;
}

.reports-problem-map__canvas {
  position: relative;
}

.reports-problem-map__map {
  width: 100%;
  min-height: 18rem;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-map-placeholder);
}

.reports-problem-map__controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  z-index: 30;
}

.reports-problem-map__controls .btn {
  background: transparent;
  border: none;
  padding: 0;
}

.reports-problem-map__controls .btn-icon {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border-radius: 50%;
  background: rgba(0,0,0,0.6);
  color: #fff;
  box-shadow: 0 6px 18px rgba(10,10,10,0.3);
  transition: transform 120ms ease, background 120ms ease;
}

.reports-problem-map__controls .btn-icon:hover {
  transform: translateY(-2px);
  background: rgba(0,0,0,0.72);
}

.reports-problem-map__controls .btn-icon[aria-pressed="true"] {
  background: var(--color-municipal-green);
  color: #fff;
}

.reports-problem-map__legend li {
  display: inline-flex;
  gap: 0.3rem;
  align-items: center;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}

.reports-problem-map__legend-icon {
  display: block;
  flex-shrink: 0;
}

.reports-problem-map__canvas {
  width: 100%;
  min-height: 18rem;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-map-placeholder);
}

.reports-problem-map__status {
  margin: 0;
  font-size: var(--text-xs);
  font-weight: 700;
}

.reports-problem-map__status--error {
  color: var(--color-repair-red);
}
</style>
