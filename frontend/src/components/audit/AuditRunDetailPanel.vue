<template>
  <div class="audit-detail">
    <template v-if="run">

      <template v-if="showScanGlobeWaiting">
        <AuditScanGlobeLoading v-if="scanPathLoading" />
        <AuditScanGlobeEmpty v-else @refresh="$emit('refreshScanPath')" />
      </template>

      <template v-else>

      <header class="audit-detail__header">
        <div class="audit-detail__intro">
          <p class="audit-detail__eyebrow">Audit run</p>
          <h2 class="audit-detail__title">{{ run.route_name }}</h2>
          <div class="audit-detail__meta">
            <span>{{ run.municipality }}</span>
            <span class="audit-detail__sep" aria-hidden="true">·</span>
            <span>{{ formatAuditDateTime(run.created_at) }}</span>
            <span class="audit-detail__sep" aria-hidden="true">·</span>
            <span class="audit-detail__issues">{{ issueCount }} issue{{ issueCount === 1 ? '' : 's' }}</span>
          </div>
        </div>
        <div class="audit-detail__status">
          <AuditRunStatusPill :status="run.status" />
          <AppBadge v-if="isDemoData" tone="warning" size="xs">Demo</AppBadge>
        </div>
      </header>

      <p v-if="isLegacyRun" class="audit-detail__legacy">
        <AppBadge tone="warning" size="xs">Legacy</AppBadge>
        Older capture format —
        <button type="button" class="audit-detail__legacy-link" @click="activeTab = 'frames'">view all frames</button>
      </p>

      <div class="audit-detail__tabs" role="tablist" aria-label="Audit run views">
        <button
          class="audit-detail__tab"
          :class="{ 'audit-detail__tab--active': activeTab === 'scanner' }"
          type="button"
          role="tab"
          :aria-selected="activeTab === 'scanner'"
          @click="activeTab = 'scanner'"
        >Scanner</button>
        <button
          class="audit-detail__tab"
          :class="{ 'audit-detail__tab--active': activeTab === 'frames' }"
          type="button"
          role="tab"
          :aria-selected="activeTab === 'frames'"
          @click="activeTab = 'frames'"
        >Frames</button>
      </div>

      <template v-if="activeTab === 'scanner'">

        <section v-if="suggestions.length > 0 || suggestionsLoading" class="audit-detections" aria-label="AI detections">
          <div class="audit-detections__head">
            <div class="audit-detections__intro">
              <span class="audit-detections__label">AI detections</span>
              <p class="audit-detections__hint">Pick a finding — evidence loads below</p>
            </div>
            <div class="audit-detections__tools">
              <span v-if="suggestions.length" class="audit-detections__count">{{ selectedDetectionIndex + 1 }} / {{ suggestions.length }}</span>
              <button
                class="audit-detections__refresh"
                type="button"
                :disabled="suggestionsLoading"
                :title="suggestionsLoading ? 'Syncing' : 'Refresh detections'"
                @click="$emit('refreshSuggestions')"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M4 4v6h6M20 20v-6h-6M20 9A8 8 0 006.34 6.34M4 15a8 8 0 0013.66 2.66" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>
          </div>

          <AppLoading v-if="suggestionsLoading && !suggestions.length" label="Loading detections" />

          <div v-else class="audit-detections__rail" role="list">
            <button
              v-for="(suggestion, index) in suggestions"
              :key="suggestion.id"
              class="audit-detections__card"
              :class="[
                `audit-detections__card--${suggestion.severity ?? 'medium'}`,
                { 'audit-detections__card--active': suggestion.id === selectedSuggestionId },
              ]"
              type="button"
              role="listitem"
              :aria-current="suggestion.id === selectedSuggestionId ? 'true' : undefined"
              @click="selectSuggestion(suggestion.id)"
            >
              <span class="audit-detections__index">{{ index + 1 }}</span>
              <div class="audit-detections__body">
                <strong>{{ categoryLabels[suggestion.category] }}</strong>
                <span class="audit-detections__meta">
                  {{ formatConfidence(suggestion.confidence) }}
                  <span v-if="suggestion.severity" class="audit-detections__sep">·</span>
                  <span v-if="suggestion.severity">{{ suggestion.severity }}</span>
                </span>
              </div>
              <span
                class="audit-detections__status"
                :class="`audit-detections__status--${suggestion.status}`"
                :title="statusLabels[suggestion.status]"
              />
            </button>
          </div>
        </section>

        <Transition name="review-panel">
          <section v-if="selectedSuggestion" class="audit-inspector" aria-label="Detection inspector">
            <div class="audit-inspector__head">
              <h3 class="audit-inspector__title">{{ categoryLabels[selectedSuggestion.category] }}</h3>
              <AppBadge :tone="selectedStatusTone" size="xs">{{ statusLabels[selectedSuggestion.status] }}</AppBadge>
            </div>

            <p v-if="selectedSuggestion.description" class="audit-inspector__desc">
              {{ selectedSuggestion.description }}
            </p>

            <div class="audit-inspector__pill">
              <span
                v-if="selectedSuggestion.severity"
                class="audit-inspector__tag audit-inspector__tag--severity"
                :class="`audit-inspector__tag--severity-${selectedSuggestion.severity}`"
              >
                {{ selectedSuggestion.severity }}
              </span>
              <span class="audit-inspector__tag">{{ formatConfidence(selectedSuggestion.confidence) }}</span>
              <span class="audit-inspector__tag audit-inspector__tag--muted">
                {{ selectedSuggestion.department ?? 'Unrouted' }}
              </span>
            </div>

            <div
              v-if="selectedSuggestion.converted_report_id || convertedReportSelected"
              class="audit-inspector__converted"
            >
              <AppBadge tone="success" size="xs">Converted</AppBadge>
              <span>{{ selectedSuggestion.converted_report_id ?? convertedReportSelected }}</span>
            </div>

            <div class="audit-inspector__toolbar" role="group" aria-label="Review actions">
              <div class="audit-inspector__choices">
                <button
                  v-for="opt in reviewOptions"
                  :key="opt.value"
                  type="button"
                  class="audit-inspector__choice"
                  :class="[
                    `audit-inspector__choice--${opt.tone}`,
                    { 'audit-inspector__choice--active': selectedSuggestion.status === opt.value },
                  ]"
                  :title="opt.label"
                  :disabled="isReviewingSelected || selectedSuggestion.status === 'converted_to_report'"
                  @click="quickReview(opt.value)"
                >
                  <svg v-if="opt.tone === 'accept'" width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  <svg v-else-if="opt.tone === 'reject'" width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
                  </svg>
                  <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M12 6v6l3.5 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                    <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8" />
                  </svg>
                </button>
              </div>

              <input
                v-model="localReviewerNote"
                class="audit-inspector__note"
                type="text"
                :disabled="isReviewingSelected || selectedSuggestion.status === 'converted_to_report'"
                maxlength="1000"
                placeholder="Reviewer note…"
                aria-label="Reviewer note"
              />

              <button
                class="audit-inspector__convert"
                type="button"
                :disabled="isConvertingSelected || selectedSuggestion.status === 'converted_to_report'"
                :title="isConvertingSelected ? 'Converting' : 'Convert to report'"
                @click="$emit('convertSuggestion', selectedSuggestion.id)"
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>

            <p v-if="reviewErrorSelected || convertErrorSelected" class="audit-inspector__error">
              {{ reviewErrorSelected ?? convertErrorSelected }}
            </p>
            <p v-if="isReviewingSelected" class="audit-inspector__hint">Saving review…</p>
          </section>
        </Transition>

        <AuditStreetViewScanner
          :error="scanPathError"
          :is-demo-data="isDemoData"
          :is-loading="scanPathLoading"
          :run="run"
          :scan-path="scanPath"
          :selected-frame-index="selectedFrameIndex"
          :selected-suggestion="selectedSuggestion"
          :suggestions="suggestions"
          @refresh="$emit('refreshScanPath')"
          @analyzed="handleAnalyzed"
          @scan-point-selected="selectScanPoint"
        />

        <AppEmptyState
          v-if="!suggestionsLoading && !scanPathLoading && suggestions.length === 0"
          tone="audit"
          title="No detections yet"
          description="The AI pipeline has not returned detections for this run."
        />

      </template>

      <AuditFrameBrowser
        v-else-if="activeTab === 'frames'"
        :error="framesError"
        :frames="frames"
        :is-loading="framesLoading"
        :run-id="run.id"
        @refresh="$emit('refreshFrames')"
      />

      </template>

    </template>

    <AppEmptyState
      v-else
      tone="audit"
      title="Select an audit run"
      description="Choose a run from the queue to review AI detections."
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import type { AuditRunSummary, AuditFrameDetail, AuditFrameSummary, AuditScanPoint } from '@/types/audit';
import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';
import type { BadgeTone } from '@/types/ui';
import { formatAuditDateTime } from '@/utils/auditFormatting';
import { isLegacyAuditRun } from '@/utils/auditLegacy';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';
import AuditRunStatusPill from './AuditRunStatusPill.vue';
import AuditFrameBrowser from './AuditFrameBrowser.vue';
import AuditScanGlobeEmpty from './AuditScanGlobeEmpty.vue';
import AuditScanGlobeLoading from './AuditScanGlobeLoading.vue';
import AuditStreetViewScanner from './AuditStreetViewScanner.vue';

