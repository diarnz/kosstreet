<template>
  <section class="grid-auto" aria-label="Audit run metrics">
    <MetricCard
      label="Total runs"
      :value="String(metrics.total)"
      description="Real backend audit runs."
      tone="ai"
    />
    <MetricCard
      label="Queued"
      :value="String(metrics.queued)"
      description="Waiting for orchestration."
      tone="neutral"
    />
    <MetricCard
      label="Running"
      :value="String(metrics.running)"
      description="Backend/AI processing."
      tone="warning"
    />
    <MetricCard
      label="Completed"
      :value="String(metrics.completed)"
      description="Backend marked complete."
      tone="success"
    />
    <MetricCard
      label="Failed"
      :value="String(metrics.failed)"
      description="Needs backend review."
      tone="neutral"
    />
  </section>
</template>

<script setup lang="ts">
import MetricCard from '@/components/common/MetricCard.vue';
import type { AuditRunMetrics } from '@/types/audit';

defineProps<{
  metrics: AuditRunMetrics;
}>();
</script>
