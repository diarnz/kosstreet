<template>
  <AppCard class="review-card stack-lg animate-scale-in" variant="default">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Step 4</p>
        <h2>Review and submit</h2>
      </div>
      <AppBadge :tone="canSubmit ? 'success' : 'warning'">
        {{ canSubmit ? 'Ready' : 'Incomplete' }}
      </AppBadge>
    </div>

    <dl class="review-card__details">
      <div>
        <dt>Category</dt>
        <dd>
          <IssueCategoryBadge v-if="draft.category" :category="draft.category" />
          <span v-else class="muted">Not selected</span>
        </dd>
      </div>
      <div>
        <dt>Location</dt>
        <dd>
          <template v-if="draft.latitude !== null && draft.longitude !== null">
            <span>{{ draft.locationLabel || formatCoordinates(draft.latitude, draft.longitude) }}</span>
          </template>
          <span v-else class="muted">Required</span>
        </dd>
      </div>
      <div>
        <dt>Photo</dt>
        <dd>{{ draft.imageFile ? draft.imageFile.name : 'No photo' }}</dd>
      </div>
      <div class="review-card__wide">
        <dt>Description</dt>
        <dd>{{ draft.description || '—' }}</dd>
      </div>
    </dl>

    <p v-if="error" class="review-card__error">{{ error }}</p>

    <AppButton :disabled="!canSubmit || isSubmitting" size="lg" @click="$emit('submit')">
      {{ isSubmitting ? 'Submitting…' : 'Submit report' }}
    </AppButton>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import IssueCategoryBadge from './IssueCategoryBadge.vue';
import type { ReportDraft } from '@/types/reportDraft';
import { formatCoordinates } from '@/utils/reportFormatting';

defineProps<{
  draft: ReportDraft;
  canSubmit: boolean;
  isSubmitting: boolean;
  error: string | null;
}>();

defineEmits<{
  submit: [];
}>();
</script>

<style scoped>
.review-card h2 {
  margin: 0;
}

.review-card__details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
  margin: 0;
}

.review-card__details > div {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.56);
}

.review-card__wide {
  grid-column: 1 / -1;
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
  color: var(--text-primary);
  font-weight: 750;
}

.review-card__error {
  color: var(--color-repair-red);
  font-weight: 850;
}

@media (max-width: 620px) {
  .review-card__details {
    grid-template-columns: 1fr;
  }
}
</style>
