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

      <div class="reports-problem-map__toolbar-actions">
        <label class="reports-problem-map__style-picker">
          <span class="sr-only">Map style</span>
          <select v-model="mapStyleKey" class="reports-problem-map__style-select" @change="applyMapStyle">
            <option v-for="(label, key) in styleLabels" :key="key" :value="key">
              {{ label }}
            </option>
          </select>
        </label>

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
    </div>

    <div class="reports-problem-map__canvas" aria-label="Kosovo issue map">
      <div ref="mapElement" class="reports-problem-map__map" />

      <div class="reports-problem-map__controls">
        <div class="reports-problem-map__control-group">
          <button
            class="reports-problem-map__control-btn"
            type="button"
            title="Zoom in"
            aria-label="Zoom in"
            @click="zoomBy(1)"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>
          <button
            class="reports-problem-map__control-btn"
            type="button"
            title="Zoom out"
            aria-label="Zoom out"
            @click="zoomBy(-1)"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <div class="reports-problem-map__control-group">
          <button
            class="reports-problem-map__control-btn"
            type="button"
            title="Zoom to reports"
            aria-label="Fit map to reports"
            @click="fitMapToReports"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M12 8a4 4 0 100 8 4 4 0 000-8z"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path d="M21 12h-2M5 12H3M12 21v-2M12 5V3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </button>
          <button
            class="reports-problem-map__control-btn"
            type="button"
            title="Toggle clustering"
            aria-label="Toggle clusters"
            :aria-pressed="clusterEnabled"
            @click="toggleClustering"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.5" />
              <circle cx="17" cy="7" r="2" stroke="currentColor" stroke-width="1.5" />
              <circle cx="12" cy="15" r="3" stroke="currentColor" stroke-width="1.5" />
            </svg>
          </button>
        </div>
      </div>

      <Transition name="map-popup">
        <div
          v-if="popupReports.length"
          class="reports-problem-map__popup-scrim"
          aria-modal="true"
          @click.self="closePopup"
        >
          <div
            class="reports-problem-map__popup-overlay"
            role="dialog"
            :aria-label="popupReports.length > 1 ? 'Reports at this location' : 'Selected report'"
            @click.stop
          >
            <article
              v-for="report in popupReports"
              :key="report.id"
              class="reports-problem-map__popup-card"
            >
              <div
                class="reports-problem-map__popup-accent-bar"
                :style="{ backgroundColor: categoryMarkerStyles[report.category].fill }"
              />
              <div v-if="report.image_url" class="reports-problem-map__popup-media">
                <img :src="resolveApiAssetUrl(report.image_url)" alt="" loading="lazy" />
              </div>
              <div class="reports-problem-map__popup-body">
                <div class="reports-problem-map__popup-head">
                  <div class="reports-problem-map__popup-title-row">
                    <img
                      class="reports-problem-map__popup-pin"
                      :src="getCategoryMarkerSvgUrl(report.category)"
                      alt=""
                      width="20"
                      height="24"
                    />
                    <span class="reports-problem-map__popup-category">{{ categoryLabels[report.category] }}</span>
                  </div>
                  <span
                    class="reports-problem-map__popup-status"
                    :class="`reports-problem-map__popup-status--${report.status}`"
                  >
                    {{ statusLabels[report.status] }}
                  </span>
                </div>
                <p class="reports-problem-map__popup-desc">
                  {{ report.description ?? 'No description provided.' }}
                </p>
              </div>
            </article>
            <button
              type="button"
              class="reports-problem-map__popup-dismiss"
              aria-label="Close report details"
              title="Close"
              @click="closePopup"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>
        </div>
      </Transition>

      <div v-if="mapLoading" class="reports-problem-map__loader" aria-hidden="true">
        <span /><span /><span />
      </div>
    </div>

    <p v-if="isMapReady" class="reports-problem-map__attribution muted">
      {{ mapAttribution }}
    </p>

    <p v-if="isLoading" class="reports-problem-map__status muted">Loading reports…</p>
    <p v-else-if="loadError" class="reports-problem-map__status reports-problem-map__status--error">
      {{ loadError }}
    </p>
    <p v-else-if="mappableReports.length === 0" class="reports-problem-map__status muted">
      No reports with valid coordinates to plot yet.
    </p>
  </section>
