<template>
  <AppCard class="audit-frame-browser stack" variant="inset">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Frame browser</p>
        <h3>What the AI analyzed</h3>
        <p class="audit-frame-browser__intro">
          Browse every Street View frame from this run. Select a frame to inspect the analyzed image
          and severity overlay.
        </p>
      </div>
      <AppButton
        :disabled="isLoading"
        size="sm"
        variant="secondary"
        @click="refreshFrames"
      >
        {{ isLoading ? 'Refreshing...' : 'Refresh frames' }}
      </AppButton>
    </div>

    <div class="audit-frame-browser__filters">
      <label class="audit-frame-browser__filter">
        <span>View</span>
        <select v-model="filterMode">
          <option value="all">All frames</option>
          <option value="detections">Detections only</option>
        </select>
      </label>

      <label class="audit-frame-browser__filter">
        <span>Severity</span>
        <select v-model="severityFilter">
          <option value="all">All severities</option>
          <option v-for="severity in severityOptions" :key="severity" :value="severity">
            {{ formatSeverityLabel(severity) }}
          </option>
        </select>
      </label>

      <label class="audit-frame-browser__filter">
        <span>Category</span>
        <select v-model="categoryFilter">
          <option value="all">All categories</option>
          <option v-for="category in categoryOptions" :key="category" :value="category">
            {{ categoryLabels[category] }}
          </option>
        </select>
      </label>
    </div>

    <AppCard v-if="error" class="stack" variant="muted">
      <AppBadge tone="danger">Backend error</AppBadge>
      <p>{{ error }}</p>
    </AppCard>

    <p v-else-if="isLoading && frames.length === 0" class="muted">Loading analyzed frames...</p>

    <AppEmptyState
      v-else-if="filteredFrames.length === 0"
      description="No frames match the current filters for this audit run."
      title="No frames to show"
      tone="audit"
    />

    <SeverityLegend v-if="frames.some((frame) => frame.has_detection_regions)" />

    <div
      v-if="filteredFrames.length > 0"
      aria-label="Analyzed frame thumbnails. Use arrow keys to move and Enter to inspect."
      class="audit-frame-browser__grid"
      role="list"
      tabindex="0"
      @keydown="handleGridKeydown"
    >
      <button
        v-for="(frame, index) in filteredFrames"
        :key="frame.id"
        :ref="(element) => setTileRef(index, element as HTMLButtonElement | null)"
        :aria-label="frameTileLabel(frame)"
        :aria-pressed="selectedFrameIndex === frame.frame_index"
        class="audit-frame-browser__tile"
        :class="{
          'audit-frame-browser__tile--selected': selectedFrameIndex === frame.frame_index,
          'audit-frame-browser__tile--focused': focusedTileIndex === index,
          [`audit-frame-browser__tile--${frame.severity ?? 'neutral'}`]: frame.is_civic_issue,
        }"
        role="listitem"
        :title="frameTileTooltip(frame)"
        type="button"
        @click="selectFrame(frame.frame_index, index)"
        @focus="focusedTileIndex = index"
      >
        <img
          :alt="`Frame ${frame.frame_index + 1}`"
          class="audit-frame-browser__thumb"
          :loading="lazyLoadThumbnails ? 'lazy' : 'eager'"
          :src="resolveApiAssetUrl(frame.frame_image_url) ?? undefined"
        />
        <div class="audit-frame-browser__tile-meta">
          <strong>#{{ frame.frame_index + 1 }}</strong>
          <span>{{ frame.heading }}°</span>
        </div>
        <AppBadge
          v-if="frame.is_civic_issue && frame.severity"
          class="audit-frame-browser__tile-badge"
          size="sm"
          :tone="getSeverityBadgeTone(frame.severity)"
        >
          {{ formatSeverityLabel(frame.severity) }}
        </AppBadge>
        <AppBadge
          v-else-if="frame.is_civic_issue"
          class="audit-frame-browser__tile-badge"
          size="sm"
          tone="source-ai-audit"
        >
          Issue
        </AppBadge>
      </button>
    </div>

    <p v-if="filteredFrames.length > 0" class="audit-frame-browser__count muted">
      Showing {{ filteredFrames.length }} of {{ frames.length }} analyzed frames
    </p>

    <p
      v-if="selectedFrameDetail"
      aria-live="polite"
      class="audit-frame-browser__selection-status muted"
    >
      Inspecting frame #{{ selectedFrameDetail.frame_index + 1 }}
      <span v-if="selectedFrameDetail.category">
        · {{ categoryLabels[selectedFrameDetail.category] }}
      </span>
    </p>

    <AppCard v-if="selectedFrameIndex !== null && detailError" class="stack" variant="muted">
      <AppBadge tone="danger">Frame detail error</AppBadge>
      <p>{{ detailError }}</p>
    </AppCard>

    <p v-else-if="selectedFrameIndex !== null && isDetailLoading" class="muted">
      Loading selected frame detail...
    </p>

    <AnalyzedFrameViewer
      v-else-if="selectedFrameDetail"
      :category="selectedFrameDetail.category"
      :confidence="selectedFrameDetail.confidence ?? 0"
      :description="selectedFrameDetail.description"
      :frame-index="selectedFrameDetail.frame_index"
      :heading="selectedFrameDetail.heading"
      :image-url="selectedFrameDetail.frame_image_url"
      :pitch="selectedFrameDetail.pitch"
      :regions="selectedFrameDetail.detection_regions"
      :severity="selectedFrameDetail.severity"
      eyebrow="Selected analyzed frame"
      subtitle="Full frame evidence for the tile selected above."
      title="Frame inspection"
    />

    <div
      v-if="selectedFrameDetail?.suggestion_id"
      class="audit-frame-browser__suggestion-link"
    >
      <RouterLink
        :to="{
          name: 'street-audit-suggestion-detail',
          params: { suggestionId: selectedFrameDetail.suggestion_id },
        }"
      >
        Open linked AI suggestion review
      </RouterLink>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import SeverityLegend from '@/components/audit/SeverityLegend.vue';