const props = withDefaults(
  defineProps<{
    run: AuditRunSummary | null;
    isDemoData?: boolean;
    suggestions?: AuditSuggestion[];
    scanPath?: AuditScanPoint[];
    scanPathLoading?: boolean;
    scanPathError?: string | null;
    frames?: AuditFrameSummary[];
    framesLoading?: boolean;
    framesError?: string | null;
    suggestionsLoading?: boolean;
    suggestionsError?: string | null;
    reviewLoadingById?: Record<string, boolean>;
    reviewErrorById?: Record<string, string | null>;
    convertLoadingById?: Record<string, boolean>;
    convertErrorById?: Record<string, string | null>;
    convertedReportBySuggestionId?: Record<string, string>;
  }>(),
  {
    isDemoData: false,
    suggestions: () => [],
    scanPath: () => [],
    scanPathLoading: false,
    scanPathError: null,
    frames: () => [],
    framesLoading: false,
    framesError: null,
    suggestionsLoading: false,
    suggestionsError: null,
    reviewLoadingById: () => ({}),
    reviewErrorById: () => ({}),
    convertLoadingById: () => ({}),
    convertErrorById: () => ({}),
    convertedReportBySuggestionId: () => ({}),
  },
);

const emit = defineEmits<{
  refreshSuggestions: [];
  refreshFrames: [];
  refreshScanPath: [];
  reviewSuggestion: [suggestionId: string, payload: AuditSuggestionReviewPayload];
  convertSuggestion: [suggestionId: string];
  analyzed: [frame: AuditFrameDetail];
}>();

