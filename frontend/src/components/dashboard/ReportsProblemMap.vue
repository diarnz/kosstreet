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

    <div ref="mapElement" class="reports-problem-map__canvas" aria-label="Kosovo issue map" />

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
import { getHiddenMapReportCount, getMappableReports } from '@/utils/map';
import { getKosovoMapPickerOptions } from '@/utils/places';

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
const loadError = ref<string | null>(null);
const isMapReady = ref(false);
let initToken = 0;
let fitBoundsToken = 0;

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
    });
    instance.getStreetView().setVisible(false);

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

  const nextMarkers = new Map<string, google.maps.Marker>();
  const currentIds = new Set(mappableReports.value.map((report) => report.id));

  for (const report of mappableReports.value) {
    const position = { lat: report.latitude, lng: report.longitude };
    const selected = report.id === props.selectedReportId;
    let marker = markersById.value.get(report.id);

    if (marker) {
      marker.setPosition(position);
      marker.setIcon(getCategoryMarkerIcon(report.category, selected));
      marker.setZIndex(selected ? 2 : 1);
    } else {
      marker = new google.maps.Marker({
        map: instance,
        position,
        icon: getCategoryMarkerIcon(report.category, selected),
        title: categoryLabels[report.category],
        zIndex: selected ? 2 : 1,
      });
      marker.addListener('click', () => emit('select', report.id));
    }

    nextMarkers.set(report.id, marker);
  }

  for (const [reportId, marker] of markersById.value.entries()) {
    if (!currentIds.has(reportId)) {
      marker.setMap(null);
    }
  }

  markersById.value = nextMarkers;
}

function updateMarkerSelection() {
  for (const report of mappableReports.value) {
    const marker = markersById.value.get(report.id);
    if (!marker) {
      continue;
    }
    const selected = report.id === props.selectedReportId;
    marker.setIcon(getCategoryMarkerIcon(report.category, selected));
    marker.setZIndex(selected ? 2 : 1);
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

function teardownMap() {
  initToken += 1;
  fitBoundsToken += 1;
  for (const marker of markersById.value.values()) {
    marker.setMap(null);
  }
  markersById.value = new Map();
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
