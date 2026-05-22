<template>
  <section class="report-queue">
    <div class="report-queue__head">
      <span class="report-queue__count">{{ reports.length }}</span>
    </div>

    <AppLoading v-if="isLoading" label="Loading" />

    <AppEmptyState
      v-else-if="reports.length === 0"
      tone="dashboard"
      title="No reports"
      description="Clear filters or create a new report."
    />

    <div v-else class="report-queue__list" role="list">
      <button
        v-for="report in reports"
        :key="report.id"
        class="report-queue__item"
        :class="{ 'report-queue__item--selected': report.id === selectedReportId }"
        type="button"
        role="listitem"
        :aria-pressed="report.id === selectedReportId"
        :aria-label="`Select ${categoryLabels[report.category]} report ${report.id}`"
        @click="$emit('select', report.id)"
      >
        <span class="report-queue__accent" aria-hidden="true" />
        <div class="report-queue__row">
          <strong class="report-queue__title">{{ categoryLabels[report.category] }}</strong>
          <span class="report-queue__time">{{ formatRelativeTime(report.created_at) }}</span>
        </div>
        <div class="report-queue__tags">
          <StatusPill :status="report.status" />
          <ReportSourceBadge compact :source="report.source" />
          <AppBadge v-if="isDemoData" tone="warning" size="xs">Demo</AppBadge>
        </div>
        <p class="report-queue__meta">
          {{ formatCoordinates(report.latitude, report.longitude) }}
        </p>
        <p v-if="report.description" class="report-queue__description">
          {{ report.description }}
        </p>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type { ReportSummary } from '@/types/report';
import { categoryLabels, formatCoordinates, formatRelativeTime } from '@/utils/reportFormatting';

defineProps<{
  reports: ReportSummary[];
  selectedReportId: string | null;
  isLoading: boolean;
  isDemoData?: boolean;
}>();

defineEmits<{
  select: [reportId: string];
}>();
</script>

<style scoped>
.report-queue {
  display: grid;
  gap: var(--space-2);
}

.report-queue__head {
  display: flex;
  justify-content: flex-end;
}

.report-queue__count {
  display: grid;
  place-items: center;
  min-width: 1.75rem;
  height: 1.75rem;
  padding: 0 0.45rem;
  border-radius: var(--radius-pill);
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.1);
  font-size: 0.72rem;
  font-weight: 900;
}

.report-queue__list {
  display: grid;
  gap: 0.45rem;
  max-height: 42rem;
  overflow: auto;
  padding-right: var(--space-1);
}

.report-queue__item {
  position: relative;
  display: grid;
  gap: 0.35rem;
  width: 100%;
  padding: 0.65rem 0.75rem 0.65rem 0.85rem;
  overflow: hidden;
  border: 1px solid rgba(23, 33, 26, 0.07);
  border-radius: var(--radius-md);
  color: inherit;
  background: rgba(255, 253, 247, 0.42);
  text-align: left;
  transition:
    border-color var(--motion-fast) ease,
    background var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

.report-queue__accent {
  position: absolute;
  inset: 0 auto 0 0;
  width: 2px;
  background: transparent;
  transition: background var(--motion-fast) ease;
}

.report-queue__item:hover {
  border-color: rgba(47, 93, 80, 0.18);
  background: rgba(255, 253, 247, 0.72);
}

.report-queue__item--selected {
  border-color: rgba(47, 93, 80, 0.32);
  background: rgba(221, 232, 213, 0.42);
  box-shadow: 0 8px 24px rgba(47, 93, 80, 0.1);
}

.report-queue__item--selected .report-queue__accent {
  background: var(--color-municipal-green);
}

.report-queue__row {
  display: flex;
  gap: var(--space-2);
  align-items: baseline;
  justify-content: space-between;
}

.report-queue__title {
  font-size: 0.88rem;
  font-weight: 850;
  letter-spacing: -0.01em;
}

.report-queue__time {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 750;
}

.report-queue__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.report-queue__meta {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 650;
  letter-spacing: 0.01em;
}

.report-queue__description {
  margin: 0;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>
