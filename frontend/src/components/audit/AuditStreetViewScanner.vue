<template>
  <section class="audit-street-view-scanner">
    <div class="audit-street-view-scanner__head">
      <span class="audit-street-view-scanner__stat">{{ scanProgressLabel }}</span>
      <AppBadge tone="source-ai-audit" size="xs">{{ modeLabel }}</AppBadge>
    </div>

    <AppCard v-if="error" class="stack" variant="muted">
      <AppBadge tone="danger">Scanner unavailable</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" size="sm" @click="emit('refresh')">Retry</AppButton>
    </AppCard>

    <AppLoading
      v-else-if="isLoading && (scanPath.length > 0 || isPipelineActive)"
      label="Loading scan path"
    />

    <template v-else-if="scanPath.length > 0 || isPipelineActive">
      <p v-if="evidenceError" class="audit-street-view-scanner__error" role="alert">
        {{ evidenceError }}
      </p>

      <div
        ref="viewportRef"
        class="audit-street-view-scanner__viewport"
        :class="{
          'audit-street-view-scanner__viewport--fs': isFullscreen,
          'audit-street-view-scanner__viewport--fs-enter': fsAnimPhase === 'enter',
          'audit-street-view-scanner__viewport--fs-exit': fsAnimPhase === 'exit',
        }"
        tabindex="0"
        aria-label="Street audit scanner viewport"
        @keydown="handleViewportKeydown"
      >
        <div ref="fsStageRef" class="scanner-fs-stage">
        <Transition name="scanner-fade" mode="out-in">
          <div v-if="scannerMode === 'evidence'" key="evidence" class="audit-street-view-scanner__evidence">
            <div class="audit-street-view-scanner__evidence-stage">
              <AnalyzedFrameViewer
                v-if="evidencePresentation && !evidenceLoading"
                layout="scanner"
                :zoomable="false"
                alt=""
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
                @image-loaded="evidenceImageLoading = false"
                @image-loading="evidenceImageLoading = true"
              />

              <Transition name="scanner-fade">
                <div
                  v-if="showEvidenceBusy"
                  class="audit-street-view-scanner__evidence-busy"
                  role="status"
                  aria-live="polite"
                >
                  <div class="audit-street-view-scanner__evidence-busy-panel">
                    <span class="audit-street-view-scanner__evidence-busy-spinner" aria-hidden="true" />
                    <p class="audit-street-view-scanner__evidence-busy-title">Loading frame</p>
                    <p class="audit-street-view-scanner__evidence-busy-sub">
                      {{ evidenceBusyLabel }}
                    </p>
                  </div>
                </div>
              </Transition>
            </div>

            <AppEmptyState
              v-if="!showEvidenceBusy && !evidencePresentation"
              tone="audit"
              title="Evidence unavailable"
              :description="evidenceError ?? 'Could not load the analyzed frame for this scan point.'"
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
        </div>

        <div v-if="showScannerHud" class="scanner-hud" aria-label="Scanner controls">
          <button
            v-if="scannerMode === 'evidence'"
            class="scanner-hud__btn"
            type="button"
            title="Street view"
            aria-label="Open street view"
            @click="enterExploreMode"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M3 11l19-9-9 19-2-8-8-2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
            </svg>
          </button>
          <button
            v-else-if="hasEvidenceForSelection"
            class="scanner-hud__btn"
            type="button"
            title="Evidence photo"
            aria-label="View evidence photo"
            @click="enterEvidenceMode"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <rect x="4" y="5" width="16" height="14" rx="2" stroke="currentColor" stroke-width="1.8" />
              <circle cx="9" cy="10" r="1.5" fill="currentColor" />
              <path d="M4 16l4.5-4.5 3 3L14 12l6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
          <span v-else class="scanner-hud__spacer" />

          <button
            class="scanner-hud__btn"
            type="button"
            :title="isFullscreen ? 'Exit fullscreen' : 'Fullscreen'"
            :aria-label="isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'"
            @click="toggleFullscreen"
          >
            <svg v-if="!isFullscreen" width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M9 3H5a2 2 0 00-2 2v4M15 3h4a2 2 0 012 2v4M9 21H5a2 2 0 01-2-2v-4M15 21h4a2 2 0 002-2v-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M9 9H5V5M15 9h4V5M9 15H5v4M15 15h4v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>
        </div>

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

    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import AuditAnalyzingOverlay from '@/components/audit/AuditAnalyzingOverlay.vue';
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
const viewportRef = ref<HTMLElement | null>(null);
const fsStageRef = ref<HTMLElement | null>(null);
const isFullscreen = ref(false);
const fsAnimPhase = ref<'enter' | 'exit' | null>(null);