const reviewOptions = [
  { value: 'accepted' as const, label: 'Accept', tone: 'accept' },
  { value: 'rejected' as const, label: 'Reject', tone: 'reject' },
  { value: 'needs_manual_review' as const, label: 'Manual review', tone: 'manual' },
];

const statusLabels: Record<AuditSuggestion['status'], string> = {
  pending_review: 'Pending review',
  accepted: 'Accepted',
  rejected: 'Rejected',
  needs_manual_review: 'Manual review',
  converted_to_report: 'Converted',
};

const activeTab = ref<'scanner' | 'frames'>('scanner');
const selectedFrameIndex = ref<number | null>(null);
const selectedSuggestionId = ref<string | null>(null);

const isPipelineActive = computed(
  () => props.run?.status === 'running' || props.run?.status === 'queued',
);

const showScanGlobeWaiting = computed(
  () =>
    activeTab.value === 'scanner' &&
    !props.scanPathError &&
    props.scanPath.length === 0 &&
    !isPipelineActive.value,
);
const localReviewStatus = ref<AuditSuggestionReviewPayload['status']>('accepted');
const localReviewerNote = ref('');

const selectedSuggestion = computed(() =>
  props.suggestions.find((s) => s.id === selectedSuggestionId.value) ?? null,
);

const selectedDetectionIndex = computed(() => {
  const index = props.suggestions.findIndex((s) => s.id === selectedSuggestionId.value);
  return index >= 0 ? index : 0;
});

const isLegacyRun = computed(() =>
  props.run ? isLegacyAuditRun(props.run, props.scanPath.length) : false,
);

const issueCount = computed(() => {
  const fromScanPath = props.scanPath.filter((p) => p.is_civic_issue).length;
  if (fromScanPath > 0) return fromScanPath;
  const fromFrames = props.frames.filter((f) => f.is_civic_issue).length;
  if (fromFrames > 0) return fromFrames;
  return props.suggestions.length;
});

