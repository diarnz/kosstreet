<template>
  <section class="audit-street-view-scanner">
    <div class="audit-street-view-scanner__head">
      <div>
        <p class="eyebrow">Street audit scanner</p>
        <h3>{{ run.route_name }}</h3>
        <p class="audit-street-view-scanner__subtitle muted">{{ scanProgressLabel }}</p>
        <p v-if="quotaLabel" class="audit-street-view-scanner__quota muted">{{ quotaLabel }}</p>
      </div>
      <AppBadge tone="source-ai-audit">{{ modeLabel }}</AppBadge>
    </div>

    <AppCard v-if="error" class="stack" variant="muted">
      <AppBadge tone="danger">Scanner unavailable</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" size="sm" @click="emit('refresh')">Retry</AppButton>
    </AppCard>

    <AppLoading v-else-if="isLoading" label="Loading scan path" />

    <AppEmptyState
      v-else-if="!scanPath.length && !isPipelineActive"
      tone="audit"
      title="No scan points yet"
      description="Scan points appear here once the pipeline starts analyzing the route."
      action-label="Refresh"
      @action="emit('refresh')"
    />

    <template v-else>
      <div class="audit-street-view-scanner__toolbar">
        <AppButton
          v-if="!isDemoData"
          :disabled="!canAnalyzeCurrentView"
          size="sm"
          type="button"
          variant="secondary"
          @click="analyzeCurrentView"
        >
          {{ isAnalyzingView ? 'Analyzing…' : 'Analyze this view' }}
        </AppButton>

        <AppButton
          v-if="scannerMode === 'explore' && hasEvidenceForSelection"
          size="sm"
          type="button"
          variant="secondary"
          @click="enterEvidenceMode"
        >
          View evidence
        </AppButton>

        <AppButton
          v-if="scannerMode === 'evidence'"
          size="sm"
          type="button"
          variant="primary"
          @click="enterExploreMode"
        >
          Explore again
        </AppButton>
      </div>

      <AuditSeverityLegend />

      <p v-if="analyzeError" class="audit-street-view-scanner__error" role="alert">
        {{ analyzeError }}
      </p>

      <p v-if="evidenceError" class="audit-street-view-scanner__error" role="alert">
        {{ evidenceError }}
      </p>

      <div
        class="audit-street-view-scanner__viewport"
        tabindex="0"
        aria-label="Street audit scanner viewport"
        @keydown="handleViewportKeydown"
      >
        <Transition name="scanner-fade" mode="out-in">
          <div v-if="scannerMode === 'evidence'" key="evidence" class="audit-street-view-scanner__evidence">
            <AppLoading v-if="evidenceLoading" label="Loading evidence frame" />

            <AnalyzedFrameViewer
              v-else-if="evidencePresentation"
              layout="scanner"
              show-metadata
              :category="evidencePresentation.category"
              :confidence="evidencePresentation.confidence"
              :description="evidencePresentation.description"
              :frame-index="evidencePresentation.frameIndex"
              :frames-total="scanPath.length || run.frames_total || undefined"
              :heading="evidencePresentation.heading"
              :image-url="evidencePresentation.imageUrl"
              :is-civic-issue="evidencePresentation.isCivicIssue"
              :latitude="evidencePresentation.latitude"
              :longitude="evidencePresentation.longitude"
              :pitch="evidencePresentation.pitch"
              :regions="evidencePresentation.regions"
              :severity="evidencePresentation.severity"
            />

            <AppEmptyState
              v-else
              tone="audit"
              title="Evidence unavailable"
              description="Could not load the analyzed frame for this scan point."
            />
          </div>

          <div v-else key="explore" class="audit-street-view-scanner__explore">
            <StreetViewPanel
              v-if="streetViewTarget || isPipelineActive"
              ref="streetViewPanelRef"
              compact
              eyebrow="Explore"
              :record-count="scanPath.length"
              :target="streetViewTarget"
              :title="streetViewTarget?.label ?? run.route_name"
              track-view-changes
              @view-changed="handleViewChanged"
            />
            <AppEmptyState
              v-else
              tone="audit"
              title="Select a scan point"
              description="Choose a point on the timeline or a suggestion to load Street View."
            />
          </div>
        </Transition>

        <AuditAnalyzingOverlay
          :progress="pipelineProgress"
          :progress-label="pipelineProgressLabel"
          :subtitle="overlaySubtitle"
          :title="overlayTitle"
          :visible="showAnalyzingOverlay"
          :show-cancel="isAnalyzingView"
          @cancel="cancelAnalyze"
        />
      </div>

      <AuditScanTimeline
        v-if="enrichedScanPath.length"
        :scan-path="enrichedScanPath"
        :selected-frame-index="selectedFrameIndex"
        @select="handleTimelineSelect"
        @hover="handleTimelineHover"
      />
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import AuditAnalyzingOverlay from '@/components/audit/AuditAnalyzingOverlay.vue';
import AuditScanTimeline from '@/components/audit/AuditScanTimeline.vue';
import AuditSeverityLegend from '@/components/audit/AuditSeverityLegend.vue';
import StreetViewPanel from '@/components/streetview/StreetViewPanel.vue';
import {
  analyzeAuditView,
  auditFrameImagePath,
  getAuditFrame,
  getOnDemandAnalyzeQuota,
} from '@/api/auditFrames';
import { getDemoFrameDetail } from '@/demo/demoAuditScanPath';
import type {
  AuditFrameDetail,
  AuditRunSummary,
  AuditScanPoint,
  OnDemandAnalyzeQuota,
} from '@/types/audit';
import type { AuditSuggestion, AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { IssueCategory } from '@/types/report';
import type { StreetViewCurrentView, StreetViewTarget } from '@/types/streetView';
import { ApiError } from '@/types/api';
import { prefetchImageUrl } from '@/utils/auditFramePrefetch';
import { enrichScanPathWithSuggestionStatus } from '@/utils/auditScanPath';
import {
  auditRunToStreetViewTarget,
  scanPointToStreetViewTarget,
  suggestionToStreetViewTarget,
} from '@/utils/streetView';

type ScannerMode = 'explore' | 'evidence';

interface EvidencePresentation {
  frameIndex: number;
  imageUrl: string;
  regions: DetectionRegion[];
  severity?: AuditSuggestionSeverity | null;
  category?: IssueCategory | null;
  description?: string | null;
  confidence?: number | null;
  heading?: number | null;
  pitch?: number | null;
  latitude?: number;
  longitude?: number;
  isCivicIssue: boolean;
}

const props = withDefaults(
  defineProps<{
    run: AuditRunSummary;
    scanPath: AuditScanPoint[];
    suggestions?: AuditSuggestion[];
    selectedFrameIndex: number | null;
    selectedSuggestion?: AuditSuggestion | null;
    isLoading?: boolean;
    error?: string | null;
    isDemoData?: boolean;
  }>(),
  {
    suggestions: () => [],
    isDemoData: false,
  },
);

const emit = defineEmits<{
  refresh: [];
  'scan-point-selected': [frameIndex: number];
  analyzed: [frame: AuditFrameDetail];
}>();

const streetViewPanelRef = ref<{ getCurrentView: () => StreetViewCurrentView | null } | null>(null);
const liveView = ref<StreetViewCurrentView | null>(null);
const isAnalyzingView = ref(false);
const analyzeError = ref<string | null>(null);
const analyzeCancelled = ref(false);
const scannerMode = ref<ScannerMode>('explore');
const exploreLocked = ref(false);
const evidenceFrame = ref<AuditFrameDetail | null>(null);
const evidenceLoading = ref(false);
const evidenceError = ref<string | null>(null);
const analyzeQuota = ref<OnDemandAnalyzeQuota | null>(null);

const enrichedScanPath = computed(() =>
  enrichScanPathWithSuggestionStatus(props.scanPath, props.suggestions),
);

const quotaLabel = computed(() => {
  if (props.isDemoData || isPipelineActive.value || !analyzeQuota.value) {
    return null;
  }

  const { remaining, limit } = analyzeQuota.value;
  return `${remaining} of ${limit} on-demand analyzes remaining this hour`;
});

const isPipelineActive = computed(
  () => props.run.status === 'running' || props.run.status === 'queued',
);

const selectedScanPoint = computed(() =>
  props.selectedFrameIndex == null
    ? null
    : props.scanPath.find((point) => point.frame_index === props.selectedFrameIndex) ?? null,
);

const activeTarget = computed<StreetViewTarget | null>(() => {
  if (props.selectedSuggestion) {
    return suggestionToStreetViewTarget(props.selectedSuggestion);
  }
  if (props.selectedFrameIndex == null || !selectedScanPoint.value) {
    return null;
  }
  return scanPointToStreetViewTarget(props.run, selectedScanPoint.value);
});

const streetViewTarget = computed<StreetViewTarget | null>(() => {
  if (activeTarget.value) {
    return activeTarget.value;
  }
  if (props.run.scan_latitude != null && props.run.scan_longitude != null) {
    return auditRunToStreetViewTarget(
      props.run,
      props.run.scan_latitude,
      props.run.scan_longitude,
    );
  }
  const firstPoint = props.scanPath[0];
  return firstPoint ? scanPointToStreetViewTarget(props.run, firstPoint) : null;
});

const hasEvidenceForSelection = computed(
  () =>
    Boolean(props.selectedSuggestion) ||
    Boolean(selectedScanPoint.value?.is_civic_issue) ||
    Boolean(evidenceFrame.value?.is_civic_issue),
);

const shouldAutoEnterEvidence = computed(
  () => hasEvidenceForSelection.value && !exploreLocked.value,
);

const modeLabel = computed(() => {
  if (isPipelineActive.value) return 'Scanning';
  if (scannerMode.value === 'evidence') return 'Evidence';
  if (props.selectedSuggestion) return 'Detection focus';
  return 'Explore';
});

const scanProgressLabel = computed(() => {
  const total = props.run.frames_total || props.scanPath.length;
  const done = props.run.frames_done;
  const points = props.scanPath.length;

  if (isPipelineActive.value && total > 0) {
    return `Scan point ${Math.min(done, total)} of ${total}`;
  }
  if (points > 0) {
    return `${points} scan point${points === 1 ? '' : 's'} along route`;
  }
  return 'Waiting for scan path';
});

const pipelineProgress = computed<number | null>(() => {
  if (!isPipelineActive.value || props.run.frames_total <= 0) return null;
  return Math.min(100, Math.round((props.run.frames_done / props.run.frames_total) * 100));
});

const pipelineProgressLabel = computed(() => {
  if (!isPipelineActive.value || props.run.frames_total <= 0) return null;
  return `Scan point ${Math.min(props.run.frames_done, props.run.frames_total)} of ${props.run.frames_total}`;
});

const showAnalyzingOverlay = computed(() => isPipelineActive.value || isAnalyzingView.value);

const overlayTitle = computed(() =>
  isAnalyzingView.value ? 'Analyzing this view…' : 'Analyzing street view…',
);

const overlaySubtitle = computed(() => {
  if (isAnalyzingView.value) return props.run.route_name;
  return `${props.run.route_name} · ${pipelineProgressLabel.value ?? 'Starting scan'}`;
});

const canAnalyzeCurrentView = computed(
  () =>
    !props.isDemoData &&
    !isPipelineActive.value &&
    !isAnalyzingView.value &&
    (analyzeQuota.value?.remaining ?? 1) > 0 &&
    Boolean(resolveAnalyzeView()),
);

const evidencePresentation = computed<EvidencePresentation | null>(() => {
  if (props.selectedSuggestion) {
    return presentationFromSuggestion(props.selectedSuggestion);
  }
  if (evidenceFrame.value) {
    return presentationFromFrame(evidenceFrame.value);
  }
  if (selectedScanPoint.value?.is_civic_issue && props.selectedFrameIndex != null) {
    if (props.isDemoData) {
      const demoFrame = getDemoFrameDetail(props.run.id, props.selectedFrameIndex);
      if (demoFrame) {
        return presentationFromFrame(demoFrame);
      }
    }

    return {
      frameIndex: props.selectedFrameIndex,
      imageUrl: auditFrameImagePath(props.run.id, props.selectedFrameIndex),
      regions: [],
      severity: selectedScanPoint.value.severity,
      isCivicIssue: true,
    };
  }
  return null;
});

watch(
  () => props.run.id,
  () => {
    analyzeError.value = null;
    evidenceError.value = null;
    isAnalyzingView.value = false;
    analyzeCancelled.value = false;
    liveView.value = null;
    evidenceFrame.value = null;
    scannerMode.value = 'explore';
    exploreLocked.value = false;
    analyzeQuota.value = null;
    void loadAnalyzeQuota();
  },
  { immediate: true },
);

watch(
  () => [props.selectedFrameIndex, props.selectedSuggestion?.id] as const,
  () => {
    exploreLocked.value = false;
    evidenceFrame.value = null;
    if (shouldAutoEnterEvidence.value) {
      scannerMode.value = 'evidence';
      void loadEvidenceFrame();
    } else {
      scannerMode.value = 'explore';
    }
  },
);

function presentationFromSuggestion(suggestion: AuditSuggestion): EvidencePresentation {
  const frameIndex = suggestion.frame_index ?? 0;
  const demoFrame =
    props.isDemoData && suggestion.frame_index != null
      ? getDemoFrameDetail(props.run.id, suggestion.frame_index)
      : null;

  return {
    frameIndex,
    imageUrl:
      suggestion.frame_image_url ??
      suggestion.image_url ??
      demoFrame?.frame_image_url ??
      auditFrameImagePath(props.run.id, frameIndex),
    regions: suggestion.detection_regions ?? demoFrame?.detection_regions ?? [],
    severity: suggestion.severity,
    category: suggestion.category,
    description: suggestion.description,
    confidence: suggestion.confidence,
    heading: suggestion.heading,
    pitch: suggestion.pitch,
    latitude: suggestion.latitude,
    longitude: suggestion.longitude,
    isCivicIssue: true,
  };
}

function presentationFromFrame(frame: AuditFrameDetail): EvidencePresentation {
  return {
    frameIndex: frame.frame_index,
    imageUrl: frame.frame_image_url,
    regions: frame.detection_regions ?? [],
    severity: frame.severity,
    category: frame.category,
    description: frame.description,
    confidence: frame.confidence,
    heading: frame.heading,
    pitch: frame.pitch,
    latitude: frame.latitude,
    longitude: frame.longitude,
    isCivicIssue: frame.is_civic_issue,
  };
}

async function loadEvidenceFrame() {
  if (props.selectedSuggestion) {
    evidenceError.value = null;
    return;
  }
  if (props.selectedFrameIndex == null) {
    evidenceFrame.value = null;
    return;
  }

  evidenceLoading.value = true;
  evidenceError.value = null;

  try {
    if (props.isDemoData) {
      evidenceFrame.value = getDemoFrameDetail(props.run.id, props.selectedFrameIndex);
      if (!evidenceFrame.value) {
        evidenceError.value = 'Could not load demo evidence frame.';
      }
      return;
    }

    evidenceFrame.value = await getAuditFrame(props.run.id, props.selectedFrameIndex);
  } catch (loadError) {
    evidenceFrame.value = null;
    evidenceError.value =
      loadError instanceof Error ? loadError.message : 'Could not load evidence frame.';
  } finally {
    evidenceLoading.value = false;
  }
}

function enterEvidenceMode() {
  exploreLocked.value = false;
  scannerMode.value = 'evidence';
  void loadEvidenceFrame();
}

function enterExploreMode() {
  exploreLocked.value = true;
  scannerMode.value = 'explore';
}

function handleTimelineHover(frameIndex: number) {
  const currentIndex = props.scanPath.findIndex((point) => point.frame_index === frameIndex);
  if (currentIndex < 0) {
    return;
  }

  for (const offset of [-1, 1]) {
    const neighbor = props.scanPath[currentIndex + offset];
    if (!neighbor) {
      continue;
    }

    prefetchImageUrl(resolveFrameImageUrl(neighbor.frame_index, neighbor.suggestion_id));
  }
}

function resolveFrameImageUrl(frameIndex: number, suggestionId?: string | null): string {
  if (props.isDemoData) {
    return getDemoFrameDetail(props.run.id, frameIndex)?.frame_image_url ?? '/demo/audit/clean_01.jpg';
  }

  if (suggestionId) {
    return `/api/v1/audit-suggestions/${encodeURIComponent(suggestionId)}/frame-image`;
  }

  return auditFrameImagePath(props.run.id, frameIndex);
}

function handleTimelineSelect(frameIndex: number) {
  emit('scan-point-selected', frameIndex);
}

async function loadAnalyzeQuota() {
  if (props.isDemoData || isPipelineActive.value) {
    analyzeQuota.value = null;
    return;
  }

  try {
    analyzeQuota.value = await getOnDemandAnalyzeQuota(props.run.id);
  } catch {
    analyzeQuota.value = null;
  }
}

function handleViewportKeydown(event: KeyboardEvent) {
  if (!props.scanPath.length || props.selectedFrameIndex == null) {
    return;
  }

  const currentIndex = props.scanPath.findIndex(
    (point) => point.frame_index === props.selectedFrameIndex,
  );
  if (currentIndex < 0) {
    return;
  }

  if (event.key === 'ArrowRight') {
    event.preventDefault();
    const next = props.scanPath[currentIndex + 1];
    if (next) emit('scan-point-selected', next.frame_index);
    return;
  }

  if (event.key === 'ArrowLeft') {
    event.preventDefault();
    const previous = props.scanPath[currentIndex - 1];
    if (previous) emit('scan-point-selected', previous.frame_index);
    return;
  }

  if (event.key === 'Enter' && hasEvidenceForSelection.value) {
    event.preventDefault();
    if (scannerMode.value === 'evidence') {
      enterExploreMode();
    } else {
      enterEvidenceMode();
    }
  }
}

function handleViewChanged(view: StreetViewCurrentView) {
  liveView.value = view;
  analyzeError.value = null;
}

function resolveAnalyzeView(): StreetViewCurrentView | null {
  return (
    streetViewPanelRef.value?.getCurrentView() ??
    liveView.value ??
    viewFromTarget(streetViewTarget.value)
  );
}

function viewFromTarget(target: StreetViewTarget | null): StreetViewCurrentView | null {
  if (!target) return null;
  return {
    latitude: target.latitude,
    longitude: target.longitude,
    heading: Math.round(target.heading ?? 0),
    pitch: Math.round(target.pitch ?? 0),
  };
}

function cancelAnalyze() {
  analyzeCancelled.value = true;
  isAnalyzingView.value = false;
}

async function analyzeCurrentView() {
  const view = resolveAnalyzeView();
  if (!view || isPipelineActive.value) return;

  isAnalyzingView.value = true;
  analyzeCancelled.value = false;
  analyzeError.value = null;

  try {
    const frame = await analyzeAuditView(props.run.id, view);
    if (analyzeCancelled.value) return;

    evidenceFrame.value = frame;
    emit('analyzed', frame);
    emit('scan-point-selected', frame.frame_index);

    if (frame.is_civic_issue) {
      exploreLocked.value = false;
      scannerMode.value = 'evidence';
    }

    void loadAnalyzeQuota();
  } catch (error) {
    if (analyzeCancelled.value) return;
    if (error instanceof ApiError && error.status === 429) {
      analyzeError.value =
        'On-demand analyze limit reached for this run. Try again after the hourly window resets.';
    } else {
      analyzeError.value =
        error instanceof Error ? error.message : 'Could not analyze this Street View.';
    }
    void loadAnalyzeQuota();
  } finally {
    if (!analyzeCancelled.value) {
      isAnalyzingView.value = false;
    }
  }
}
</script>

<style scoped>
.audit-street-view-scanner {
  display: grid;
  gap: var(--space-3);
}

.audit-street-view-scanner__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
}