type FsOriginRect = {
  left: number;
  top: number;
  width: number;
  height: number;
};

const fsOriginRect = ref<FsOriginRect | null>(null);

const FS_ENTER_MS = 520;
const FS_EXIT_MS = 380;

const showScannerHud = computed(
  () => !props.isLoading && !props.error && (props.scanPath.length > 0 || isPipelineActive.value),
);

function prefersReducedMotion(): boolean {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function applyFsFlipVars(viewport: HTMLElement, rect: FsOriginRect) {
  const originCx = rect.left + rect.width / 2;
  const originCy = rect.top + rect.height / 2;
  const viewportCx = window.innerWidth / 2;
  const viewportCy = window.innerHeight / 2;
  const scaleX = rect.width / window.innerWidth;
  const scaleY = rect.height / window.innerHeight;
  const scale = Math.max(Math.min(scaleX, scaleY), 0.06);

  viewport.style.setProperty('--fs-x', `${originCx - viewportCx}px`);
  viewport.style.setProperty('--fs-y', `${originCy - viewportCy}px`);
  viewport.style.setProperty('--fs-scale', String(scale));
}

function captureFsOrigin(viewport: HTMLElement): FsOriginRect {
  const rect = viewport.getBoundingClientRect();
  return {
    left: rect.left,
    top: rect.top,
    width: rect.width,
    height: rect.height,
  };
}

function clearFsFlipVars(viewport: HTMLElement) {
  viewport.style.removeProperty('--fs-x');
  viewport.style.removeProperty('--fs-y');
  viewport.style.removeProperty('--fs-scale');
}

function waitForAnimation(stage: HTMLElement, animationName: string, timeoutMs: number): Promise<void> {
  return new Promise((resolve) => {
    const finish = () => {
      stage.removeEventListener('animationend', onEnd);
      window.clearTimeout(fallback);
      resolve();
    };
    const onEnd = (event: AnimationEvent) => {
      if (event.animationName === animationName) {
        finish();
      }
    };
    stage.addEventListener('animationend', onEnd);
    const fallback = window.setTimeout(finish, timeoutMs + 50);
  });
}

function nextFrame(): Promise<void> {
  return new Promise((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
  });
}

async function toggleFullscreen() {
  const viewport = viewportRef.value;
  if (!viewport) return;

  const reducedMotion = prefersReducedMotion();

  if (document.fullscreenElement === viewport) {
    if (reducedMotion || !fsOriginRect.value) {
      fsAnimPhase.value = null;
      await document.exitFullscreen();
      return;
    }

    applyFsFlipVars(viewport, fsOriginRect.value);
    fsAnimPhase.value = 'exit';
    const stage = fsStageRef.value;
    if (stage) {
      await waitForAnimation(stage, 'scanner-fs-exit', FS_EXIT_MS);
    }
    fsAnimPhase.value = null;
    await document.exitFullscreen();
    clearFsFlipVars(viewport);
    fsOriginRect.value = null;
    return;
  }

  const origin = captureFsOrigin(viewport);
  fsOriginRect.value = origin;
  applyFsFlipVars(viewport, origin);

  try {
    await viewport.requestFullscreen();
  } catch {
    fsAnimPhase.value = null;
    fsOriginRect.value = null;
    clearFsFlipVars(viewport);
    return;
  }

  if (reducedMotion) {
    return;
  }

  await nextFrame();
  fsAnimPhase.value = 'enter';
  const stage = fsStageRef.value;
  if (stage) {
    await waitForAnimation(stage, 'scanner-fs-enter', FS_ENTER_MS);
  }
  fsAnimPhase.value = null;
}

function syncFullscreenState() {
  const active = document.fullscreenElement === viewportRef.value;
  isFullscreen.value = active;
  if (!active) {
    fsAnimPhase.value = null;
    fsOriginRect.value = null;
    const viewport = viewportRef.value;
    if (viewport) {
      clearFsFlipVars(viewport);
    }
  }
}

document.addEventListener('fullscreenchange', syncFullscreenState);

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', syncFullscreenState);
});

const exploreLocked = ref(false);
const evidenceFrame = ref<AuditFrameDetail | null>(null);
const evidenceLoading = ref(false);
const evidenceImageLoading = ref(false);
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

const showEvidenceBusy = computed(
  () => evidenceLoading.value || evidenceImageLoading.value,
);

