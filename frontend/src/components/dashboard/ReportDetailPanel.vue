<template>
  <section v-if="displayReport" class="report-detail" :class="`report-detail--${displayReport.status}`">
    <!-- Left status accent bar -->
    <span class="report-detail__accent" aria-hidden="true" />

    <!-- ── Header ── -->
    <header class="report-detail__head">
      <div class="report-detail__head-left">
        <p class="report-detail__eyebrow">Inspector</p>
        <h2 class="report-detail__title">{{ categoryLabels[displayReport.category] }}</h2>
        <div class="report-detail__meta">
          <ReportSourceBadge :source="displayReport.source" />
          <IssueCategoryBadge :category="displayReport.category" />
          <DepartmentSuggestion :category="displayReport.category" />
          <AppBadge v-if="isDemoData" tone="warning" size="xs">Demo</AppBadge>
        </div>
      </div>
      <div class="report-detail__head-right">
        <StatusPill :status="displayReport.status" />
        <time class="report-detail__date">{{ formatDateTime(displayReport.created_at) }}</time>
      </div>
    </header>

    <!-- ── Description ── -->
    <p v-if="displayReport.description" class="report-detail__description">
      {{ displayReport.description }}
    </p>

    <!-- ── Resolution / rejection ── -->
    <div v-if="reportDetail?.resolution_note || reportDetail?.rejection_reason" class="report-detail__note"
      :class="{ 'report-detail__note--danger': reportDetail?.rejection_reason }">
      <span class="report-detail__note-label">{{ reportDetail?.rejection_reason ? 'Rejected' : 'Resolution' }}</span>
      <p>{{ reportDetail?.rejection_reason ?? reportDetail?.resolution_note }}</p>
    </div>

    <!-- ── Loading / error ── -->
    <AppLoading v-if="isDetailLoading" label="Loading detail" />
    <div v-if="detailError" class="report-detail__error">
      <span>{{ detailError }}</span>
      <button type="button" class="report-detail__retry" @click="$emit('retry-detail')">Retry</button>
    </div>

    <!-- ── Progress track ── -->
    <ReportWorkflowTimeline compact :current-status="displayReport.status" />

    <!-- ── Status actions ── -->
    <ReportStatusActions
      :allowed-statuses="allowedNextStatuses"
      :current-status="displayReport.status"
      :error="statusUpdateError"
      :is-demo-data="isDemoData"
      :is-updating="isUpdatingStatus"
      @update="$emit('update-status', $event)"
    />
  </section>

  <div v-else class="report-detail-empty">
    <div class="report-detail-empty__icon" aria-hidden="true">
      <svg viewBox="0 0 32 32" fill="none">
        <rect x="4" y="4" width="24" height="24" rx="4" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 2" />
        <path d="M11 16h10M16 11v10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
      </svg>
    </div>
    <p class="report-detail-empty__title">Select a report</p>
    <p class="report-detail-empty__sub">Pick one from the inbox to inspect</p>
  </div>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import IssueCategoryBadge from '@/components/reports/IssueCategoryBadge.vue';
import ReportStatusActions from '@/components/reports/ReportStatusActions.vue';
import ReportWorkflowTimeline from '@/components/reports/ReportWorkflowTimeline.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import DepartmentSuggestion from './DepartmentSuggestion.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type { ReportDetail, ReportStatusUpdatePayload, ReportSummary, TicketStatus } from '@/types/report';
import { categoryLabels, formatDateTime } from '@/utils/reportFormatting';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    report: ReportSummary | null;
    reportDetail?: ReportDetail | null;
    isDetailLoading?: boolean;
    detailError?: string | null;
    allowedNextStatuses?: TicketStatus[];
    isUpdatingStatus?: boolean;
    statusUpdateError?: string | null;
    isDemoData?: boolean;
  }>(),
  {
    reportDetail: null,
    isDetailLoading: false,
    detailError: null,
    allowedNextStatuses: () => [],
    isUpdatingStatus: false,
    statusUpdateError: null,
    isDemoData: false,
  },
);

defineEmits<{
  'update-status': [payload: ReportStatusUpdatePayload];
  'retry-detail': [];
}>();

const displayReport = computed(() => props.reportDetail ?? props.report);
</script>

<style scoped>
/* ─── Root ─── */
.report-detail {
  position: relative;
  display: grid;
  gap: var(--space-4);
  padding-left: var(--space-3);
}

/* Status accent bar */
.report-detail__accent {
  position: absolute;
  left: 0;
  top: 0.25rem;
  bottom: 0.25rem;
  width: 3px;
  border-radius: 999px;
  background: rgba(23, 33, 26, 0.15);
  transition: background var(--motion-base) ease, box-shadow var(--motion-base) ease;
}

.report-detail--new        .report-detail__accent { background: var(--color-road-graphite); }
.report-detail--verified   .report-detail__accent { background: var(--color-resolved-blue);  box-shadow: 0 0 8px rgba(63, 110, 140, 0.4); }
.report-detail--assigned   .report-detail__accent { background: var(--color-municipal-green); box-shadow: 0 0 8px rgba(47, 93, 80, 0.4); }
.report-detail--in_progress .report-detail__accent { background: var(--color-amber-signal);  box-shadow: 0 0 8px rgba(217, 144, 47, 0.4); }
.report-detail--resolved   .report-detail__accent { background: #245143;                     box-shadow: 0 0 8px rgba(36, 81, 67, 0.4); }
.report-detail--rejected   .report-detail__accent { background: var(--color-repair-red);     box-shadow: 0 0 8px rgba(200, 76, 58, 0.4); }

/* ─── Header ─── */
.report-detail__head {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  justify-content: space-between;
}

.report-detail__head-left {
  display: grid;
  gap: 0.3rem;
  min-width: 0;
}

.report-detail__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.report-detail__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 2.8vw, 2rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1.1;
  color: var(--text-primary);
}

