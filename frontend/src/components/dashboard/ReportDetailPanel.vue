<template>
  <section v-if="displayReport" class="report-detail">
    <header class="report-detail__header">
      <div>
        <h2>{{ categoryLabels[displayReport.category] }}</h2>
        <p class="report-detail__id">{{ displayReport.id }}</p>
      </div>
      <StatusPill :status="displayReport.status" />
    </header>

    <div class="report-detail__chips">
      <ReportSourceBadge :source="displayReport.source" />
      <IssueCategoryBadge :category="displayReport.category" />
      <AppBadge v-if="isDemoData" tone="warning">Demo</AppBadge>
      <span class="report-detail__chip">{{ formatCoordinates(displayReport.latitude, displayReport.longitude) }}</span>
      <span class="report-detail__chip">{{ formatDateTime(displayReport.created_at) }}</span>
      <DepartmentSuggestion :category="displayReport.category" />
    </div>

    <p v-if="displayReport.description" class="report-detail__description">
      {{ displayReport.description }}
    </p>

    <p v-if="reportDetail?.resolution_note" class="report-detail__note">
      <strong>Resolution:</strong> {{ reportDetail.resolution_note }}
    </p>
    <p v-if="reportDetail?.rejection_reason" class="report-detail__note report-detail__note--danger">
      <strong>Rejected:</strong> {{ reportDetail.rejection_reason }}
    </p>

    <AppLoading v-if="isDetailLoading" label="Loading detail" />

    <p v-if="detailError" class="report-detail__error">
      {{ detailError }}
      <AppButton size="sm" variant="secondary" @click="$emit('retry-detail')">Retry</AppButton>
    </p>

    <ReportWorkflowTimeline compact :current-status="displayReport.status" />

    <ReportStatusActions
      :allowed-statuses="allowedNextStatuses"
      :current-status="displayReport.status"
      :error="statusUpdateError"
      :is-demo-data="isDemoData"
      :is-updating="isUpdatingStatus"
      @update="$emit('update-status', $event)"
    />
  </section>

  <AppEmptyState
    v-else
    tone="dashboard"
    title="Select a report"
    description="Pick one from the queue to inspect and update."
  />
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import IssueCategoryBadge from '@/components/reports/IssueCategoryBadge.vue';
import ReportStatusActions from '@/components/reports/ReportStatusActions.vue';
import ReportWorkflowTimeline from '@/components/reports/ReportWorkflowTimeline.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import DepartmentSuggestion from './DepartmentSuggestion.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type { ReportDetail, ReportStatusUpdatePayload, ReportSummary, TicketStatus } from '@/types/report';
import { categoryLabels, formatCoordinates, formatDateTime } from '@/utils/reportFormatting';
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
.report-detail {
  display: grid;
  gap: var(--space-4);
}

.report-detail__header {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: flex-start;
  justify-content: space-between;
}

.report-detail h2 {
  margin: 0;
  font-size: clamp(1.35rem, 2.5vw, 1.75rem);
  letter-spacing: -0.03em;
}

.report-detail__id {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 800;
  letter-spacing: 0.04em;
  word-break: break-all;
}

.report-detail__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.report-detail__chip {
  padding: 0.35rem 0.65rem;
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  background: rgba(23, 33, 26, 0.05);
  font-size: var(--text-xs);
  font-weight: 750;
}

.report-detail__description,
.report-detail__note {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.report-detail__note--danger {
  color: var(--color-repair-red);
}

.report-detail__error {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  margin: 0;
  color: var(--color-repair-red);
  font-size: var(--text-sm);
  font-weight: 750;
}
</style>
