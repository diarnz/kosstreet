<template>
  <AppCard class="suggestion-unavailable stack" variant="inset">
    <div class="cluster-between">
      <AppBadge tone="source-ai-audit">AI suggestion review</AppBadge>
      <span class="muted">Backend endpoint required</span>
    </div>

    <div>
      <h3>Suggestion review activates after real AI results are exposed.</h3>
      <p>
        This area will render detections only after
        <code>GET /api/v1/audit-runs/:id/suggestions</code> returns model-produced results.
      </p>
    </div>

    <dl class="suggestion-unavailable__fields">
      <div v-for="field in fields" :key="field.label">
        <dt>{{ field.label }}</dt>
        <dd>{{ field.description }}</dd>
      </div>
    </dl>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';

const fields = [
  { label: 'Category', description: 'Pothole, garbage, broken light, sidewalk issue, sign, or other.' },
  { label: 'Confidence', description: 'Model confidence returned by the AI pipeline.' },
  { label: 'Location', description: 'Latitude and longitude for the reviewed street-level frame.' },
  { label: 'Evidence', description: 'Legally usable image URL, attribution, explanation, and optional bounding box.' },
  { label: 'Review', description: 'Human accept, reject, or manual-review decision persisted by backend.' },
];
</script>

<style scoped>
.suggestion-unavailable h3,
.suggestion-unavailable p {
  margin: 0;
}

.suggestion-unavailable p {
  color: var(--text-secondary);
}

code {
  color: var(--source-ai-audit-text);
  font-weight: 800;
}

.suggestion-unavailable__fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr));
  gap: var(--space-3);
  margin: 0;
}

.suggestion-unavailable__fields > div {
  display: grid;
  gap: var(--space-2);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: rgba(255, 253, 247, 0.62);
}

dt {
  color: var(--text-primary);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

dd {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>
