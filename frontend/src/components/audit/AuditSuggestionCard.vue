<template>
  <AppCard class="audit-suggestion-card" variant="inset">
    <div class="audit-suggestion-card__header">
      <h3 class="audit-suggestion-card__title">{{ categoryLabels[suggestion.category] }}</h3>
      <div class="audit-suggestion-card__header-actions">
        <button
          v-if="showScannerAction"
          class="audit-suggestion-card__locate"
          type="button"
          :aria-label="`Locate on scanner`"
          @click="$emit('select', suggestion.id)"
        >
          <svg viewBox="0 0 24 24" fill="none" width="13" height="13" aria-hidden="true">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" />
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.5" />
            <path d="M12 3v3M12 18v3M3 12h3M18 12h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          </svg>
          Locate
        </button>
        <AppBadge :tone="statusTone">{{ statusLabel }}</AppBadge>
      </div>
    </div>

    <p v-if="suggestion.description" class="audit-suggestion-card__description">
      {{ suggestion.description }}
    </p>

    <div class="audit-suggestion-card__meta">
      <div class="audit-suggestion-card__meta-item">
        <span class="audit-suggestion-card__meta-label">Confidence</span>
        <div class="audit-suggestion-card__confidence">
          <div class="audit-suggestion-card__confidence-track">
            <span
              class="audit-suggestion-card__confidence-fill"
              :style="{ width: `${(suggestion.confidence ?? 0) * 100}%` }"
            />
          </div>
          <span class="audit-suggestion-card__confidence-value">{{ formatConfidence(suggestion.confidence) }}</span>
        </div>
      </div>
      <div class="audit-suggestion-card__meta-item">
        <span class="audit-suggestion-card__meta-label">Severity</span>
        <span
          class="audit-suggestion-card__severity"
          :class="suggestion.severity ? `audit-suggestion-card__severity--${suggestion.severity}` : ''"
        >{{ suggestion.severity ?? 'Unknown' }}</span>
      </div>
      <div class="audit-suggestion-card__meta-item">
        <span class="audit-suggestion-card__meta-label">Department</span>
        <span>{{ suggestion.department ?? 'Unrouted' }}</span>
      </div>
      <div class="audit-suggestion-card__meta-item">
        <span class="audit-suggestion-card__meta-label">Detected</span>
        <span>{{ formatDateTime(suggestion.created_at) }}</span>
      </div>
    </div>

    <AppCard v-if="!compact && suggestion.frame_image_url" class="audit-suggestion-card__evidence" variant="muted">
      <AnalyzedFrameViewer
        layout="compact"
        :category="suggestion.category"
        :confidence="suggestion.confidence"
        :description="suggestion.description ?? undefined"
        :frame-index="suggestion.frame_index ?? undefined"
        :heading="suggestion.heading ?? undefined"
        :image-url="suggestion.frame_image_url"
        :latitude="suggestion.latitude"
        :longitude="suggestion.longitude"
        :pitch="suggestion.pitch ?? undefined"
        :regions="suggestion.detection_regions ?? []"
        :severity="suggestion.severity ?? undefined"
        :show-metadata="false"
      />
      <div class="audit-suggestion-card__evidence-footer">
        <AppBadge tone="source-ai-audit">Evidence</AppBadge>
        <span class="audit-suggestion-card__attribution">{{ suggestion.image_attribution ?? 'Attribution not returned' }}</span>
      </div>
      <p v-if="suggestion.explanation" class="audit-suggestion-card__explanation">{{ suggestion.explanation }}</p>
      <RouterLink
        class="audit-suggestion-card__detail-link"
        :to="{ name: 'street-audit-suggestion-detail', params: { suggestionId: suggestion.id } }"
      >
        Open full analyzed frame
        <svg viewBox="0 0 16 16" fill="none" width="12" height="12" aria-hidden="true">
          <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </RouterLink>
    </AppCard>

    <form class="audit-suggestion-card__review" @submit.prevent="submitReview">
      <div class="audit-suggestion-card__review-header">
        <span class="audit-suggestion-card__review-label">Review decision</span>
      </div>

      <div class="audit-suggestion-card__segment" role="group" aria-label="Review decision">
        <button
          v-for="opt in reviewOptions"
          :key="opt.value"
          type="button"
          class="audit-suggestion-card__seg-btn"
          :class="{ 'audit-suggestion-card__seg-btn--active': reviewStatus === opt.value, [`audit-suggestion-card__seg-btn--${opt.tone}`]: reviewStatus === opt.value }"
          :disabled="isReviewing || suggestion.status === 'converted_to_report'"
          @click="reviewStatus = opt.value"
        >{{ opt.label }}</button>
      </div>

      <textarea
        v-model="reviewerNote"
        class="audit-suggestion-card__note"
        :disabled="isReviewing || suggestion.status === 'converted_to_report'"
        rows="2"
        placeholder="Optional note for municipal review history…"
      />

      <div class="audit-suggestion-card__actions">
        <AppButton
          :disabled="isReviewing || suggestion.status === 'converted_to_report'"
          type="submit"
          variant="secondary"
          size="sm"
        >
          {{ isReviewing ? 'Saving…' : 'Save review' }}
        </AppButton>
        <AppButton
          :disabled="isConverting || suggestion.status === 'converted_to_report'"
          type="button"
          size="sm"
          @click="$emit('convert', suggestion.id)"
        >
          {{ isConverting ? 'Converting…' : 'Convert to report' }}
        </AppButton>
      </div>
    </form>

    <AppCard v-if="suggestion.reviewer_note" class="audit-suggestion-card__note-card" variant="muted">
      <AppBadge tone="info">Reviewer note</AppBadge>
      <p>{{ suggestion.reviewer_note }}</p>
    </AppCard>

    <AppCard v-if="suggestion.converted_report_id || convertedReportId" variant="muted">
      <AppBadge tone="success">Converted to report</AppBadge>
      <p class="audit-suggestion-card__report-id">{{ suggestion.converted_report_id ?? convertedReportId }}</p>
    </AppCard>

    <AppCard v-if="reviewError || convertError" class="audit-suggestion-card__error" variant="inset">
      <AppBadge tone="danger">Action failed</AppBadge>
      <p>{{ reviewError ?? convertError }}</p>
    </AppCard>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';
