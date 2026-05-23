<template>
  <div class="audit-detail">
    <template v-if="run">

      <div class="audit-detail__header">
        <div class="audit-detail__intro">
          <h2 class="audit-detail__title">{{ run.route_name }}</h2>
          <div class="audit-detail__meta">
            <span>{{ run.municipality }}</span>
            <span class="audit-detail__sep" aria-hidden="true">·</span>
            <span>{{ formatAuditDateTime(run.created_at) }}</span>
            <span class="audit-detail__sep" aria-hidden="true">·</span>
            <span><strong>{{ issueCount }}</strong> issue{{ issueCount === 1 ? '' : 's' }}</span>
          </div>
        </div>
        <div class="cluster">
          <AuditRunStatusPill :status="run.status" />
          <AppBadge v-if="isDemoData" tone="warning">Demo</AppBadge>
        </div>
      </div>

      <AppCard v-if="isLegacyRun" class="audit-detail__legacy" variant="muted">
        <AppBadge tone="warning">Legacy scan format</AppBadge>
        <p class="audit-detail__legacy-copy">
          This run used the older four-heading capture model. Use the All frames tab for the full filmstrip.
        </p>
        <AppButton
          v-if="activeTab !== 'frames'"
          size="sm"
          type="button"
          variant="secondary"
          @click="activeTab = 'frames'"
        >
          Open All frames
        </AppButton>
      </AppCard>

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
        >All frames</button>
      </div>

      <template v-if="activeTab === 'scanner'">

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

        <div v-if="suggestions.length > 0 || suggestionsLoading" class="audit-detail__detections">
          <div class="audit-detail__detections-head">
            <span class="audit-detail__detections-label">
              {{ suggestions.length }} detection{{ suggestions.length === 1 ? '' : 's' }}
            </span>
            <button
              class="audit-detail__detections-refresh"
              type="button"
              :disabled="suggestionsLoading"
              @click="$emit('refreshSuggestions')"
            >{{ suggestionsLoading ? 'Syncing…' : 'Refresh' }}</button>
          </div>

          <div class="audit-detail__chips" role="list">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion.id"
              class="audit-detail__chip"
              :class="{ 'audit-detail__chip--active': suggestion.id === selectedSuggestionId }"
              type="button"
              role="listitem"
              @click="selectSuggestion(suggestion.id)"
            >
              <span
                class="audit-detail__chip-dot"
                :style="{ background: severityColor(suggestion.severity) }"
                aria-hidden="true"
              />
              <span class="audit-detail__chip-name">{{ categoryLabels[suggestion.category] }}</span>
              <span class="audit-detail__chip-pct">{{ formatConfidence(suggestion.confidence) }}</span>
              <span
                class="audit-detail__chip-badge"
                :class="`audit-detail__chip-badge--${suggestion.status}`"
              >{{ shortStatusLabel(suggestion.status) }}</span>
            </button>
          </div>
        </div>

        <Transition name="review-panel">
          <div v-if="selectedSuggestion" class="audit-detail__review">

            <div class="audit-detail__review-top">
              <div class="audit-detail__review-title-row">
                <h3 class="audit-detail__review-title">{{ categoryLabels[selectedSuggestion.category] }}</h3>
                <AppBadge :tone="selectedStatusTone">{{ statusLabels[selectedSuggestion.status] }}</AppBadge>
              </div>
              <p v-if="selectedSuggestion.description" class="audit-detail__review-desc">
                {{ selectedSuggestion.description }}
              </p>
            </div>

            <div class="audit-detail__review-stats">
              <div class="audit-detail__stat">
                <div class="audit-detail__confidence-track">
                  <span
                    class="audit-detail__confidence-fill"
                    :style="{ width: `${(selectedSuggestion.confidence ?? 0) * 100}%` }"
                  />
                </div>
                <span class="audit-detail__stat-val">{{ formatConfidence(selectedSuggestion.confidence) }}</span>
                <span class="audit-detail__stat-label">confidence</span>
              </div>
              <span class="audit-detail__stat-sep" aria-hidden="true" />
              <div class="audit-detail__stat">
                <span
                  class="audit-detail__stat-val"
                  :class="selectedSuggestion.severity ? `audit-detail__stat-sev--${selectedSuggestion.severity}` : ''"
                >{{ selectedSuggestion.severity ?? 'Unknown' }}</span>
                <span class="audit-detail__stat-label">severity</span>
              </div>
              <span class="audit-detail__stat-sep" aria-hidden="true" />
              <div class="audit-detail__stat">
                <span class="audit-detail__stat-val">{{ selectedSuggestion.department ?? 'Unrouted' }}</span>
                <span class="audit-detail__stat-label">department</span>
              </div>
            </div>

            <div class="audit-detail__form">
              <div class="audit-detail__actions" role="group" aria-label="Review decision">
                <button
                  v-for="opt in reviewOptions"
                  :key="opt.value"
                  type="button"
                  class="audit-detail__action"
                  :class="[`audit-detail__action--${opt.tone}`, { 'audit-detail__action--active': selectedSuggestion.status === opt.value }]"
                  :disabled="isReviewingSelected || selectedSuggestion.status === 'converted_to_report'"
                  @click="quickReview(opt.value)"
                >{{ isReviewingSelected && localReviewStatus === opt.value ? 'Saving…' : opt.label }}</button>
              </div>

              <textarea
                v-model="localReviewerNote"
                class="audit-detail__note"
                :disabled="isReviewingSelected || selectedSuggestion.status === 'converted_to_report'"
                rows="2"
                placeholder="Add a note…"
              />

              <div class="audit-detail__form-footer">
                <p v-if="reviewErrorSelected || convertErrorSelected" class="audit-detail__form-error">
                  {{ reviewErrorSelected ?? convertErrorSelected }}
                </p>
                <div v-if="selectedSuggestion.converted_report_id || convertedReportSelected" class="audit-detail__converted">
                  <AppBadge tone="success">Converted to report</AppBadge>
                  <span class="audit-detail__converted-id">{{ selectedSuggestion.converted_report_id ?? convertedReportSelected }}</span>
                </div>
                <AppButton
                  size="sm"
                  type="button"
                  :disabled="isConvertingSelected || selectedSuggestion.status === 'converted_to_report'"
                  @click="$emit('convertSuggestion', selectedSuggestion.id)"
                >{{ isConvertingSelected ? 'Converting…' : 'Convert to report' }}</AppButton>
              </div>
            </div>

          </div>
        </Transition>

        <AppEmptyState
          v-if="!suggestionsLoading && !scanPathLoading && suggestions.length === 0 && !scanPath.length"
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
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import type { AuditRunSummary, AuditFrameDetail, AuditFrameSummary, AuditScanPoint } from '@/types/audit';
import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';
import type { BadgeTone } from '@/types/ui';
import { formatAuditDateTime } from '@/utils/auditFormatting';
import { isLegacyAuditRun } from '@/utils/auditLegacy';
import { pickInitialScanPoint } from '@/utils/streetView';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';
import AuditRunStatusPill from './AuditRunStatusPill.vue';
import AuditFrameBrowser from './AuditFrameBrowser.vue';
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