</template>

<script setup lang="ts">
import maplibregl, { type GeoJSONSource, type Map as MapLibreMap, type Marker } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import type { IssueCategory, ReportSummary } from '@/types/report';
import { useDarkMode } from '@/composables/useDarkMode';
import { categoryLabels, statusLabels } from '@/utils/reportFormatting';
import {
  categoryMarkerStyles,
  getCategoryMarkerSvgUrl,
} from '@/utils/categoryMapMarkers';
import { resolveApiAssetUrl } from '@/utils/apiAssets';
import {
  isMapLibre3dStyle,
  MAPLIBRE_STYLE_LABELS,
  resolveMapStyleUrl,
  type MapLibreStyleKey,
} from '@/utils/mapLibreStyles';
import {
  getHiddenMapReportCount,
  getMappableReports,
  KOSOVO_BOUNDS,
  KOSOVO_DEFAULT_VIEWPORT,
} from '@/utils/map';

const props = defineProps<{
  reports: ReportSummary[];
  selectedReportId: string | null;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  select: [reportId: string];
}>();

const CLUSTER_SOURCE_ID = 'reports-cluster-source';
const CLUSTER_LAYER_ID = 'reports-clusters';
const CLUSTER_COUNT_LAYER_ID = 'reports-cluster-count';
const UNCLUSTERED_LAYER_ID = 'reports-unclustered';

const { isDark } = useDarkMode();

const legendCategories = Object.keys(categoryMarkerStyles) as IssueCategory[];
const styleLabels = MAPLIBRE_STYLE_LABELS;

const mapElement = ref<HTMLElement | null>(null);
const map = shallowRef<MapLibreMap | null>(null);
const htmlMarkers = shallowRef<Marker[]>([]);
const popupReports = ref<ReportSummary[]>([]);
const clusterEnabled = ref(false);
const mapStyleKey = ref<MapLibreStyleKey>('carto');
const mapLoading = ref(true);
const loadError = ref<string | null>(null);
const isMapReady = ref(false);
const coordGroups = shallowRef(new Map<string, ReportSummary[]>());

let initToken = 0;
let fitBoundsToken = 0;
let focusReportToken = 0;
let lastFitSignature = '';
let clusterClickHandler: ((event: maplibregl.MapLayerMouseEvent) => void) | null = null;
let pointClickHandler: ((event: maplibregl.MapLayerMouseEvent) => void) | null = null;
let clusterEnterHandler: (() => void) | null = null;
let clusterLeaveHandler: (() => void) | null = null;
let pointEnterHandler: (() => void) | null = null;
let pointLeaveHandler: (() => void) | null = null;
let styleReadyTimeout: ReturnType<typeof setTimeout> | null = null;
let styleIdleHandler: (() => void) | null = null;
let styleSwitchToken = 0;
let mapBackgroundClickHandler: ((event: maplibregl.MapMouseEvent) => void) | null = null;

const mappableReports = computed(() => getMappableReports(props.reports));
const is3dActive = computed(() => isMapLibre3dStyle(mapStyleKey.value));
const hiddenCount = computed(() => getHiddenMapReportCount(props.reports));

const mapAttribution = '© KoStreet · © contributor';

const legendIconUrls = Object.fromEntries(
  legendCategories.map((category) => [category, getCategoryMarkerSvgUrl(category)]),
) as Record<IssueCategory, string>;

onMounted(() => {
  void initMap();
});

onBeforeUnmount(() => {
  teardownMap();
});