import { useAuditFramesStore } from '@/stores/auditFrames';
import type { AuditRunStatus } from '@/types/audit';
import type {
  AuditFrameCategoryFilter,
  AuditFrameFilterMode,
  AuditFrameSeverityFilter,
  AuditFrameSummary,
} from '@/types/auditFrame';
import type { AuditSuggestionSeverity } from '@/types/detection';
import type { IssueCategory } from '@/types/report';
import {
  buildFrameTileLabel,
  buildRegionTooltipContent,
  formatSeverityLabel,
  getSeverityBadgeTone,
  resolveApiAssetUrl,
  type RegionOverlayVariant,
} from '@/utils/detectionRegions';
import { categoryLabels } from '@/utils/reportFormatting';

const props = withDefaults(
  defineProps<{
    runId: string;
    runStatus?: AuditRunStatus | null;
    lazyLoadThumbnails?: boolean;
  }>(),
  {
    runStatus: null,
    lazyLoadThumbnails: true,
  },
);

const auditFramesStore = useAuditFramesStore();
const tileRefs = ref<Array<HTMLButtonElement | null>>([]);
const focusedTileIndex = ref(0);
const filterMode = ref<AuditFrameFilterMode>('all');
const severityFilter = ref<AuditFrameSeverityFilter>('all');
const categoryFilter = ref<AuditFrameCategoryFilter>('all');
const selectedFrameIndex = ref<number | null>(null);

const severityOptions: AuditSuggestionSeverity[] = ['low', 'medium', 'high', 'critical'];
const categoryOptions: IssueCategory[] = [
  'pothole',
  'garbage',
  'broken_streetlight',
  'blocked_sidewalk',
  'damaged_sign',
  'other',
];

const frames = computed(() => auditFramesStore.framesForRun(props.runId));
const isLoading = computed(() => auditFramesStore.isLoadingForRun(props.runId));
const error = computed(() => auditFramesStore.errorForRun(props.runId));
const selectedFrameDetail = computed(() =>
  auditFramesStore.frameDetail(props.runId, selectedFrameIndex.value),
);
const isDetailLoading = computed(() =>
  auditFramesStore.isDetailLoading(props.runId, selectedFrameIndex.value),
);
const detailError = computed(() =>
  auditFramesStore.detailError(props.runId, selectedFrameIndex.value),
);

const filteredFrames = computed(() =>
  frames.value.filter((frame) => {
    if (filterMode.value === 'detections' && !frame.is_civic_issue) {
      return false;
    }

    if (severityFilter.value !== 'all' && frame.severity !== severityFilter.value) {
      return false;
    }

    if (categoryFilter.value !== 'all' && frame.category !== categoryFilter.value) {
      return false;
    }

    return true;
  }),
);

watch(
  () => props.runId,
  (runId) => {
    selectedFrameIndex.value = null;
    focusedTileIndex.value = 0;
    if (runId) {
      void auditFramesStore.fetchForRun(runId);
    }
  },
  { immediate: true },
);

watch(
  () => props.runStatus,
  (status) => {
    if (status === 'queued' || status === 'running') {
      void auditFramesStore.fetchForRun(props.runId);
    }
  },
);

watch(filteredFrames, (nextFrames) => {
  tileRefs.value = [];

  if (nextFrames.length === 0) {
    selectedFrameIndex.value = null;
    focusedTileIndex.value = 0;
    return;
  }

  if (focusedTileIndex.value >= nextFrames.length) {
    focusedTileIndex.value = nextFrames.length - 1;
  }

  if (
    selectedFrameIndex.value !== null &&
    !nextFrames.some((frame) => frame.frame_index === selectedFrameIndex.value)
  ) {
    selectedFrameIndex.value = null;
  }
});

