<template>
  <AppCard class="review-card stack" variant="command">
    <div class="cluster-between">
      <div>
        <h2>Review and submit</h2>
        <p>Confirm the structured report before sending it to the municipality workflow.</p>
      </div>
      <AppBadge :tone="canSubmit ? 'success' : 'warning'">
        {{ canSubmit ? 'Ready' : 'Needs required fields' }}
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
          <span v-if="draft.latitude !== null && draft.longitude !== null">
            {{ draft.latitude }}, {{ draft.longitude }}
          </span>
          <span v-else class="muted">Required</span>
        </dd>
      </div>
      <div>
        <dt>Photo</dt>
        <dd>
          <span v-if="draft.imageFile">{{ draft.imageFile.name }} selected locally</span>
          <span v-else class="muted">No local photo selected</span>
        </dd>
      </div>
      <div>
        <dt>AI analysis</dt>
        <dd>
          <span v-if="draft.aiSuggestion">Real AI suggestion available</span>
          <span v-else class="muted">Not connected yet</span>
        </dd>
      </div>
      <div class="review-card__wide">
        <dt>Description</dt>
        <dd>{{ draft.description || 'No description added' }}</dd>
      </div>
    </dl>

    <p v-if="error" class="review-card__error">{{ error }}</p>

    <AppButton :disabled="!canSubmit || isSubmitting" size="lg" @click="$emit('submit')">
      {{ isSubmitting ? 'Submitting report...' : 'Submit report' }}
    </AppButton>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import IssueCategoryBadge from './IssueCategoryBadge.vue';
import type { ReportDraft } from '@/types/reportDraft';

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
  margin: 0 0 var(--space-2);
}

.review-card p {
  color: var(--text-secondary);
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

