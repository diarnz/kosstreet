<template>
  <section class="report-review">
    <div class="report-review__panel">
      <div v-if="draft.imagePreviewUrl" class="report-review__photo">
        <img :src="draft.imagePreviewUrl" alt="Issue photo preview" />
      </div>
      <div v-else class="report-review__photo report-review__photo--empty" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="4" y="5" width="16" height="14" rx="2" stroke="currentColor" stroke-width="1.6" />
          <circle cx="9" cy="10" r="1.4" fill="currentColor" />
          <path d="M4 16l4.5-4.5 3 3L14 12l6 6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
        </svg>
      </div>

      <div class="report-review__body">
        <div class="report-review__tags">
          <IssueCategoryBadge v-if="resolvedCategory" :category="resolvedCategory" />
          <AppBadge v-else tone="warning" size="xs">Detecting…</AppBadge>
          <AppBadge v-if="confidenceLabel" tone="source-ai-audit" size="xs">{{ confidenceLabel }}</AppBadge>
          <AppBadge v-if="severityLabel" :tone="severityTone" size="xs">{{ severityLabel }}</AppBadge>
        </div>

        <p class="report-review__location">
          {{ locationLine }}
        </p>

        <p v-if="aiDescription" class="report-review__hint">
          {{ aiDescription }}
        </p>
      </div>
    </div>

    <label class="report-review__note">
      <span class="report-review__note-label">Note <span class="muted">(optional)</span></span>
      <AppTextarea
        :model-value="description"
        :maxlength="maxDescriptionLength"
        aria-label="Optional issue note"
        placeholder="Anything else staff should know…"
        @update:model-value="$emit('update:description', $event)"
      />
      <span class="report-review__count muted">{{ description.length }}/{{ maxDescriptionLength }}</span>
    </label>

    <p v-if="draft.isAnalyzingImage" class="report-review__status">AI is still analyzing your photo…</p>
    <p v-else-if="!canSubmit" class="report-review__status report-review__status--warn">
      Add a location to submit.
    </p>
    <p v-if="error" class="report-review__error">{{ error }}</p>

    <AppButton
      class="report-review__submit"
      :disabled="!canSubmit || isSubmitting || draft.isAnalyzingImage"
      size="lg"
      @click="$emit('submit')"
    >
      {{ isSubmitting ? 'Submitting…' : 'Submit report' }}
    </AppButton>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppTextarea from '@/components/common/AppTextarea.vue';
import IssueCategoryBadge from './IssueCategoryBadge.vue';
import type { ReportDraft } from '@/types/reportDraft';
import type { BadgeTone } from '@/types/ui';
import { categoryLabels, formatConfidence, formatCoordinates } from '@/utils/reportFormatting';
import { SEVERITY_LABELS } from '@/utils/detectionRegions';

const props = withDefaults(
  defineProps<{
    draft: ReportDraft;
    description: string;
    canSubmit: boolean;
    isSubmitting: boolean;
    error: string | null;
    maxDescriptionLength?: number;
  }>(),
  {
    maxDescriptionLength: 1000,
  },
);

defineEmits<{
  submit: [];
  'update:description': [value: string];
}>();

const resolvedCategory = computed(
  () => props.draft.imageAnalysis?.category ?? props.draft.category,
);

const confidenceLabel = computed(() => {
  const confidence = props.draft.imageAnalysis?.confidence;
  return confidence == null ? null : `AI ${formatConfidence(confidence)}`;
});

const severityLabel = computed(() => {
  const severity = props.draft.imageAnalysis?.severity;
  return severity ? SEVERITY_LABELS[severity] : null;
});

const severityTone = computed((): BadgeTone => {
  const severity = props.draft.imageAnalysis?.severity;
  if (severity === 'high' || severity === 'critical') return 'danger';
  if (severity === 'medium') return 'warning';
  return 'success';
});

const locationLine = computed(() => {
  if (props.draft.latitude === null || props.draft.longitude === null) {
    return 'Location required';
  }
  return props.draft.locationLabel || formatCoordinates(props.draft.latitude, props.draft.longitude);
});

const aiDescription = computed(() => {
  const analysis = props.draft.imageAnalysis;
  if (!analysis?.category) {
    return null;
  }
  if (analysis.description?.trim()) {
    return analysis.description.trim();
  }
  return `AI classified this as ${categoryLabels[analysis.category]}.`;
});
</script>

<style scoped>
.report-review {
  display: grid;
  gap: var(--space-4);
}

.report-review__panel {
  display: grid;
  grid-template-columns: 5.5rem minmax(0, 1fr);
  gap: var(--space-3);
  align-items: start;
  padding: var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-lg);
  background: rgba(255, 253, 247, 0.5);
}

.report-review__photo {
  width: 5.5rem;
  height: 5.5rem;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--surface-muted);
  box-shadow: 0 4px 14px rgba(23, 33, 26, 0.08);
}

.report-review__photo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.report-review__photo--empty {
  display: grid;
  place-items: center;
  color: var(--text-muted);
}

.report-review__photo--empty svg {
  width: 1.6rem;
  height: 1.6rem;
}

.report-review__body {
  display: grid;
  gap: 0.45rem;
  min-width: 0;
}

.report-review__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}

.report-review__location {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 800;
  letter-spacing: -0.01em;
}

.report-review__hint {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  line-height: 1.45;
}

.report-review__note {
  display: grid;
  gap: 0.35rem;
}

.report-review__note-label {
  font-size: var(--text-xs);
  font-weight: 800;
  color: var(--text-secondary);
}

.report-review__count {
  justify-self: end;
  font-size: 0.65rem;
  font-weight: 700;
}

.report-review__status {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 700;
}

.report-review__status--warn {
  color: var(--color-amber-signal);
}

.report-review__error {
  margin: 0;
  color: var(--color-repair-red);
  font-size: var(--text-sm);
  font-weight: 750;
}

.report-review__submit {
  width: 100%;
}

@media (max-width: 640px) {
  .report-review {
    gap: var(--space-3);
  }

  .report-review__panel {
    grid-template-columns: 4.5rem minmax(0, 1fr);
    gap: var(--space-2);
    padding: var(--space-2);
  }

  .report-review__photo {
    width: 4.5rem;
    height: 4.5rem;
  }

  .report-review__location {
    font-size: var(--text-xs);
  }

  .report-review__submit {
    min-height: 2.75rem;
  }
}
</style>