function mappableReportsSignature(): string {
  return mappableReports.value
    .map((report) => `${report.id}:${report.latitude}:${report.longitude}`)
    .sort()
    .join('|');
}

watch(
  () => props.reports,
  () => {
    if (!isMapReady.value) {
      return;
    }
    rebuildCoordGroups();
    syncMarkers();

    const signature = mappableReportsSignature();
    if (signature === lastFitSignature) {
      return;
    }
    lastFitSignature = signature;
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
    syncMarkers();
    if (reportId) {
      void focusOnReport(reportId);
    }
  },
);

watch(isDark, () => {
  if (!isMapReady.value || is3dActive.value) {
    return;
  }
  applyMapStyle();
});

async function initMap() {
  const token = (initToken += 1);
  loadError.value = null;
  mapLoading.value = true;

  await nextTick();
  if (token !== initToken || !mapElement.value) {
    mapLoading.value = false;
    return;
  }

  try {
    const is3d = isMapLibre3dStyle(mapStyleKey.value);

    const instance = new maplibregl.Map({
      container: mapElement.value,
      style: resolveMapStyleUrl(mapStyleKey.value, isDark.value),
      center: [KOSOVO_DEFAULT_VIEWPORT.center.longitude, KOSOVO_DEFAULT_VIEWPORT.center.latitude],
      zoom: KOSOVO_DEFAULT_VIEWPORT.zoom,
      pitch: is3d ? 60 : 0,
      maxBounds: [
        [KOSOVO_BOUNDS.west, KOSOVO_BOUNDS.south],
        [KOSOVO_BOUNDS.east, KOSOVO_BOUNDS.north],
      ],
      attributionControl: false,
      renderWorldCopies: false,
    });

    instance.on('load', () => {
      if (token !== initToken) {
        return;
      }
      map.value = instance;
      isMapReady.value = true;
      mapLoading.value = false;
      rebuildCoordGroups();
      ensureClusterSource();
      syncMarkers();
      void fitMapToReports();
      applyMapPitch();

      mapBackgroundClickHandler = (event) => {
        const layerIds = [CLUSTER_LAYER_ID, UNCLUSTERED_LAYER_ID].filter((layerId) => instance.getLayer(layerId));
        if (layerIds.length === 0) {
          return;
        }

        const hit = instance.queryRenderedFeatures(event.point, { layers: layerIds });
        if (hit.length === 0) {
          closePopup();
        }
      };
      instance.on('click', mapBackgroundClickHandler);
    });

    instance.on('error', (event) => {
      if (event.error?.message) {
        loadError.value = `Map failed to load: ${event.error.message}`;
        mapLoading.value = false;
      }
    });
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Map could not be initialized.';
    mapLoading.value = false;
  }
}

function rebuildCoordGroups() {
  const groups = new Map<string, ReportSummary[]>();
  for (const report of mappableReports.value) {
    const key = `${report.latitude.toFixed(6)}:${report.longitude.toFixed(6)}`;
    const existing = groups.get(key) ?? [];
    existing.push(report);
    groups.set(key, existing);
  }
  coordGroups.value = groups;
}

function buildGeoJson(): GeoJSON.FeatureCollection<GeoJSON.Point> {
  const features: GeoJSON.Feature<GeoJSON.Point>[] = [];

  for (const reports of coordGroups.value.values()) {
    const representative = reports[0];
    features.push({
      type: 'Feature',
      properties: {
        reportId: representative.id,
        category: representative.category,
        color: categoryMarkerStyles[representative.category].fill,
        count: reports.length,
      },
      geometry: {
        type: 'Point',
        coordinates: [representative.longitude, representative.latitude],
      },
    });
  }

  return { type: 'FeatureCollection', features };
}