const isReviewingSelected = computed(() =>
  selectedSuggestion.value ? (props.reviewLoadingById[selectedSuggestion.value.id] ?? false) : false,
);
const reviewErrorSelected = computed(() =>
  selectedSuggestion.value ? (props.reviewErrorById[selectedSuggestion.value.id] ?? null) : null,
);
const isConvertingSelected = computed(() =>
  selectedSuggestion.value ? (props.convertLoadingById[selectedSuggestion.value.id] ?? false) : false,
);
const convertErrorSelected = computed(() =>
  selectedSuggestion.value ? (props.convertErrorById[selectedSuggestion.value.id] ?? null) : null,
);
const convertedReportSelected = computed(() =>
  selectedSuggestion.value ? (props.convertedReportBySuggestionId[selectedSuggestion.value.id] ?? null) : null,
);

const selectedStatusTone = computed<BadgeTone>(() => {
  if (!selectedSuggestion.value) return 'info';
  const s = selectedSuggestion.value.status;
  if (s === 'accepted' || s === 'converted_to_report') return 'success';
  if (s === 'rejected') return 'danger';
  if (s === 'needs_manual_review') return 'warning';
  return 'info';
});

watch(
  () => props.run?.id,
  () => {
    activeTab.value =
      props.run && isLegacyAuditRun(props.run, props.scanPath.length) ? 'frames' : 'scanner';
    selectedFrameIndex.value = null;
    selectedSuggestionId.value = null;
  },
);

watch(
  () => [props.run?.id, props.suggestions] as const,
  ([runId, suggestions]) => {
    if (!runId) return;
    if (!suggestions.length) {
      selectedSuggestionId.value = null;
      return;
    }
    const current = suggestions.find((s) => s.id === selectedSuggestionId.value);
    if (!current) {
      const first = suggestions[0];
      selectedSuggestionId.value = first.id;
      if (first.frame_index != null) {
        selectedFrameIndex.value = first.frame_index;
      }
    }
  },
  { immediate: true },
);

watch(
  () => selectedSuggestion.value,
  (suggestion) => {
    if (!suggestion) return;
    const s = suggestion.status;
    localReviewStatus.value =
      s === 'accepted' || s === 'rejected' || s === 'needs_manual_review' ? s : 'accepted';
    localReviewerNote.value = suggestion.reviewer_note ?? '';
  },
  { immediate: true },
);

function handleAnalyzed(frame: AuditFrameDetail) {
  selectedFrameIndex.value = frame.frame_index;
  if (frame.suggestion_id) selectedSuggestionId.value = frame.suggestion_id;
  emit('analyzed', frame);
  emit('refreshScanPath');
  emit('refreshSuggestions');
  emit('refreshFrames');
}

function selectScanPoint(frameIndex: number) {
  selectedFrameIndex.value = frameIndex;
  selectedSuggestionId.value = null;
  const linked = props.scanPath.find((p) => p.frame_index === frameIndex)?.suggestion_id;
  if (linked) selectedSuggestionId.value = linked;
}

function selectSuggestion(suggestionId: string) {
  selectedSuggestionId.value = suggestionId;
  const suggestion = props.suggestions.find((s) => s.id === suggestionId);
  if (suggestion?.frame_index != null) selectedFrameIndex.value = suggestion.frame_index;
}

function quickReview(status: AuditSuggestionReviewPayload['status']) {
  if (!selectedSuggestion.value || isReviewingSelected.value) return;
  localReviewStatus.value = status;
  emit('reviewSuggestion', selectedSuggestion.value.id, {
    status,
    reviewer_note: localReviewerNote.value.trim() || null,
  });
}

</script>

<style scoped>
.audit-detail {
  display: grid;
  gap: 0.65rem;
}

.audit-detail__header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.audit-detail__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.audit-detail__title {
  margin: 0;
  font-size: clamp(1.05rem, 2vw, 1.35rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.15;
}

.audit-detail__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.3rem;
  margin-top: 0.15rem;
  color: var(--text-secondary);
  font-size: 0.68rem;
}

.audit-detail__issues {
  color: var(--color-amber-signal);
  font-weight: 800;
}

.audit-detail__sep {
  color: var(--text-muted);
}

.audit-detail__status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.audit-detail__legacy {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  color: var(--text-muted);
  font-size: 0.65rem;
}

.audit-detail__legacy-link {
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--color-municipal-green);
  font: inherit;
  font-weight: 750;
  cursor: pointer;
  text-decoration: underline;
}