const shortLabels: Record<string, string> = {
  pending_review: 'Pending',
  accepted: 'Accepted',
  rejected: 'Rejected',
  needs_manual_review: 'Manual',
  converted_to_report: 'Converted',
};

const activeTab = ref<'scanner' | 'frames'>('scanner');
const selectedFrameIndex = ref<number | null>(null);
const selectedSuggestionId = ref<string | null>(null);
const localReviewStatus = ref<AuditSuggestionReviewPayload['status']>('accepted');
const localReviewerNote = ref('');

const selectedSuggestion = computed(() =>
  props.suggestions.find((s) => s.id === selectedSuggestionId.value) ?? null,
);

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

function severityColor(severity: string | null | undefined): string {
  const map: Record<string, string> = {
    low: '#4a8c6e',
    medium: '#b07d2a',
    high: '#c0522a',
    critical: '#991b1b',
  };
  return map[severity ?? ''] ?? 'rgba(23, 33, 26, 0.2)';
}

function shortStatusLabel(status: string): string {
  return shortLabels[status] ?? status;
}

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
  () => [props.run?.id, props.scanPath] as const,
  ([runId, scanPath]) => {
    if (!runId || !scanPath.length || selectedFrameIndex.value != null) return;
    const initial = pickInitialScanPoint(scanPath);
    selectedFrameIndex.value = initial?.frame_index ?? null;
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

function submitReview() {
  quickReview(localReviewStatus.value);
}
</script>

<style scoped>
.audit-detail {
  display: grid;
  gap: var(--space-4);
}

/* ─── Header ─── */
.audit-detail__header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.audit-detail__title {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.1rem);
  letter-spacing: -0.03em;
}

