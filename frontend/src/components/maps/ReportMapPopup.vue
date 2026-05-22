<template>
  <aside v-if="report" class="report-map-popup" aria-live="polite">
    <div>
      <p class="eyebrow">Selected on map</p>
      <h3>{{ categoryLabels[report.category] }}</h3>
    </div>
    <p>{{ report.description || 'No description provided.' }}</p>
    <span>{{ formatCoordinates(report.latitude, report.longitude) }}</span>
  </aside>
</template>

<script setup lang="ts">
import type { ReportSummary } from '@/types/report';
import { categoryLabels, formatCoordinates } from '@/utils/reportFormatting';

defineProps<{
  report: ReportSummary | null;
}>();
</script>

<style scoped>
.report-map-popup {
  display: grid;
  gap: var(--space-2);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  background: rgba(255, 253, 247, 0.88);
  box-shadow: var(--shadow-card);
}

.report-map-popup h3,
.report-map-popup p {
  margin: 0;
}

.report-map-popup p:not(.eyebrow),
.report-map-popup span {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>