import type { BadgeTone } from '@/types/ui';
import {
  categoryLabels,
  formatConfidence,
  formatDateTime,
} from '@/utils/reportFormatting';

const props = defineProps<{
  suggestion: AuditSuggestion;
  compact?: boolean;
  showScannerAction?: boolean;
  isReviewing?: boolean;
  isConverting?: boolean;
  reviewError?: string | null;
  convertError?: string | null;
  convertedReportId?: string | null;
}>();

const emit = defineEmits<{
  review: [suggestionId: string, payload: AuditSuggestionReviewPayload];
  convert: [suggestionId: string];
  select: [suggestionId: string];
}>();

const reviewOptions = [
  { value: 'accepted' as const, label: 'Accept', tone: 'accept' },
  { value: 'rejected' as const, label: 'Reject', tone: 'reject' },
  { value: 'needs_manual_review' as const, label: 'Manual review', tone: 'manual' },
];

const reviewStatus = ref<AuditSuggestionReviewPayload['status']>('accepted');
const reviewerNote = ref('');

const suggestionReviewStatus = computed(() =>
  props.suggestion.status === 'accepted' ||
  props.suggestion.status === 'rejected' ||
  props.suggestion.status === 'needs_manual_review'
    ? props.suggestion.status
    : 'accepted',
);

watch(
  () => props.suggestion,
  (suggestion) => {
    reviewStatus.value = suggestionReviewStatus.value;
    reviewerNote.value = suggestion.reviewer_note ?? '';
  },
  { immediate: true },
);

const statusLabels: Record<AuditSuggestion['status'], string> = {
  pending_review: 'Pending review',
  accepted: 'Accepted',
  rejected: 'Rejected',
  needs_manual_review: 'Manual review',
  converted_to_report: 'Converted',
};

const statusTone = computed<BadgeTone>(() => {
  if (props.suggestion.status === 'accepted' || props.suggestion.status === 'converted_to_report') {
    return 'success';
  }
  if (props.suggestion.status === 'rejected') return 'danger';
  if (props.suggestion.status === 'needs_manual_review') return 'warning';
  return 'info';
});

const statusLabel = computed(() => statusLabels[props.suggestion.status]);

function submitReview() {
  emit('review', props.suggestion.id, {
    status: reviewStatus.value,
    reviewer_note: reviewerNote.value.trim() ? reviewerNote.value.trim() : null,
  });
}
</script>

<style scoped>
.audit-suggestion-card {
  display: grid;
  gap: var(--space-3);
}

.audit-suggestion-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
}

.audit-suggestion-card__title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 875;
  letter-spacing: -0.015em;
  line-height: 1.25;
}

.audit-suggestion-card__header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.audit-suggestion-card__locate {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.12);
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.72);
  font-size: var(--text-xs);
  font-weight: 800;
  cursor: pointer;
  transition: color var(--motion-fast) ease, border-color var(--motion-fast) ease, background var(--motion-fast) ease;
}