.audit-detail__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-1);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.audit-detail__meta strong {
  color: var(--text-primary);
  font-weight: 875;
}

.audit-detail__sep {
  color: var(--text-muted);
}

/* ─── Legacy ─── */
.audit-detail__legacy {
  display: grid;
  gap: var(--space-2);
}

.audit-detail__legacy-copy {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

/* ─── Tabs ─── */
.audit-detail__tabs {
  display: flex;
  gap: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid rgba(23, 33, 26, 0.08);
}

.audit-detail__tab {
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-pill);
  padding: var(--space-2) var(--space-4);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.72);
  font-size: var(--text-sm);
  font-weight: 800;
  cursor: pointer;
  transition: color var(--motion-fast) ease, background var(--motion-fast) ease, border-color var(--motion-fast) ease;
}

.audit-detail__tab--active {
  border-color: rgba(47, 93, 80, 0.35);
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.1);
}

/* ─── Detection chips ─── */
.audit-detail__detections {
  display: grid;
  gap: var(--space-2);
}

.audit-detail__detections-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.audit-detail__detections-label {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.audit-detail__detections-refresh {
  border: 0;
  padding: 0;
  color: var(--text-muted);
  background: transparent;
  font-size: var(--text-xs);
  font-weight: 800;
  cursor: pointer;
  transition: color var(--motion-fast) ease;
}

.audit-detail__detections-refresh:hover:not(:disabled) {
  color: var(--text-primary);
}

.audit-detail__detections-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.audit-detail__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.audit-detail__chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.72);
  font-size: var(--text-xs);
  font-weight: 800;
  cursor: pointer;
  transition: border-color var(--motion-fast) ease, background var(--motion-fast) ease, color var(--motion-fast) ease, box-shadow var(--motion-fast) ease;
}

.audit-detail__chip:hover {
  border-color: rgba(23, 33, 26, 0.2);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.95);
}

.audit-detail__chip--active {
  border-color: rgba(47, 93, 80, 0.4);
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.08);
  box-shadow: 0 2px 8px rgba(47, 93, 80, 0.1);
}

.audit-detail__chip-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.audit-detail__chip-name {
  font-weight: 850;
}

.audit-detail__chip-pct {
  color: var(--text-muted);
  font-weight: 700;
}

.audit-detail__chip-badge {
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius-pill);
  font-size: 0.6rem;
  font-weight: 900;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.audit-detail__chip-badge--pending_review { background: rgba(23, 33, 26, 0.07); color: var(--text-muted); }