.audit-detail__tabs {
  display: inline-flex;
  align-self: flex-start;
  gap: 0.2rem;
  padding: 0.2rem;
  border-radius: var(--radius-pill);
  background: var(--surface-inset);
  border: var(--border-soft);
}

.audit-detail__tab {
  border: 0;
  border-radius: var(--radius-pill);
  padding: 0.35rem 0.75rem;
  color: var(--text-muted);
  background: transparent;
  font-size: 0.68rem;
  font-weight: 800;
  cursor: pointer;
  transition: color var(--motion-fast) ease, background var(--motion-fast) ease;
}

.audit-detail__tab--active {
  color: var(--text-primary);
  background: var(--surface-panel-strong);
  box-shadow: var(--shadow-inset);
}

.audit-detections {
  display: grid;
  gap: 0.45rem;
  padding: 0.55rem 0.65rem;
  border: var(--border-soft);
  border-radius: var(--radius-lg);
  background: color-mix(in srgb, var(--surface-panel-strong) 90%, transparent);
}

.audit-detections__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.audit-detections__intro {
  display: grid;
  gap: 0.12rem;
}

.audit-detections__label {
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.audit-detections__hint {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.65rem;
}

.audit-detections__tools {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}

.audit-detections__count {
  font-size: 0.62rem;
  font-weight: 800;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.audit-detections__refresh {
  display: grid;
  place-items: center;
  width: 1.65rem;
  height: 1.65rem;
  border: 0;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  background: transparent;
  cursor: pointer;
}

.audit-detections__refresh:hover:not(:disabled) {
  color: var(--text-primary);
  background: color-mix(in srgb, var(--text-muted) 12%, transparent);
}

.audit-detections__refresh:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.audit-detections__rail {
  display: flex;
  gap: 0.45rem;
  overflow-x: auto;
  padding-bottom: 0.1rem;
  scrollbar-width: none;
}

.audit-detections__rail::-webkit-scrollbar {
  display: none;
}

.audit-detections__card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-shrink: 0;
  min-width: 9.5rem;
  padding: 0.5rem 0.6rem 0.5rem 0.55rem;
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface-inset);
  color: var(--text-secondary);
  text-align: left;
  cursor: pointer;
  transition:
    border-color var(--motion-fast) ease,
    background var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease,
    transform var(--motion-fast) ease;
}

.audit-detections__card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.35rem;
  bottom: 0.35rem;
  width: 3px;
  border-radius: 999px;
  background: rgba(23, 33, 26, 0.15);
}

