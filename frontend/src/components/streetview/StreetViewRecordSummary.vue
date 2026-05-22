<template>
  <aside v-if="target" class="street-view-summary" aria-live="polite">
    <div>
      <p class="eyebrow">{{ sourceLabel }}</p>
      <h3>{{ target.label }}</h3>
    </div>
    <p>{{ target.description || 'No description provided.' }}</p>
    <dl>
      <div>
        <dt>Coordinates</dt>
        <dd>{{ formatCoordinates(target.latitude, target.longitude) }}</dd>
      </div>
      <div v-if="target.heading !== undefined || target.pitch !== undefined">
        <dt>AI frame POV</dt>
        <dd>Heading {{ target.heading ?? 'n/a' }}, pitch {{ target.pitch ?? 'n/a' }}</dd>
      </div>
    </dl>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { StreetViewTarget } from '@/types/streetView';
import { formatCoordinates } from '@/utils/reportFormatting';

const props = defineProps<{
  target: StreetViewTarget | null;
}>();

const sourceLabel = computed(() => {
  if (props.target?.source === 'audit_suggestion') return 'Audit evidence';
  if (props.target?.source === 'audit_run') return 'Audit scan location';
  return 'Report location';
});
</script>

<style scoped>
.street-view-summary {
  display: grid;
  gap: var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  background: rgba(255, 253, 247, 0.88);
  box-shadow: var(--shadow-card);
}

.street-view-summary h3,
.street-view-summary p {
  margin: 0;
}

.street-view-summary p:not(.eyebrow),
.street-view-summary dd {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.street-view-summary dl {
  display: grid;
  gap: var(--space-2);
  margin: 0;
}

.street-view-summary dl > div {
  display: grid;
  gap: var(--space-1);
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
}
</style>