function ensureClusterSource() {
  const instance = map.value;
  if (!instance || instance.getSource(CLUSTER_SOURCE_ID)) {
    updateClusterData();
    return;
  }

  instance.addSource(CLUSTER_SOURCE_ID, {
    type: 'geojson',
    data: buildGeoJson(),
    cluster: true,
    clusterMaxZoom: 14,
    clusterRadius: 50,
  });

  instance.addLayer({
    id: CLUSTER_LAYER_ID,
    type: 'circle',
    source: CLUSTER_SOURCE_ID,
    filter: ['has', 'point_count'],
    paint: {
      'circle-color': ['step', ['get', 'point_count'], '#22c55e', 5, '#eab308', 15, '#ef4444'],
      'circle-radius': ['step', ['get', 'point_count'], 18, 5, 24, 15, 30],
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
      'circle-opacity': 0.9,
    },
  });

  instance.addLayer({
    id: CLUSTER_COUNT_LAYER_ID,
    type: 'symbol',
    source: CLUSTER_SOURCE_ID,
    filter: ['has', 'point_count'],
    layout: {
      'text-field': '{point_count_abbreviated}',
      'text-size': 12,
    },
    paint: {
      'text-color': '#ffffff',
    },
  });

  instance.addLayer({
    id: UNCLUSTERED_LAYER_ID,
    type: 'circle',
    source: CLUSTER_SOURCE_ID,
    filter: ['!', ['has', 'point_count']],
    paint: {
      'circle-color': ['get', 'color'],
      'circle-radius': 8,
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
    },
  });

  attachClusterHandlers();
  setClusterLayersVisible(clusterEnabled.value);
}

function attachClusterHandlers() {
  const instance = map.value;
  if (!instance) {
    return;
  }

  if (clusterClickHandler) {
    instance.off('click', CLUSTER_LAYER_ID, clusterClickHandler);
  }
  if (pointClickHandler) {
    instance.off('click', UNCLUSTERED_LAYER_ID, pointClickHandler);
  }
  if (clusterEnterHandler) {
    instance.off('mouseenter', CLUSTER_LAYER_ID, clusterEnterHandler);
  }
  if (clusterLeaveHandler) {
    instance.off('mouseleave', CLUSTER_LAYER_ID, clusterLeaveHandler);
  }
  if (pointEnterHandler) {
    instance.off('mouseenter', UNCLUSTERED_LAYER_ID, pointEnterHandler);
  }
  if (pointLeaveHandler) {
    instance.off('mouseleave', UNCLUSTERED_LAYER_ID, pointLeaveHandler);
  }

  clusterClickHandler = async (event) => {
    const features = instance.queryRenderedFeatures(event.point, { layers: [CLUSTER_LAYER_ID] });
    const clusterFeature = features[0];
    if (!clusterFeature) {
      return;
    }

    const clusterId = clusterFeature.properties?.cluster_id as number | undefined;
    const source = instance.getSource(CLUSTER_SOURCE_ID) as GeoJSONSource | undefined;
    if (clusterId == null || !source) {
      return;
    }

    const expansionZoom = Math.min(await source.getClusterExpansionZoom(clusterId), 18);
    const coordinates = (clusterFeature.geometry as GeoJSON.Point).coordinates as [number, number];
    instance.easeTo({ center: coordinates, zoom: expansionZoom, duration: 450 });
  };

  pointClickHandler = (event) => {
    const feature = event.features?.[0];
    const reportId = feature?.properties?.reportId as string | undefined;
    if (!reportId) {
      return;
    }

    const reports = findReportsById(reportId);
    emit('select', reportId);
    if (reports.length) {
      showPopupForReports(reports);
    }
  };

  instance.on('click', CLUSTER_LAYER_ID, clusterClickHandler);
  instance.on('click', UNCLUSTERED_LAYER_ID, pointClickHandler);

  clusterEnterHandler = () => {
    instance.getCanvas().style.cursor = 'pointer';
  };
  clusterLeaveHandler = () => {
    instance.getCanvas().style.cursor = '';
  };
  pointEnterHandler = () => {
    instance.getCanvas().style.cursor = 'pointer';
  };
  pointLeaveHandler = () => {
    instance.getCanvas().style.cursor = '';
  };

  instance.on('mouseenter', CLUSTER_LAYER_ID, clusterEnterHandler);
  instance.on('mouseleave', CLUSTER_LAYER_ID, clusterLeaveHandler);
  instance.on('mouseenter', UNCLUSTERED_LAYER_ID, pointEnterHandler);
  instance.on('mouseleave', UNCLUSTERED_LAYER_ID, pointLeaveHandler);
}

