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
        :class="[`report-queue__item--${report.status}`, { 'report-queue__item--selected': report.id === selectedReportId }]"
        type="button"
        role="listitem"
        :aria-pressed="report.id === selectedReportId"
        :aria-label="`Select ${categoryLabels[report.category]} report`"
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
import { categoryLabels, formatRelativeTime } from '@/utils/reportFormatting';

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
  max-height: 42rem;
  overflow: auto;
  padding-right: 2px;
  scrollbar-width: thin;
  scrollbar-color: rgba(47, 93, 80, 0.15) transparent;
}

/* ─── Queue item ─── */
.report-queue__item {
  position: relative;
  display: grid;
  gap: 0.3rem;
  width: 100%;
  padding: 0.7rem 0.75rem 0.7rem 1rem;
  overflow: hidden;
  border: none;
  border-bottom: 1px solid rgba(23, 33, 26, 0.06);
  border-radius: 0;
  color: inherit;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition:
    background var(--motion-fast) ease,
    padding-left var(--motion-fast) var(--ease-out-expo);
}

.report-queue__item:first-child {
  border-top: 1px solid rgba(23, 33, 26, 0.06);
}

.report-queue__item:hover {
  background: rgba(47, 93, 80, 0.04);
  padding-left: 1.2rem;
}

.report-queue__item--selected {
  background: rgba(47, 93, 80, 0.07);
  padding-left: 1.2rem;
}

/* ─── Accent bar (status color) ─── */
.report-queue__accent {
  position: absolute;
  inset: 8px auto 8px 0;
  width: 3px;
  border-radius: 999px;
  background: rgba(23, 33, 26, 0.12);
  transition: background var(--motion-fast) ease, box-shadow var(--motion-fast) ease;
}

.report-queue__item--new        .report-queue__accent { background: var(--color-road-graphite); }
.report-queue__item--verified   .report-queue__accent { background: var(--color-resolved-blue); }
.report-queue__item--assigned   .report-queue__accent { background: var(--color-municipal-green); }
.report-queue__item--in_progress .report-queue__accent { background: var(--color-amber-signal); }
.report-queue__item--resolved   .report-queue__accent { background: #245143; }
.report-queue__item--rejected   .report-queue__accent { background: var(--color-repair-red); }

/* Brighten accent on selection */
.report-queue__item--selected.report-queue__item--new        .report-queue__accent { box-shadow: 0 0 6px rgba(58, 63, 59, 0.35); }
.report-queue__item--selected.report-queue__item--verified   .report-queue__accent { box-shadow: 0 0 6px rgba(63, 110, 140, 0.45); }
.report-queue__item--selected.report-queue__item--assigned   .report-queue__accent { box-shadow: 0 0 6px rgba(47, 93, 80, 0.45); }
.report-queue__item--selected.report-queue__item--in_progress .report-queue__accent { box-shadow: 0 0 6px rgba(217, 144, 47, 0.45); }
.report-queue__item--selected.report-queue__item--resolved   .report-queue__accent { box-shadow: 0 0 6px rgba(36, 81, 67, 0.45); }
.report-queue__item--selected.report-queue__item--rejected   .report-queue__accent { box-shadow: 0 0 6px rgba(200, 76, 58, 0.45); }

/* ─── Content ─── */
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
  color: var(--text-primary);
}

.report-queue__time {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.66rem;
  font-weight: 750;
}

.report-queue__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.28rem;
}

.report-queue__description {
  margin: 0;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}
</style>