.audit-detail__chip-badge--accepted { background: rgba(47, 93, 80, 0.12); color: var(--color-municipal-green); }
.audit-detail__chip-badge--rejected { background: rgba(192, 57, 43, 0.1); color: #c0392b; }
.audit-detail__chip-badge--needs_manual_review { background: rgba(176, 125, 42, 0.12); color: #b07d2a; }
.audit-detail__chip-badge--converted_to_report { background: rgba(47, 93, 80, 0.12); color: var(--color-municipal-green); }

/* ─── Review panel ─── */
.audit-detail__review {
  display: grid;
  gap: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid rgba(23, 33, 26, 0.08);
}

.review-panel-enter-active {
  transition: opacity var(--motion-base) ease, transform var(--motion-base) var(--ease-out-expo);
}

.review-panel-leave-active {
  transition: opacity var(--motion-fast) ease;
}

.review-panel-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.review-panel-leave-to {
  opacity: 0;
}

.audit-detail__review-top {
  display: grid;
  gap: var(--space-2);
}

.audit-detail__review-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.audit-detail__review-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 875;
  letter-spacing: -0.02em;
}

.audit-detail__review-desc {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
}

/* ─── Stats row ─── */
.audit-detail__review-stats {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: 1px solid rgba(23, 33, 26, 0.07);
  border-radius: var(--radius-md);
  background: rgba(23, 33, 26, 0.025);
}

.audit-detail__stat {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.audit-detail__confidence-track {
  width: 4rem;
  height: 4px;
  border-radius: var(--radius-pill);
  background: rgba(23, 33, 26, 0.1);
  overflow: hidden;
}

.audit-detail__confidence-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--color-amber-signal), var(--color-municipal-green));
}

.audit-detail__stat-val {
  font-size: var(--text-sm);
  font-weight: 875;
  color: var(--text-primary);
  text-transform: capitalize;
}

.audit-detail__stat-sev--low { color: #4a8c6e; }
.audit-detail__stat-sev--medium { color: #b07d2a; }
.audit-detail__stat-sev--high { color: #c0522a; }
.audit-detail__stat-sev--critical { color: #991b1b; }

.audit-detail__stat-label {
  font-size: var(--text-xs);
  font-weight: 750;
  color: var(--text-muted);
}

.audit-detail__stat-sep {
  width: 1px;
  height: 1.25rem;
  background: rgba(23, 33, 26, 0.1);
  flex-shrink: 0;
}

/* ─── Review form ─── */
.audit-detail__form {
  display: grid;
  gap: var(--space-3);
}

.audit-detail__actions {
  display: flex;
  gap: var(--space-2);
}

.audit-detail__action {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  border: 1.5px solid transparent;
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  font-weight: 800;
  cursor: pointer;
  transition: background var(--motion-fast) ease, color var(--motion-fast) ease, border-color var(--motion-fast) ease;
}

.audit-detail__action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.audit-detail__action--accept {
  border-color: rgba(47, 93, 80, 0.35);
  color: var(--color-municipal-green);
  background: rgba(47, 93, 80, 0.06);
}
.audit-detail__action--accept:hover:not(:disabled),
.audit-detail__action--accept.audit-detail__action--active {
  color: #fff;
  background: var(--color-municipal-green);
  border-color: var(--color-municipal-green);
}

.audit-detail__action--reject {
  border-color: rgba(192, 57, 43, 0.35);
  color: #c0392b;
  background: rgba(192, 57, 43, 0.06);
}
.audit-detail__action--reject:hover:not(:disabled),
.audit-detail__action--reject.audit-detail__action--active {
  color: #fff;
  background: #c0392b;
  border-color: #c0392b;
}

.audit-detail__action--manual {
  border-color: rgba(176, 125, 42, 0.35);
  color: var(--color-amber-signal);
  background: rgba(176, 125, 42, 0.06);
}
.audit-detail__action--manual:hover:not(:disabled),
.audit-detail__action--manual.audit-detail__action--active {
  color: #fff;
  background: var(--color-amber-signal);
  border-color: var(--color-amber-signal);
}

.audit-detail__note {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.72);
  font: inherit;
  font-size: var(--text-sm);
  resize: vertical;
  box-sizing: border-box;
  transition: border-color var(--motion-fast) ease;
}

.audit-detail__note:focus {
  outline: none;
  border-color: rgba(47, 93, 80, 0.4);
}

.audit-detail__note:disabled { opacity: 0.5; }

.audit-detail__form-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.audit-detail__form-error {
  margin: 0;
  color: var(--color-repair-red);
  font-size: var(--text-sm);
  font-weight: 750;
}

.audit-detail__converted {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border: 1px solid rgba(47, 93, 80, 0.15);
  border-radius: var(--radius-md);
  background: rgba(47, 93, 80, 0.05);
}

.audit-detail__converted-id {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 750;
  overflow-wrap: anywhere;
}
</style>
