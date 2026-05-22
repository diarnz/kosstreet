<template>
  <section class="dashboard-metrics" aria-label="Dashboard metrics">
    <MetricCard label="Total reports" :value="String(metrics.total)" description="All fetched reports." tone="info" />
    <MetricCard label="New" :value="String(metrics.new)" description="Waiting for review." tone="neutral" />
    <MetricCard
      label="In progress"
      :value="String(metrics.inProgress)"
      description="Currently being handled."
      tone="warning"
    />
    <MetricCard label="Resolved" :value="String(metrics.resolved)" description="Completed reports." tone="success" />
    <MetricCard label="Citizen" :value="String(metrics.citizen)" description="Submitted by citizens." tone="success" />
    <MetricCard
      label="AI Street Audit"
      :value="String(metrics.streetAudit)"
      description="AI-suggested reports."
      tone="ai"
    />
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
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 12rem), 1fr));
  gap: var(--space-4);
}
</style>