.report-detail__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}

.report-detail__head-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.4rem;
  flex-shrink: 0;
}

.report-detail__date {
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 750;
  white-space: nowrap;
}

/* ─── Description ─── */
.report-detail__description {
  margin: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(23, 33, 26, 0.04);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.6;
  border-left: 2px solid rgba(23, 33, 26, 0.1);
}

/* ─── Note ─── */
.report-detail__note {
  display: grid;
  gap: 0.25rem;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(36, 81, 67, 0.07);
  border: 1px solid rgba(36, 81, 67, 0.15);
}

.report-detail__note--danger {
  background: rgba(200, 76, 58, 0.06);
  border-color: rgba(200, 76, 58, 0.18);
}

.report-detail__note-label {
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.report-detail__note--danger .report-detail__note-label {
  color: var(--color-repair-red);
}

.report-detail__note p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

/* ─── Error ─── */
.report-detail__error {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(200, 76, 58, 0.06);
  color: var(--color-repair-red);
  font-size: var(--text-sm);
  font-weight: 750;
}

.report-detail__retry {
  padding: 0.25rem 0.65rem;
  border: 1px solid rgba(200, 76, 58, 0.3);
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--color-repair-red);
  font-size: 0.72rem;
  font-weight: 850;
  cursor: pointer;
  transition: background var(--motion-fast) ease;
}

.report-detail__retry:hover {
  background: rgba(200, 76, 58, 0.1);
}

/* ─── Override workflow timeline (compact) ─── */
:deep(.workflow-timeline--compact) {
  display: flex;
  flex-wrap: nowrap;
  gap: 0;
  align-items: center;
  overflow-x: auto;
  padding: var(--space-3) var(--space-3);
  border-radius: var(--radius-lg);
  background: rgba(23, 33, 26, 0.04);
  scrollbar-width: none;
}

:deep(.workflow-timeline--compact)::-webkit-scrollbar {
  display: none;
}

:deep(.workflow-timeline--compact .workflow-timeline__item) {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 0 0.6rem;
  flex: 1;
  min-width: 0;
  opacity: 0.35;
  transform: none;
  transition: opacity var(--motion-fast) ease;
}

:deep(.workflow-timeline--compact .workflow-timeline__item::before) {
  content: '';
  position: absolute;
  top: 0.6rem;
  left: 50%;
  right: -50%;
  height: 1px;
  background: rgba(23, 33, 26, 0.15);
  z-index: 0;
}

:deep(.workflow-timeline--compact .workflow-timeline__item:last-child::before) {
  display: none;
}

:deep(.workflow-timeline--compact .workflow-timeline__item--done) {
  opacity: 0.65;
}

:deep(.workflow-timeline--compact .workflow-timeline__item--current) {
  opacity: 1;
  transform: none;
}

/* ─── Override status actions: kill AppCard box ─── */
:deep(.app-card.status-actions),
:deep(.app-card--inset.status-actions) {
  padding: 0 !important;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
}

:deep(.status-actions .cluster-between) {
  display: none;
}

:deep(.status-actions .muted) {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin: 0 0 var(--space-1);
}

:deep(.status-actions__form) {
  display: grid;
  gap: var(--space-3);
}

:deep(.status-actions fieldset) {
  padding: 0;
  border: 0;
  margin: 0;
  display: grid;
  gap: var(--space-2);
  min-width: 0;
}

:deep(.status-actions legend) {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: var(--space-2);
  float: none;
  width: 100%;
  padding: 0;
}

:deep(.status-actions__options) {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

:deep(.status-actions__option) {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 2rem;
  padding: 0 0.9rem;
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.55);
  cursor: pointer;
  font-size: var(--text-xs);
  transition:
    border-color var(--motion-fast) ease,
    background var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

:deep(.status-actions__option:hover) {
  border-color: rgba(47, 93, 80, 0.25);
  background: rgba(255, 253, 247, 0.9);
}

:deep(.status-actions__option--selected) {
  border-color: rgba(47, 93, 80, 0.4);
  background: rgba(221, 232, 213, 0.65);
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.12);
}

:deep(.status-actions__option input[type="radio"]) {
  display: none;
}

:deep(.status-actions__error.app-card) {
  padding: var(--space-3) !important;
  border-radius: var(--radius-md) !important;
  background: rgba(200, 76, 58, 0.06) !important;
  border: 1px solid rgba(200, 76, 58, 0.18) !important;
}

:deep(.status-actions__error p) {
  margin: 0.3rem 0 0;
  font-size: var(--text-xs);
  color: var(--color-repair-red);
}

/* ─── Empty state ─── */
.report-detail-empty {
  display: grid;
  place-items: center;
  gap: var(--space-2);
  padding: var(--space-8) var(--space-4);
  text-align: center;
}

.report-detail-empty__icon {
  display: grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: rgba(23, 33, 26, 0.05);
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.report-detail-empty__icon svg {
  width: 1.4rem;
  height: 1.4rem;
}

.report-detail-empty__title {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 850;
  color: var(--text-secondary);
}

.report-detail-empty__sub {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--text-muted);
}
</style>
