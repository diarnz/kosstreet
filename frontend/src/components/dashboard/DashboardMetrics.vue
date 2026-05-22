<template>
  <section class="dashboard-metrics" aria-label="Dashboard metrics">
    <MetricCard label="Total" :value="String(metrics.total)" tone="info" />
    <MetricCard label="New" :value="String(metrics.new)" tone="neutral" />
    <MetricCard label="In progress" :value="String(metrics.inProgress)" tone="warning" />
    <MetricCard label="Resolved" :value="String(metrics.resolved)" tone="success" />
    <MetricCard label="Citizen" :value="String(metrics.citizen)" tone="success" />
    <MetricCard label="AI audit" :value="String(metrics.streetAudit)" tone="ai" />
  </section>
</template>

<script setup lang="ts">
import MetricCard from '@/components/common/MetricCard.vue';
import type { DashboardMetrics } from '@/types/dashboard';

defineProps<{
  metrics: DashboardMetrics;
}>();
</script>

<style scoped>
.dashboard-metrics {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: var(--space-3);
}

@media (max-width: 980px) {
  .dashboard-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .dashboard-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