function updateClusterData() {
  const instance = map.value;
  if (!instance) {
    return;
  }

  const source = instance.getSource(CLUSTER_SOURCE_ID) as GeoJSONSource | undefined;
  source?.setData(buildGeoJson());
}

function setClusterLayersVisible(visible: boolean) {
  const instance = map.value;
  if (!instance) {
    return;
  }

  for (const layerId of [CLUSTER_LAYER_ID, CLUSTER_COUNT_LAYER_ID, UNCLUSTERED_LAYER_ID]) {
    if (!instance.getLayer(layerId)) {
      continue;
    }
    instance.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
  }
}

function clearHtmlMarkers() {
  for (const marker of htmlMarkers.value) {
    marker.remove();
  }
  htmlMarkers.value = [];
}

function syncMarkers() {
  const instance = map.value;
  if (!instance) {
    return;
  }

  rebuildCoordGroups();
  updateClusterData();

  if (clusterEnabled.value) {
    clearHtmlMarkers();
    setClusterLayersVisible(true);
    return;
  }

  setClusterLayersVisible(false);
  clearHtmlMarkers();

  const nextMarkers: Marker[] = [];
  for (const reports of coordGroups.value.values()) {
    const representative = reports[0];
    const containsSelected = reports.some((report) => report.id === props.selectedReportId);
    const markerElement = document.createElement('button');
    markerElement.type = 'button';
    markerElement.className = 'reports-problem-map__pin';
    markerElement.setAttribute('aria-label', categoryLabels[representative.category]);
    markerElement.innerHTML = `<img src="${getCategoryMarkerSvgUrl(representative.category, containsSelected)}" alt="" width="${containsSelected ? 44 : 36}" height="${containsSelected ? 52 : 44}" />`;

    markerElement.addEventListener('click', (event) => {
      event.stopPropagation();
      emit('select', representative.id);
      showPopupForReports(reports);
    });

    const marker = new maplibregl.Marker({ element: markerElement, anchor: 'bottom' })
      .setLngLat([representative.longitude, representative.latitude])
      .addTo(instance);

    nextMarkers.push(marker);
  }

  htmlMarkers.value = nextMarkers;
}

function findReportsById(reportId: string): ReportSummary[] {
  for (const reports of coordGroups.value.values()) {
    if (reports.some((report) => report.id === reportId)) {
      return reports;
    }
  }
  return [];
}

function findReportById(reportId: string): ReportSummary | null {
  return mappableReports.value.find((report) => report.id === reportId) ?? null;
}

async function focusOnReport(reportId: string) {
  const instance = map.value;
  const report = findReportById(reportId);
  if (!instance || !report) {
    return;
  }

  const token = (focusReportToken += 1);
  await nextTick();
  if (token !== focusReportToken || !map.value) {
    return;
  }

  const targetZoom = is3dActive.value ? 16 : 15;
  instance.easeTo({
    center: [report.longitude, report.latitude],
    zoom: targetZoom,
    pitch: is3dActive.value ? 60 : 0,
    duration: 500,
  });
}

function setMapInteractionLocked(locked: boolean) {
  const instance = map.value;
  if (!instance) {
    return;
  }

  const handlers = [
    instance.dragPan,
    instance.scrollZoom,
    instance.boxZoom,
    instance.dragRotate,
    instance.keyboard,
    instance.doubleClickZoom,
    instance.touchZoomRotate,
  ];

  for (const handler of handlers) {
    if (locked) {
      handler.disable();
    } else {
      handler.enable();
    }
  }
}

