<template>
  <AppCard class="report-queue stack" variant="command">
    <div class="cluster-between">
      <div>
        <h2>Report queue</h2>
        <p>{{ reports.length }} report{{ reports.length === 1 ? '' : 's' }} in current view.</p>
      </div>
      <AppLoading v-if="isLoading" label="Loading reports" />
    </div>

    <AppEmptyState
      v-if="!isLoading && reports.length === 0"
      tone="dashboard"
      title="No reports in this view"
      description="Create a real citizen report or clear filters to see available reports."
    />

    <div v-else class="report-queue__list" role="list">
      <button
        v-for="report in reports"
        :key="report.id"
        class="report-queue__item"
        :class="{ 'report-queue__item--selected': report.id === selectedReportId }"
        type="button"
        role="listitem"
        @click="$emit('select', report.id)"
      >
        <span class="report-queue__topline">
          <IssueCategoryBadge :category="report.category" />
          <StatusPill :status="report.status" />
          <ReportSourceBadge :source="report.source" />
        </span>
        <strong>{{ categoryLabels[report.category] }}</strong>
        <span class="report-queue__meta">
          {{ formatCoordinates(report.latitude, report.longitude) }} ·
          {{ formatDateTime(report.created_at) }}
        </span>
        <span v-if="report.description" class="report-queue__description">
          {{ report.description }}
        </span>
      </button>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import IssueCategoryBadge from '@/components/reports/IssueCategoryBadge.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type { ReportSummary } from '@/types/report';
import { categoryLabels, formatCoordinates, formatDateTime } from '@/utils/reportFormatting';

defineProps<{
  reports: ReportSummary[];
  selectedReportId: string | null;
  isLoading: boolean;
}>();

defineEmits<{
  select: [reportId: string];
}>();
</script>

<style scoped>
.report-queue h2 {
  margin: 0 0 var(--space-2);
}

.report-queue p {
  color: var(--text-secondary);
}

.report-queue__list {
  display: grid;
  gap: var(--space-3);
  max-height: 42rem;
  overflow: auto;
  padding-right: var(--space-1);
}

.report-queue__item {
  display: grid;
  gap: var(--space-3);
  width: 100%;
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.68);
  text-align: left;
}

.report-queue__item--selected {
  border-color: rgba(47, 93, 80, 0.42);
  background: rgba(221, 232, 213, 0.56);
  box-shadow: var(--shadow-card);
}

.report-queue__topline {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.report-queue__meta,
.report-queue__description {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>