const evidenceBusyLabel = computed(() => {
  if (evidenceLoading.value) {
    return 'Fetching analyzed frame data…';
  }

  const total = props.scanPath.length || props.run.frames_total;
  if (props.selectedFrameIndex != null && total > 0) {
    const index = props.scanPath.findIndex((point) => point.frame_index === props.selectedFrameIndex);
    const position = index >= 0 ? index + 1 : props.selectedFrameIndex + 1;
    return `Preparing scan point ${position} of ${total}`;
  }

  return 'Preparing evidence photo…';
});

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
    evidenceImageLoading.value = true;
    exploreLocked.value = false;
    evidenceFrame.value = null;
    if (shouldAutoEnterEvidence.value) {
      scannerMode.value = 'evidence';
      void loadEvidenceFrame();
    } else {
      scannerMode.value = 'explore';
      evidenceImageLoading.value = false;
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
  evidenceError.value = null;

  if (props.selectedSuggestion) {
    evidenceLoading.value = false;
    evidenceImageLoading.value = true;
    return;
  }

  if (props.selectedFrameIndex == null) {
    evidenceFrame.value = null;
    evidenceLoading.value = false;
    evidenceImageLoading.value = false;
    return;
  }

  evidenceLoading.value = true;
  evidenceImageLoading.value = true;

  try {
    if (props.isDemoData) {
      evidenceFrame.value = getDemoFrameDetail(props.run.id, props.selectedFrameIndex);
      if (!evidenceFrame.value) {
        evidenceError.value = 'Could not load demo evidence frame.';
        evidenceImageLoading.value = false;
      }
      return;
    }

    evidenceFrame.value = await getAuditFrame(props.run.id, props.selectedFrameIndex);
  } catch (loadError) {
    evidenceFrame.value = null;
    evidenceImageLoading.value = false;
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

function resolveFrameImageUrl(frameIndex: number, suggestionId?: string | null): string {
  if (props.isDemoData) {
    return getDemoFrameDetail(props.run.id, frameIndex)?.frame_image_url ?? '/demo/audit/clean_01.jpg';
  }

  if (suggestionId) {
    return `/api/v1/audit-suggestions/${encodeURIComponent(suggestionId)}/frame-image`;
  }

  return auditFrameImagePath(props.run.id, frameIndex);
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
  gap: 0.5rem;
}

.audit-street-view-scanner__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.audit-street-view-scanner__info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.audit-street-view-scanner__stat {
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.audit-street-view-scanner__stat--quota {
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.audit-street-view-scanner__sep {
  color: var(--text-muted);
  font-size: var(--text-xs);
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
  --fs-x: 0px;
  --fs-y: 0px;
  --fs-scale: 1;
  position: relative;
  min-height: 22rem;
  outline: none;
}

.scanner-fs-stage {
  position: relative;
  width: 100%;
}

.audit-street-view-scanner__viewport:fullscreen .scanner-fs-stage,
.audit-street-view-scanner__viewport--fs .scanner-fs-stage {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.audit-street-view-scanner__viewport--fs-enter .scanner-fs-stage {
  animation: scanner-fs-enter 520ms var(--ease-spring, cubic-bezier(0.22, 1.12, 0.32, 1)) both;
}

.audit-street-view-scanner__viewport--fs-exit .scanner-fs-stage {
  animation: scanner-fs-exit 380ms var(--ease-out-expo, ease) both;
}

@keyframes scanner-fs-enter {
  from {
    opacity: 0.72;
    transform: translate(var(--fs-x), var(--fs-y)) scale(var(--fs-scale));
  }

  to {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
}

@keyframes scanner-fs-exit {
  from {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }

  to {
    opacity: 0.55;
    transform: translate(var(--fs-x), var(--fs-y)) scale(var(--fs-scale));
  }
}

.audit-street-view-scanner__viewport--fs-enter .scanner-hud {
  animation: scanner-hud-enter 360ms 120ms ease both;
}

@keyframes scanner-hud-enter {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.audit-street-view-scanner__viewport:fullscreen,
.audit-street-view-scanner__viewport--fs {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 100%;
  background: #050708;
  overflow: hidden;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__evidence,
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__evidence {
  flex: 1;
  width: 100%;
  min-height: 0;
  justify-content: stretch;
  align-items: stretch;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__evidence::before,
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__evidence::before {
  display: none;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer),
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer) {
  width: 100%;
  height: 100%;
  max-width: none;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer__layout),
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer__layout) {
  height: 100%;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer__media),
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer__media) {
  width: 100%;
  height: 100%;
  max-width: none !important;
  max-height: none !important;
  aspect-ratio: unset !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__evidence :deep(img),
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__evidence :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #050708;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__explore,
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__explore {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__explore :deep(.street-view-panel),
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__explore :deep(.street-view-panel) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.audit-street-view-scanner__viewport:fullscreen .audit-street-view-scanner__explore :deep(.street-view-panel__canvas),
.audit-street-view-scanner__viewport--fs .audit-street-view-scanner__explore :deep(.street-view-panel__canvas) {
  flex: 1;
  height: 100% !important;
  min-height: 0 !important;
}

.audit-street-view-scanner__viewport:-moz-full-screen {
  width: 100vw;
  height: 100vh;
  background: #050708;
}

.audit-street-view-scanner__viewport:-webkit-full-screen {
  width: 100vw;
  height: 100vh;
  background: #050708;
}

.audit-street-view-scanner__viewport:focus-visible {
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.35);
  border-radius: var(--radius-lg);
}

/* ─── Explore mode ─── */
.audit-street-view-scanner__explore {
  position: relative;
}

.audit-street-view-scanner__explore :deep(.street-view-panel__canvas) {
  min-height: clamp(18rem, 42vh, 28rem);
}

/* ─── Evidence mode ─── */
.audit-street-view-scanner__evidence {
  position: relative;
  display: flex;
  justify-content: center;
}

.audit-street-view-scanner__evidence-stage {
  position: relative;
  width: min(100%, 42rem);
  min-height: clamp(18rem, 42vh, 28rem);
}

.audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer) {
  width: 100%;
}

.audit-street-view-scanner__evidence-busy {
  position: absolute;
  inset: 0;
  z-index: 12;
  display: grid;
  place-items: center;
  border-radius: var(--radius-lg);
  background: rgba(8, 12, 10, 0.58);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.audit-street-view-scanner__evidence-busy-panel {
  display: grid;
  gap: 0.35rem;
  justify-items: center;
  padding: 1rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: calc(var(--radius-md) + 2px);
  background: rgba(12, 16, 14, 0.82);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  text-align: center;
}

.audit-street-view-scanner__evidence-busy-spinner {
  width: 1.35rem;
  height: 1.35rem;
  border: 2px solid rgba(47, 93, 80, 0.25);
  border-top-color: var(--color-municipal-green);
  border-radius: 50%;
  animation: audit-evidence-spin 800ms linear infinite;
}

.audit-street-view-scanner__evidence-busy-title {
  margin: 0.15rem 0 0;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 850;
  letter-spacing: -0.01em;
}

.audit-street-view-scanner__evidence-busy-sub {
  margin: 0;
  max-width: 14rem;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.68rem;
  line-height: 1.45;
}

@keyframes audit-evidence-spin {
  to {
    transform: rotate(360deg);
  }
}

.audit-street-view-scanner__evidence :deep(.analyzed-frame-viewer__media) {
  border-radius: var(--radius-lg);
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.12),
    0 8px 32px rgba(0, 0, 0, 0.22),
    0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Gradient vignette at top of evidence image for HUD readability */
.audit-street-view-scanner__evidence-stage::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4rem;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.45) 0%, transparent 100%);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  z-index: 15;
  pointer-events: none;
}

/* ─── Unified icon HUD ─── */
.scanner-hud {
  position: absolute;
  inset: 0.65rem 0.65rem auto;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  pointer-events: none;
}

.scanner-hud__spacer {
  flex: 1;
}

.scanner-hud__btn {
  display: grid;
  place-items: center;
  width: 2.35rem;
  height: 2.35rem;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: var(--radius-md);
  background: rgba(8, 12, 16, 0.72);
  backdrop-filter: blur(12px) saturate(1.3);
  color: rgba(255, 255, 255, 0.95);
  cursor: pointer;
  pointer-events: all;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
  transition:
    background var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    transform var(--motion-fast) ease;
}

.scanner-hud__btn:hover {
  background: rgba(12, 18, 24, 0.9);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.audit-street-view-scanner__viewport:fullscreen .scanner-hud,
.audit-street-view-scanner__viewport--fs .scanner-hud {
  inset: 1rem 1rem auto;
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
  .audit-street-view-scanner__explore :deep(.street-view-panel__canvas) {
    min-height: 20rem;
  }
}

@media (max-width: 640px) {
  .audit-street-view-scanner__head {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-2);
  }

  .audit-street-view-scanner__info {
    justify-content: space-between;
  }

  .audit-street-view-scanner__viewport {
    min-height: 16rem;
  }

  .audit-street-view-scanner__explore :deep(.street-view-panel__canvas) {
    min-height: 16rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .scanner-fade-enter-active,
  .scanner-fade-leave-active {
    transition: none;
  }

  .audit-street-view-scanner__viewport--fs-enter .scanner-fs-stage,
  .audit-street-view-scanner__viewport--fs-exit .scanner-fs-stage,
  .audit-street-view-scanner__viewport--fs-enter .scanner-hud {
    animation: none;
  }
}
</style>
