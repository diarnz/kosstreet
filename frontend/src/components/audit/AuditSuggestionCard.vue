<template>
  <AppCard class="audit-suggestion-card" variant="inset">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">AI suggestion</p>
        <h3>{{ categoryLabels[suggestion.category] }}</h3>
      </div>
      <div class="cluster">
        <AppBadge :tone="categoryTone"> {{ categoryLabels[suggestion.category] }} </AppBadge>
        <AppBadge :tone="statusTone">{{ statusLabel }}</AppBadge>
      </div>
    </div>

    <p class="audit-suggestion-card__description">
      {{ suggestion.description ?? 'No model description returned.' }}
    </p>

    <dl class="audit-suggestion-card__grid">
      <div>
        <dt>Confidence</dt>
        <dd>{{ formatConfidence(suggestion.confidence) }}</dd>
      </div>
      <div>
        <dt>Severity</dt>
        <dd>{{ suggestion.severity ?? 'Not set' }}</dd>
      </div>
      <div>
        <dt>Location</dt>
        <dd>{{ formatCoordinates(suggestion.latitude, suggestion.longitude) }}</dd>
      </div>
      <div>
        <dt>Department</dt>
        <dd>{{ suggestion.department ?? 'Not routed' }}</dd>
      </div>
      <div>
        <dt>Frame</dt>
        <dd>Heading {{ suggestion.heading ?? 'n/a' }}, pitch {{ suggestion.pitch ?? 'n/a' }}</dd>
      </div>
      <div>
        <dt>Created</dt>
        <dd>{{ formatDateTime(suggestion.created_at) }}</dd>
      </div>
    </dl>

    <AppCard class="audit-suggestion-card__evidence" variant="muted">
      <div class="cluster-between">
        <AppBadge tone="source-ai-audit">Evidence</AppBadge>
        <span>{{ suggestion.image_attribution ?? 'Attribution not returned' }}</span>
      </div>
      <p>{{ suggestion.explanation ?? 'No model explanation returned.' }}</p>
      <RouterLink
        class="audit-suggestion-card__street-view-link"
        :to="{ name: 'street-audit-suggestion-detail', params: { suggestionId: suggestion.id } }"
      >
        Open Google Street View context
      </RouterLink>
      <p v-if="hasHiddenProviderUrl" class="muted">
        Street View evidence URL is stored by the backend. Raw provider URLs are not rendered because
        they may contain API credentials.
      </p>
    </AppCard>

    <form class="audit-suggestion-card__review" @submit.prevent="submitReview">
      <label>
        Review decision
        <select v-model="reviewStatus" :disabled="isReviewing || suggestion.status === 'converted_to_report'">
          <option value="accepted">Accept</option>
          <option value="rejected">Reject</option>
          <option value="needs_manual_review">Needs manual review</option>
        </select>
      </label>

      <label>
        Reviewer note
        <textarea
          v-model="reviewerNote"
          :disabled="isReviewing || suggestion.status === 'converted_to_report'"
          rows="3"
          placeholder="Optional note for municipal review history."
        />
      </label>

      <div class="audit-suggestion-card__actions">
        <AppButton
          :disabled="isReviewing || suggestion.status === 'converted_to_report'"
          type="submit"
          variant="secondary"
        >
          {{ isReviewing ? 'Saving review...' : 'Save review' }}
        </AppButton>
        <AppButton
          :disabled="isConverting || suggestion.status === 'converted_to_report'"
          type="button"
          @click="$emit('convert', suggestion.id)"
        >
          {{ isConverting ? 'Converting...' : 'Convert to report' }}
        </AppButton>
      </div>
    </form>

    <AppCard v-if="suggestion.reviewer_note" variant="muted">
      <AppBadge tone="info">Reviewer note</AppBadge>
      <p>{{ suggestion.reviewer_note }}</p>
    </AppCard>

    <AppCard v-if="suggestion.converted_report_id || convertedReportId" variant="muted">
      <AppBadge tone="success">Converted report</AppBadge>
      <p>{{ suggestion.converted_report_id ?? convertedReportId }}</p>
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
import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';
import type { BadgeTone } from '@/types/ui';
import {
  categoryLabels,
  formatConfidence,
  formatCoordinates,
  formatDateTime,
} from '@/utils/reportFormatting';

const props = defineProps<{
  suggestion: AuditSuggestion;
  isReviewing?: boolean;
  isConverting?: boolean;
  reviewError?: string | null;
  convertError?: string | null;
  convertedReportId?: string | null;
}>();

const emit = defineEmits<{
  review: [suggestionId: string, payload: AuditSuggestionReviewPayload];
  convert: [suggestionId: string];
}>();

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
  if (props.suggestion.status === 'rejected') {
    return 'danger';
  }
  if (props.suggestion.status === 'needs_manual_review') {
    return 'warning';
  }
  return 'info';
});

const categoryTone = computed<BadgeTone>(
  () => `category-${props.suggestion.category.replace(/_/g, '-')}` as BadgeTone,
);
const statusLabel = computed(() => statusLabels[props.suggestion.status]);
const hasHiddenProviderUrl = computed(() => Boolean(props.suggestion.image_url));

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
  gap: var(--space-4);
}

.audit-suggestion-card h3,
.audit-suggestion-card p {
  margin: 0;
}

.audit-suggestion-card__description,
.audit-suggestion-card__evidence p,
.audit-suggestion-card__error p {
  color: var(--text-secondary);
}

.audit-suggestion-card__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 11rem), 1fr));
  gap: var(--space-3);
  margin: 0;
}

.audit-suggestion-card__grid > div {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
}

.audit-suggestion-card__evidence,
.audit-suggestion-card__error {
  display: grid;
  gap: var(--space-2);
}

.audit-suggestion-card__evidence span {
  color: var(--text-muted);
  font-size: var(--text-sm);
  font-weight: 800;
}

.audit-suggestion-card__street-view-link {
  width: fit-content;
  color: var(--source-ai-audit-text);
  font-size: var(--text-sm);
  font-weight: 900;
  text-decoration: none;
}

.audit-suggestion-card__street-view-link:hover {
  text-decoration: underline;
}

.audit-suggestion-card__review {
  display: grid;
  gap: var(--space-3);
}

.audit-suggestion-card__review label {
  display: grid;
  gap: var(--space-2);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 850;
}

select,
textarea {
  width: 100%;
  border: var(--border-strong);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  color: var(--text-primary);
  background: var(--surface-panel);
  font: inherit;
}

textarea {
  resize: vertical;
}

.audit-suggestion-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

dt {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

dd {
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--text-primary);
  font-weight: 750;
}
</style>