.audit-suggestion-card__locate:hover {
  color: var(--color-municipal-green);
  border-color: rgba(47, 93, 80, 0.35);
  background: rgba(47, 93, 80, 0.06);
}

.audit-suggestion-card__description {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.audit-suggestion-card__meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.07);
  border-radius: var(--radius-md);
  background: rgba(23, 33, 26, 0.025);
}

.audit-suggestion-card__meta-item {
  display: grid;
  gap: var(--space-1);
}

.audit-suggestion-card__meta-label {
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.audit-suggestion-card__meta-item > span:not(.audit-suggestion-card__meta-label):not(.audit-suggestion-card__confidence) {
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 800;
}

.audit-suggestion-card__confidence {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.audit-suggestion-card__confidence-track {
  flex: 1;
  height: 4px;
  border-radius: var(--radius-pill);
  background: rgba(23, 33, 26, 0.1);
  overflow: hidden;
}

.audit-suggestion-card__confidence-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--color-amber-signal), var(--color-municipal-green));
}

.audit-suggestion-card__confidence-value {
  font-size: var(--text-sm);
  font-weight: 800;
  color: var(--text-primary);
  flex-shrink: 0;
}

.audit-suggestion-card__severity {
  font-size: var(--text-sm);
  font-weight: 800;
  text-transform: capitalize;
  color: var(--text-primary);
}

.audit-suggestion-card__severity--low { color: #4a8c6e; }
.audit-suggestion-card__severity--medium { color: #b07d2a; }
.audit-suggestion-card__severity--high { color: #c0522a; }
.audit-suggestion-card__severity--critical { color: #991b1b; }

.audit-suggestion-card__evidence {
  display: grid;
  gap: var(--space-2);
}

.audit-suggestion-card__evidence-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.audit-suggestion-card__attribution {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 750;
}

.audit-suggestion-card__explanation {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.45;
}

.audit-suggestion-card__detail-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--source-ai-audit-text);
  font-size: var(--text-sm);
  font-weight: 900;
  text-decoration: none;
}

.audit-suggestion-card__detail-link:hover { text-decoration: underline; }

.audit-suggestion-card__review {
  display: grid;
  gap: var(--space-3);
  padding: var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.07);
  border-radius: var(--radius-md);
}

.audit-suggestion-card__review-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.audit-suggestion-card__review-label {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.audit-suggestion-card__segment {
  display: flex;
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.audit-suggestion-card__seg-btn {
  flex: 1;
  padding: var(--space-2) var(--space-2);
  border: 0;
  border-right: 1px solid rgba(23, 33, 26, 0.1);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.6);
  font-size: var(--text-xs);
  font-weight: 800;
  cursor: pointer;
  transition: color var(--motion-fast) ease, background var(--motion-fast) ease;
}

.audit-suggestion-card__seg-btn:last-child {
  border-right: 0;
}

.audit-suggestion-card__seg-btn:hover:not(:disabled) {
  background: rgba(23, 33, 26, 0.04);
  color: var(--text-primary);
}

.audit-suggestion-card__seg-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.audit-suggestion-card__seg-btn--active.audit-suggestion-card__seg-btn--accept {
  color: #fff;
  background: var(--color-municipal-green);
}

.audit-suggestion-card__seg-btn--active.audit-suggestion-card__seg-btn--reject {
  color: #fff;
  background: #c0392b;
}

.audit-suggestion-card__seg-btn--active.audit-suggestion-card__seg-btn--manual {
  color: #fff;
  background: var(--color-amber-signal);
}

.audit-suggestion-card__note {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.72);
  font: inherit;
  font-size: var(--text-sm);
  resize: vertical;
  transition: border-color var(--motion-fast) ease;
}

.audit-suggestion-card__note:focus {
  outline: none;
  border-color: rgba(47, 93, 80, 0.4);
}

.audit-suggestion-card__note:disabled {
  opacity: 0.5;
}

.audit-suggestion-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.audit-suggestion-card__note-card,
.audit-suggestion-card__error {
  display: grid;
  gap: var(--space-2);
}

.audit-suggestion-card__note-card p,
.audit-suggestion-card__error p,
.audit-suggestion-card__report-id {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

@media (max-width: 640px) {
  .audit-suggestion-card__header {
    flex-direction: column;
    gap: var(--space-2);
  }

  .audit-suggestion-card__header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .audit-suggestion-card__meta {
    grid-template-columns: 1fr;
  }

  .audit-suggestion-card__segment {
    flex-direction: column;
  }

  .audit-suggestion-card__seg-btn {
    border-right: 0;
    border-bottom: 1px solid rgba(23, 33, 26, 0.1);
  }

  .audit-suggestion-card__seg-btn:last-child {
    border-bottom: 0;
  }
}
</style>
