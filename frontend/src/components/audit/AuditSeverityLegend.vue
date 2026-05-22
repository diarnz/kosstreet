<template>
  <div class="severity-legend" aria-label="Severity legend">
    <span class="severity-legend__label">Severity</span>
    <ul class="severity-legend__items">
      <li v-for="item in items" :key="item.key">
        <span class="severity-legend__swatch" :style="{ background: item.color }" aria-hidden="true" />
        {{ item.label }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { SEVERITY_COLORS, SEVERITY_LABELS } from '@/utils/detectionRegions';

const items = [
  { key: 'low', label: SEVERITY_LABELS.low, color: SEVERITY_COLORS.low },
  { key: 'medium', label: SEVERITY_LABELS.medium, color: SEVERITY_COLORS.medium },
  { key: 'high', label: SEVERITY_LABELS.high, color: SEVERITY_COLORS.high },
  { key: 'critical', label: SEVERITY_LABELS.critical, color: SEVERITY_COLORS.critical },
];
</script>

<style scoped>
.severity-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2) var(--space-3);
  padding: var(--space-2) var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.72);
}

.severity-legend__label {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.severity-legend__items {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
}

.severity-legend__items li {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 750;
}

.severity-legend__swatch {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: var(--radius-pill);
  box-shadow: inset 0 0 0 1px rgba(23, 33, 26, 0.12);
}
</style>
