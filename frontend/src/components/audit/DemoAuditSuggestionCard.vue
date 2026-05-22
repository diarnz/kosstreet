<template>
  <AppCard class="demo-suggestion-card" variant="inset">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Demo AI suggestion</p>
        <h3>{{ categoryLabels[suggestion.category] }}</h3>
      </div>
      <AppBadge tone="warning">Demo scenario</AppBadge>
    </div>

    <p>{{ suggestion.description }}</p>

    <dl class="demo-suggestion-card__grid">
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
        <dt>Status</dt>
        <dd>{{ suggestion.status.replace(/_/g, ' ') }}</dd>
      </div>
    </dl>

    <AppCard class="demo-suggestion-card__evidence" variant="muted">
      <AppBadge tone="source-ai-audit">No restricted image shown</AppBadge>
      <p>
        {{ suggestion.explanation }}
      </p>
    </AppCard>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import type { AuditSuggestion } from '@/types/detection';
import {
  categoryLabels,
  formatConfidence,
  formatCoordinates,
} from '@/utils/reportFormatting';

defineProps<{
  suggestion: AuditSuggestion;
}>();
</script>

<style scoped>
.demo-suggestion-card {
  display: grid;
  gap: var(--space-4);
}

.demo-suggestion-card h3,
.demo-suggestion-card p {
  margin: 0;
}

.demo-suggestion-card p {
  color: var(--text-secondary);
}

.demo-suggestion-card__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin: 0;
}

.demo-suggestion-card__grid > div {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
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
  text-transform: capitalize;
}

.demo-suggestion-card__evidence {
  display: grid;
  gap: var(--space-2);
}

@media (max-width: 620px) {
  .demo-suggestion-card__grid {
    grid-template-columns: 1fr;
  }
}
</style>