function showPopupForReports(reports: ReportSummary[]) {
  popupReports.value = reports;
  setMapInteractionLocked(true);
}

function closePopup() {
  popupReports.value = [];
  setMapInteractionLocked(false);
}

function applyMapPitch() {
  const instance = map.value;
  if (!instance) {
    return;
  }

  const pitch = is3dActive.value ? 60 : 0;
  if (Math.abs(instance.getPitch() - pitch) < 0.5) {
    return;
  }

  instance.easeTo({ pitch, duration: 450 });
}

function clearStyleSwitchWaiters(instance: MapLibreMap) {
  if (styleIdleHandler) {
    instance.off('idle', styleIdleHandler);
    styleIdleHandler = null;
  }
  if (styleReadyTimeout) {
    clearTimeout(styleReadyTimeout);
    styleReadyTimeout = null;
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

  const targetZoom = is3dActive.value ? 16 : 15;

  if (mappableReports.value.length === 1) {
    const report = mappableReports.value[0];
    instance.easeTo({
      center: [report.longitude, report.latitude],
      zoom: targetZoom,
      pitch: is3dActive.value ? 60 : 0,
      duration: 500,
    });
    return;
  }

  const bounds = new maplibregl.LngLatBounds();
  for (const report of mappableReports.value) {
    bounds.extend([report.longitude, report.latitude]);
  }
  instance.fitBounds(bounds, { padding: 48, duration: 500, maxZoom: targetZoom });
  instance.once('moveend', () => applyMapPitch());
}

function zoomBy(delta: number) {
  const instance = map.value;
  if (!instance) {
    return;
  }
  instance.easeTo({ zoom: instance.getZoom() + delta, duration: 250 });
}

function toggleClustering() {
  clusterEnabled.value = !clusterEnabled.value;
  syncMarkers();
}

function finishStyleSwitch(instance: MapLibreMap) {
  clearStyleSwitchWaiters(instance);
  mapLoading.value = false;
  ensureClusterSource();
  syncMarkers();
  void fitMapToReports();
  applyMapPitch();
}

function applyMapStyle() {
  const instance = map.value;
  if (!instance) {
    return;
  }

  const token = (styleSwitchToken += 1);
  loadError.value = null;
  mapLoading.value = true;
  clearStyleSwitchWaiters(instance);

  const done = () => {
    if (token !== styleSwitchToken) {
      return;
    }
    finishStyleSwitch(instance);
  };

  styleIdleHandler = () => {
    if (!instance.isStyleLoaded()) {
      return;
    }
    done();
  };
  instance.on('idle', styleIdleHandler);

  styleReadyTimeout = setTimeout(done, 1500);

  instance.setStyle(resolveMapStyleUrl(mapStyleKey.value, isDark.value));
}

function teardownMap() {
  initToken += 1;
  fitBoundsToken += 1;
  if (map.value) {
    clearStyleSwitchWaiters(map.value);
  }
  closePopup();
  clearHtmlMarkers();

  const instance = map.value;
  if (instance) {
    if (mapBackgroundClickHandler) {
      instance.off('click', mapBackgroundClickHandler);
      mapBackgroundClickHandler = null;
    }
    if (clusterClickHandler) {
      instance.off('click', CLUSTER_LAYER_ID, clusterClickHandler);
    }
    if (pointClickHandler) {
      instance.off('click', UNCLUSTERED_LAYER_ID, pointClickHandler);
    }
    if (clusterEnterHandler) {
      instance.off('mouseenter', CLUSTER_LAYER_ID, clusterEnterHandler);
    }
    if (clusterLeaveHandler) {
      instance.off('mouseleave', CLUSTER_LAYER_ID, clusterLeaveHandler);
    }
    if (pointEnterHandler) {
      instance.off('mouseenter', UNCLUSTERED_LAYER_ID, pointEnterHandler);
    }
    if (pointLeaveHandler) {
      instance.off('mouseleave', UNCLUSTERED_LAYER_ID, pointLeaveHandler);
    }
    instance.remove();
  }

  map.value = null;
  isMapReady.value = false;
  mapLoading.value = false;
  loadError.value = null;
}
</script>

<style scoped>
.reports-problem-map {
  display: grid;
  gap: var(--space-3);
  min-width: 0;
  position: relative;
}

.reports-problem-map__toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  justify-content: space-between;
}