.audit-street-view-scanner__head h3 {
  margin: 0.15rem 0 0;
  font-size: clamp(1.1rem, 2vw, 1.35rem);
  letter-spacing: -0.02em;
}

.audit-street-view-scanner__subtitle {
  margin: 0.2rem 0 0;
  font-size: var(--text-sm);
}

.audit-street-view-scanner__quota {
  margin: 0.15rem 0 0;
  font-size: var(--text-xs);
}

.audit-street-view-scanner__toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.audit-street-view-scanner__error {
  margin: 0;
  padding: var(--space-3) var(--space-4);
  border: 1px solid rgba(185, 28, 28, 0.18);
  border-radius: var(--radius-md);
  color: var(--color-repair-red);
  background: rgba(254, 242, 242, 0.82);
  font-size: var(--text-sm);
  font-weight: 750;
}

.audit-street-view-scanner__viewport {
  position: relative;
  min-height: 22rem;
  outline: none;
}

.audit-street-view-scanner__viewport:focus-visible {
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.35);
  border-radius: var(--radius-lg);
}

.audit-street-view-scanner__explore :deep(.street-view-panel__canvas) {
  min-height: clamp(22rem, 60vh, 36rem);
}

.audit-street-view-scanner__evidence {
  min-height: clamp(22rem, 60vh, 36rem);
}

.scanner-fade-enter-active,
.scanner-fade-leave-active {
  transition: opacity var(--motion-base) ease;
}

.scanner-fade-enter-from,
.scanner-fade-leave-to {
  opacity: 0;
}

@media (max-width: 720px) {
  .audit-street-view-scanner__explore :deep(.street-view-panel__canvas),
  .audit-street-view-scanner__evidence {
    min-height: 20rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .scanner-fade-enter-active,
  .scanner-fade-leave-active {
    transition: none;
  }
}
</style>
