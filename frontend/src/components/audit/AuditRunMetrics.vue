<template>
  <div class="audit-metrics" aria-label="Audit run metrics">
    <div class="audit-metrics__stat">
      <span class="audit-metrics__value">{{ metrics.total }}</span>
      <span class="audit-metrics__label">Total</span>
    </div>
    <span class="audit-metrics__sep" aria-hidden="true" />
    <div class="audit-metrics__stat">
      <span class="audit-metrics__value">{{ metrics.queued }}</span>
      <span class="audit-metrics__label">Queued</span>
    </div>
    <span class="audit-metrics__sep" aria-hidden="true" />
    <div class="audit-metrics__stat audit-metrics__stat--running">
      <span class="audit-metrics__value">{{ metrics.running }}</span>
      <span class="audit-metrics__label">Running</span>
    </div>
    <span class="audit-metrics__sep" aria-hidden="true" />
    <div class="audit-metrics__stat audit-metrics__stat--success">
      <span class="audit-metrics__value">{{ metrics.completed }}</span>
      <span class="audit-metrics__label">Completed</span>
    </div>
    <span class="audit-metrics__sep" aria-hidden="true" />
    <div class="audit-metrics__stat">
      <span class="audit-metrics__value">{{ metrics.failed }}</span>
      <span class="audit-metrics__label">Failed</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AuditRunMetrics } from '@/types/audit';

defineProps<{
  metrics: AuditRunMetrics;
}>();
</script>

<style scoped>
.audit-metrics {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.62);
  overflow-x: auto;
  width: fit-content;
}

.audit-metrics__stat {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
  flex-shrink: 0;
}

.audit-metrics__value {
  font-size: 1.25rem;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1;
}

.audit-metrics__label {
  font-size: var(--text-xs);
  font-weight: 800;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.audit-metrics__stat--running .audit-metrics__value {
  color: var(--color-amber-signal);
}

.audit-metrics__stat--success .audit-metrics__value {
  color: var(--color-municipal-green);
}

.audit-metrics__sep {
  width: 1px;
  height: 1.25rem;
  background: rgba(23, 33, 26, 0.12);
  flex-shrink: 0;
}
</style>
