<template>
  <div class="dashboard-metrics" aria-label="Dashboard metrics">
    <div class="dashboard-metrics__stat">
      <span class="dashboard-metrics__value">{{ metrics.total }}</span>
      <span class="dashboard-metrics__label">Total</span>
    </div>
    <span class="dashboard-metrics__sep" aria-hidden="true" />
    <div class="dashboard-metrics__stat">
      <span class="dashboard-metrics__value">{{ metrics.new }}</span>
      <span class="dashboard-metrics__label">New</span>
    </div>
    <span class="dashboard-metrics__sep" aria-hidden="true" />
    <div class="dashboard-metrics__stat dashboard-metrics__stat--warning">
      <span class="dashboard-metrics__value">{{ metrics.inProgress }}</span>
      <span class="dashboard-metrics__label">In progress</span>
    </div>
    <span class="dashboard-metrics__sep" aria-hidden="true" />
    <div class="dashboard-metrics__stat dashboard-metrics__stat--success">
      <span class="dashboard-metrics__value">{{ metrics.resolved }}</span>
      <span class="dashboard-metrics__label">Resolved</span>
    </div>
    <span class="dashboard-metrics__sep" aria-hidden="true" />
    <div class="dashboard-metrics__stat dashboard-metrics__stat--citizen">
      <span class="dashboard-metrics__value">{{ metrics.citizen }}</span>
      <span class="dashboard-metrics__label">Citizen</span>
    </div>
    <span class="dashboard-metrics__sep" aria-hidden="true" />
    <div class="dashboard-metrics__stat dashboard-metrics__stat--ai">
      <span class="dashboard-metrics__value">{{ metrics.streetAudit }}</span>
      <span class="dashboard-metrics__label">AI Audit</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DashboardMetrics } from '@/types/dashboard';

defineProps<{
  metrics: DashboardMetrics;
}>();
</script>

<style scoped>
.dashboard-metrics {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.62);
  backdrop-filter: blur(14px);
  overflow-x: auto;
  width: fit-content;
  scrollbar-width: none;
}

.dashboard-metrics::-webkit-scrollbar {
  display: none;
}

.dashboard-metrics__stat {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
  flex-shrink: 0;
}

.dashboard-metrics__value {
  font-size: 1.25rem;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1;
}

.dashboard-metrics__label {
  font-size: var(--text-xs);
  font-weight: 800;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.dashboard-metrics__stat--warning .dashboard-metrics__value {
  color: var(--color-amber-signal);
}

.dashboard-metrics__stat--success .dashboard-metrics__value {
  color: var(--color-municipal-green);
}

.dashboard-metrics__stat--citizen .dashboard-metrics__value {
  color: var(--color-resolved-blue);
}

.dashboard-metrics__stat--ai .dashboard-metrics__value {
  color: var(--color-sidewalk-blue);
}

.dashboard-metrics__sep {
  width: 1px;
  height: 1.25rem;
  background: rgba(23, 33, 26, 0.12);
  flex-shrink: 0;
}
</style>