.reports-problem-map__toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
}

.reports-problem-map__style-picker {
  display: inline-flex;
}

.reports-problem-map__style-select {
  border: 1px solid var(--status-new-border);
  border-radius: var(--radius-md);
  background: var(--surface-inset);
  color: var(--text-primary);
  font-size: var(--text-xs);
  font-weight: 700;
  padding: 0.35rem 0.55rem;
  color-scheme: light dark;
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
  position: relative;
  width: 100%;
  min-height: 18rem;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-map-placeholder);
}

.reports-problem-map__map {
  width: 100%;
  min-height: 18rem;
}

.reports-problem-map__controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.reports-problem-map__control-group {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--radius-md);
  border: 1px solid var(--status-new-border);
  background: var(--surface-panel-strong);
  box-shadow: var(--shadow-card);
}

.reports-problem-map__control-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: 0;
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
}

.reports-problem-map__control-btn + .reports-problem-map__control-btn {
  border-top: 1px solid var(--status-new-border);
}

.reports-problem-map__control-btn:hover {
  background: var(--color-success-surface);
}

.reports-problem-map__control-btn[aria-pressed='true'] {
  background: var(--color-municipal-green);
  color: #fff;
}

.reports-problem-map__loader {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  background: rgba(248, 245, 238, 0.42);
  pointer-events: none;
}

:global(html.dark) .reports-problem-map__loader {
  background: rgba(16, 20, 18, 0.62);
}

:global(html.dark) .reports-problem-map__style-select {
  color-scheme: dark;
}

.reports-problem-map__loader span {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: var(--color-municipal-green);
  animation: reports-map-pulse 1.1s infinite ease-in-out;
}

.reports-problem-map__loader span:nth-child(2) {
  animation-delay: 0.15s;
}

.reports-problem-map__loader span:nth-child(3) {
  animation-delay: 0.3s;
}

.reports-problem-map__status {
  margin: 0;
  font-size: var(--text-xs);
  font-weight: 700;
}

.reports-problem-map__status--error {
  color: var(--color-repair-red);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.map-popup-enter-active,
.map-popup-leave-active {
  transition: opacity 240ms ease;
}

.map-popup-enter-active .reports-problem-map__popup-overlay,
.map-popup-leave-active .reports-problem-map__popup-overlay {
  transition:
    transform 280ms cubic-bezier(0.22, 1, 0.36, 1),
    opacity 240ms ease;
}

.map-popup-enter-from,
.map-popup-leave-to {
  opacity: 0;
}

.map-popup-enter-from .reports-problem-map__popup-overlay,
.map-popup-leave-to .reports-problem-map__popup-overlay {
  opacity: 0;
  transform: scale(0.9);
}

.reports-problem-map__popup-scrim {
  position: absolute;
  inset: 0;
  z-index: 4;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  background: rgba(248, 245, 238, 0.42);
  backdrop-filter: blur(10px) saturate(1.1);
  -webkit-backdrop-filter: blur(10px) saturate(1.1);
}

:global(html.dark) .reports-problem-map__popup-scrim {
  background: rgba(8, 12, 10, 0.52);
}

.reports-problem-map__popup-overlay {
  position: relative;
  width: min(300px, calc(100% - 1.5rem));
  transform: scale(1);
  border-radius: calc(var(--radius-lg) + 2px);
  border: 1px solid var(--status-new-border);
  background: var(--surface-panel-strong);
  color: var(--text-primary);
  box-shadow:
    0 24px 48px rgba(16, 20, 18, 0.22),
    0 8px 16px rgba(16, 20, 18, 0.12);
  overflow: hidden;
  pointer-events: auto;
}

:global(html.dark) .reports-problem-map__popup-overlay {
  box-shadow:
    0 28px 56px rgba(0, 0, 0, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.04);
}

.reports-problem-map__popup-card {
  display: block;
}

.reports-problem-map__popup-card + .reports-problem-map__popup-card {
  border-top: 1px solid var(--status-new-border);
}

.reports-problem-map__popup-accent-bar {
  height: 0.22rem;
}

.reports-problem-map__popup-media {
  overflow: hidden;
  background: var(--surface-muted);
}

.reports-problem-map__popup-media img {
  display: block;
  width: 100%;
  height: 7.25rem;
  object-fit: cover;
}

.reports-problem-map__popup-body {
  padding: 0.85rem 1rem 1rem;
}

.reports-problem-map__popup-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.55rem;
  margin-bottom: 0.45rem;
}