function setTileRef(index: number, element: HTMLButtonElement | null) {
  tileRefs.value[index] = element;
}

function frameTileLabel(frame: AuditFrameSummary): string {
  return buildFrameTileLabel({
    frameIndex: frame.frame_index,
    heading: frame.heading,
    isCivicIssue: frame.is_civic_issue,
    category: frame.category ? categoryLabels[frame.category] : null,
    severity: frame.severity,
  });
}

function frameTileTooltip(frame: AuditFrameSummary): string {
  if (!frame.is_civic_issue) {
    return 'No issue detected in this frame.';
  }

  const tooltip = buildRegionTooltipContent({
    category: frame.category ? categoryLabels[frame.category] : null,
    confidence: frame.confidence,
    description: frame.has_detection_regions
      ? 'AI-estimated overlay available on inspection.'
      : 'Detection without pinpointed overlay.',
    severity: frame.severity,
  });

  return `${tooltip.title}. ${tooltip.body}`;
}

function refreshFrames() {
  void auditFramesStore.fetchForRun(props.runId);
}

function selectFrame(frameIndex: number, tileIndex = focusedTileIndex.value) {
  selectedFrameIndex.value = frameIndex;
  focusedTileIndex.value = tileIndex;
  void auditFramesStore.fetchFrameDetail(props.runId, frameIndex);
}

function focusTile(index: number) {
  if (filteredFrames.value.length === 0) {
    return;
  }

  const clampedIndex = Math.max(0, Math.min(index, filteredFrames.value.length - 1));
  focusedTileIndex.value = clampedIndex;
  tileRefs.value[clampedIndex]?.focus();
}

function handleGridKeydown(event: KeyboardEvent) {
  if (filteredFrames.value.length === 0) {
    return;
  }

  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    event.preventDefault();
    focusTile(focusedTileIndex.value + 1);
    return;
  }

  if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    event.preventDefault();
    focusTile(focusedTileIndex.value - 1);
    return;
  }

  if (event.key === 'Home') {
    event.preventDefault();
    focusTile(0);
    return;
  }

  if (event.key === 'End') {
    event.preventDefault();
    focusTile(filteredFrames.value.length - 1);
    return;
  }

  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    const frame = filteredFrames.value[focusedTileIndex.value];
    if (frame) {
      selectFrame(frame.frame_index, focusedTileIndex.value);
    }
  }
}
</script>

<style scoped>
.audit-frame-browser h3 {
  margin: 0;
}

.audit-frame-browser__intro,
.audit-frame-browser__count,
p {
  color: var(--text-secondary);
}

.audit-frame-browser__filters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
}

.audit-frame-browser__filter {
  display: grid;
  gap: var(--space-2);
  min-width: 0;
}

.audit-frame-browser__filter span {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.audit-frame-browser__filter select {
  width: 100%;
  border: var(--border-soft);
  border-radius: var(--radius-sm);
  padding: 0.65rem 0.75rem;
  background: rgba(255, 253, 247, 0.82);
  color: var(--text-primary);
  font: inherit;
}

.audit-frame-browser__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(7.5rem, 1fr));
  gap: var(--space-3);
}

.audit-frame-browser__tile {
  position: relative;
  display: grid;
  gap: var(--space-2);
  padding: var(--space-2);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.72);
  cursor: pointer;
  text-align: left;
}

.audit-frame-browser__tile--selected {
  border-color: var(--source-ai-audit-border);
  box-shadow: 0 0 0 1px rgba(47, 93, 80, 0.12);
}

.audit-frame-browser__tile--focused,
.audit-frame-browser__tile:focus-visible {
  outline: 3px solid rgba(47, 93, 80, 0.35);
  outline-offset: 2px;
}

.audit-frame-browser__selection-status {
  margin: 0;
}

.audit-frame-browser__tile--low {
  border-color: var(--severity-low-border);
}

.audit-frame-browser__tile--medium {
  border-color: var(--severity-medium-border);
}

.audit-frame-browser__tile--high {
  border-color: var(--severity-high-border);
}

.audit-frame-browser__tile--critical {
  border-color: var(--severity-critical-border);
}

.audit-frame-browser__thumb {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: var(--radius-sm);
  background: var(--surface-muted);
}

.audit-frame-browser__tile-meta {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.audit-frame-browser__tile-badge {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
}

.audit-frame-browser__suggestion-link a {
  color: var(--source-ai-audit-text);
  font-weight: 800;
  text-decoration: none;
}

.audit-frame-browser__suggestion-link a:hover {
  text-decoration: underline;
}

@media (max-width: 760px) {
  .audit-frame-browser__filters {
    grid-template-columns: 1fr;
  }
}
</style>
