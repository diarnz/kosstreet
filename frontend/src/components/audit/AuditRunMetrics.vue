<template>
  <section class="audit-metrics" aria-label="Audit run metrics">
    <MetricCard label="Total" :value="String(metrics.total)" tone="ai" />
    <MetricCard label="Queued" :value="String(metrics.queued)" tone="neutral" />
    <MetricCard label="Running" :value="String(metrics.running)" tone="warning" />
    <MetricCard label="Completed" :value="String(metrics.completed)" tone="success" />
    <MetricCard label="Failed" :value="String(metrics.failed)" tone="neutral" />
  </section>
</template>

<script setup lang="ts">
import MetricCard from '@/components/common/MetricCard.vue';
import type { AuditRunMetrics } from '@/types/audit';

defineProps<{
  metrics: AuditRunMetrics;
}>();
</script>

<style scoped>
.audit-metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--space-3);
}

@media (max-width: 860px) {
  .audit-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .audit-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