.audit-detections__card--low::before { background: #22c55e; }
.audit-detections__card--medium::before { background: #eab308; }
.audit-detections__card--high::before,
.audit-detections__card--critical::before { background: #ef4444; }

.audit-detections__card--active {
  border-color: color-mix(in srgb, var(--color-municipal-green) 45%, var(--status-new-border));
  background: color-mix(in srgb, var(--color-municipal-green) 14%, var(--surface-inset));
  box-shadow: 0 4px 14px color-mix(in srgb, var(--color-municipal-green) 18%, transparent);
  transform: translateY(-1px);
}

.audit-detections__index {
  display: grid;
  place-items: center;
  width: 1.35rem;
  height: 1.35rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--text-muted) 18%, transparent);
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 900;
  flex-shrink: 0;
}

.audit-detections__card--active .audit-detections__index {
  background: var(--color-municipal-green);
  color: #fff;
}

.audit-detections__body {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
  flex: 1;
}

.audit-detections__body strong {
  font-size: 0.72rem;
  font-weight: 900;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.audit-detections__meta {
  font-size: 0.6rem;
  font-weight: 750;
  color: var(--text-muted);
  text-transform: capitalize;
}

.audit-detections__sep {
  margin: 0 0.1rem;
}

.audit-detections__status {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 999px;
  flex-shrink: 0;
  background: rgba(23, 33, 26, 0.2);
}

.audit-detections__status--accepted,
.audit-detections__status--converted_to_report {
  background: var(--color-municipal-green);
}

.audit-detections__status--rejected {
  background: #c0392b;
}

.audit-detections__status--needs_manual_review {
  background: var(--color-amber-signal);
}

.audit-detections__status--pending_review {
  background: rgba(23, 33, 26, 0.22);
}

.review-panel-enter-active {
  transition: opacity var(--motion-base) ease, transform var(--motion-base) var(--ease-out-expo);
}

.review-panel-leave-active {
  transition: opacity var(--motion-fast) ease;
}

.review-panel-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.review-panel-leave-to {
  opacity: 0;
}

.audit-inspector {
  display: grid;
  gap: 0.45rem;
  padding: 0.65rem 0.75rem;
  border: var(--border-soft);
  border-radius: var(--radius-lg);
  background: color-mix(in srgb, var(--surface-panel-strong) 92%, transparent);
}

.audit-inspector__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.audit-inspector__title {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 900;
  letter-spacing: -0.02em;
}

.audit-inspector__desc {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.audit-inspector__pill {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.3rem;
  width: fit-content;
  padding: 0.28rem 0.55rem;
  border-radius: 999px;
  background: var(--surface-inset);
  border: var(--border-soft);
}

.audit-inspector__tag {
  font-size: 0.62rem;
  font-weight: 800;
  color: var(--text-primary);
  text-transform: capitalize;
}

.audit-inspector__tag--muted {
  color: var(--text-muted);
  text-transform: none;
}

.audit-inspector__tag--severity {
  padding: 0.12rem 0.42rem;
  border-radius: 999px;
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.audit-inspector__tag--severity-low { background: rgba(34, 197, 94, 0.14); color: #16a34a; }
.audit-inspector__tag--severity-medium { background: rgba(234, 179, 8, 0.16); color: #b45309; }
.audit-inspector__tag--severity-high,
.audit-inspector__tag--severity-critical { background: rgba(239, 68, 68, 0.14); color: #dc2626; }

.audit-inspector__converted {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.62rem;
  color: var(--text-muted);
  overflow-wrap: anywhere;
}

.audit-inspector__toolbar {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding-top: 0.35rem;
  border-top: var(--border-soft);
}

.audit-inspector__choices {
  display: flex;
  gap: 0.3rem;
  flex-shrink: 0;
}

.audit-inspector__choice--accept { --action: var(--color-municipal-green); }
.audit-inspector__choice--reject { --action: #c0392b; }
.audit-inspector__choice--manual { --action: var(--color-amber-signal); }

.audit-inspector__choice {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border: 1px solid color-mix(in srgb, var(--action) 30%, transparent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--action) 8%, transparent);
  color: var(--action);
  cursor: pointer;
  transition: background var(--motion-fast) ease, border-color var(--motion-fast) ease, color var(--motion-fast) ease;
}

.audit-inspector__choice--active,
.audit-inspector__choice:hover:not(:disabled) {
  background: var(--action);
  border-color: var(--action);
  color: #fff;
}

.audit-inspector__choice:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.audit-inspector__note {
  flex: 1;
  min-width: 0;
  height: 2rem;
  padding: 0 0.55rem;
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface-inset);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.68rem;
}

.audit-inspector__note::placeholder {
  color: var(--text-muted);
}

.audit-inspector__note:focus {
  outline: none;
  border-color: color-mix(in srgb, var(--color-municipal-green) 40%, var(--status-new-border));
}

.audit-inspector__convert {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  flex-shrink: 0;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--color-municipal-green);
  color: #fff;
  cursor: pointer;
}

.audit-inspector__convert:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.audit-inspector__error {
  margin: 0;
  font-size: 0.62rem;
  font-weight: 700;
  color: var(--color-repair-red);
}

.audit-inspector__hint {
  margin: 0;
  font-size: 0.6rem;
  color: var(--text-muted);
}

@media (max-width: 640px) {
  .audit-detail__header {
    flex-direction: column;
  }

  .audit-detail__status {
    flex-direction: row;
    align-items: center;
    width: 100%;
  }

  .audit-detail__tabs {
    width: 100%;
    justify-content: stretch;
  }

  .audit-detail__tab {
    flex: 1;
    text-align: center;
  }

  .audit-detections__head {
    flex-direction: column;
    align-items: stretch;
    gap: 0.35rem;
  }

  .audit-detections__tools {
    justify-content: space-between;
    width: 100%;
  }

  .audit-inspector__head {
    flex-direction: column;
    gap: 0.35rem;
  }

  .audit-inspector__toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .audit-inspector__choices {
    flex-direction: column;
    width: 100%;
  }

  .audit-inspector__choice {
    width: 100%;
    justify-content: center;
  }

  .audit-inspector__convert {
    width: 100%;
  }
}
</style>