.reports-problem-map__popup-title-row {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 0;
}

.reports-problem-map__popup-pin {
  flex-shrink: 0;
  display: block;
}

.reports-problem-map__popup-category {
  font-size: 0.92rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.reports-problem-map__popup-status {
  flex-shrink: 0;
  padding: 0.18rem 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--status-new-border);
  background: var(--status-new-surface);
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 750;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.reports-problem-map__popup-status--in_progress {
  border-color: color-mix(in srgb, var(--color-municipal-green) 35%, transparent);
  background: color-mix(in srgb, var(--color-municipal-green) 14%, transparent);
  color: var(--color-municipal-green);
}

.reports-problem-map__popup-status--resolved {
  border-color: color-mix(in srgb, var(--color-municipal-green) 45%, transparent);
  background: color-mix(in srgb, var(--color-municipal-green) 18%, transparent);
  color: var(--color-municipal-green);
}

.reports-problem-map__popup-desc {
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.reports-problem-map__popup-dismiss {
  position: absolute;
  top: 0.55rem;
  right: 0.55rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.7rem;
  height: 1.7rem;
  border: 1px solid color-mix(in srgb, var(--status-new-border) 70%, transparent);
  border-radius: 50%;
  background: color-mix(in srgb, var(--surface-panel-strong) 82%, transparent);
  color: var(--text-primary);
  cursor: pointer;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  transition: background 140ms ease, transform 140ms ease;
}

.reports-problem-map__popup-dismiss:hover {
  background: var(--color-success-surface);
  transform: scale(1.05);
}

.reports-problem-map__attribution {
  margin: 0;
  font-size: 0.62rem;
  font-weight: 650;
  text-align: right;
  opacity: 0.55;
}

:deep(.reports-problem-map__pin) {
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
  line-height: 0;
}

@keyframes reports-map-pulse {
  0%,
  80%,
  100% {
    opacity: 0.35;
    transform: scale(0.85);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 640px) {
  .reports-problem-map__toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-2);
  }

  .reports-problem-map__toolbar-actions {
    width: 100%;
    justify-content: space-between;
  }

  .reports-problem-map__legend {
    gap: 0.35rem 0.55rem;
  }

  .reports-problem-map__legend li {
    font-size: 0.62rem;
  }

  .reports-problem-map__canvas,
  .reports-problem-map__map {
    min-height: 14rem;
  }

  .reports-problem-map__controls {
    top: 6px;
    right: 6px;
  }

  .reports-problem-map__popup-scrim {
    align-items: flex-end;
    padding: 0.5rem;
  }

  .reports-problem-map__popup-overlay {
    width: 100%;
    max-height: min(72vh, 28rem);
    overflow-y: auto;
  }
}
</style>
