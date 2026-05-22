<template>
  <AppCard class="report-detail stack" variant="command">
    <template v-if="displayReport">
      <div class="cluster-between">
        <div>
          <p class="eyebrow">Selected Report</p>
          <h2>{{ categoryLabels[displayReport.category] }}</h2>
        </div>
        <StatusPill :status="displayReport.status" />
      </div>

      <div class="report-detail__badges">
        <IssueCategoryBadge :category="displayReport.category" />
        <ReportSourceBadge :source="displayReport.source" />
        <AppBadge v-if="isDemoData" tone="warning">Demo record</AppBadge>
      </div>

      <dl class="report-detail__grid">
        <div>
          <dt>Tracking ID</dt>
          <dd>{{ displayReport.id }}</dd>
        </div>
        <div>
          <dt>Coordinates</dt>
          <dd>{{ formatCoordinates(displayReport.latitude, displayReport.longitude) }}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{{ formatDateTime(displayReport.created_at) }}</dd>
        </div>
        <div>
          <dt>AI confidence</dt>
          <dd>{{ formatConfidence(displayReport.confidence) }}</dd>
        </div>
        <div v-if="reportDetail">
          <dt>Updated</dt>
          <dd>{{ formatDateTime(reportDetail.updated_at) }}</dd>
        </div>
        <div class="report-detail__wide">
          <dt>Description</dt>
          <dd>{{ displayReport.description || 'No description provided.' }}</dd>
        </div>
        <div v-if="reportDetail?.resolution_note" class="report-detail__wide">
          <dt>Resolution note</dt>
          <dd>{{ reportDetail.resolution_note }}</dd>
        </div>
        <div v-if="reportDetail?.rejection_reason" class="report-detail__wide">
          <dt>Rejection reason</dt>
          <dd>{{ reportDetail.rejection_reason }}</dd>
        </div>
      </dl>

      <DepartmentSuggestion :category="displayReport.category" />

      <AppCard v-if="isDetailLoading" variant="inset">
        <AppLoading label="Loading workflow detail" />
      </AppCard>

      <AppCard v-if="detailError" class="report-detail__notice" variant="muted">
        <div class="cluster-between">
          <AppBadge tone="warning">Detail endpoint pending</AppBadge>
          <AppButton size="sm" variant="secondary" @click="$emit('retry-detail')">Retry detail</AppButton>
        </div>
        <p>{{ detailError }}</p>
      </AppCard>

      <AppCard variant="inset" class="stack">
        <div class="cluster-between">
          <AppBadge tone="neutral">Workflow status</AppBadge>
          <span class="muted">Status changes require backend confirmation</span>
        </div>
        <ReportWorkflowTimeline :current-status="displayReport.status" />
      </AppCard>

      <ReportStatusActions
        :allowed-statuses="allowedNextStatuses"
        :current-status="displayReport.status"
        :error="statusUpdateError"
        :is-demo-data="isDemoData"
        :is-updating="isUpdatingStatus"
        @update="$emit('update-status', $event)"
      />

      <ReportWorkflowHistory :events="reportDetail?.workflow_events ?? []" />
    </template>

    <AppEmptyState
      v-else
      tone="dashboard"
      title="Select a report"
      description="Choose a report from the queue to inspect its details, source, location, and suggested municipal department."
    />
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import IssueCategoryBadge from '@/components/reports/IssueCategoryBadge.vue';
import ReportStatusActions from '@/components/reports/ReportStatusActions.vue';
import ReportWorkflowHistory from '@/components/reports/ReportWorkflowHistory.vue';
import ReportWorkflowTimeline from '@/components/reports/ReportWorkflowTimeline.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import DepartmentSuggestion from './DepartmentSuggestion.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type { ReportDetail, ReportStatusUpdatePayload, ReportSummary, TicketStatus } from '@/types/report';
import {
  categoryLabels,
  formatConfidence,
  formatCoordinates,
  formatDateTime,
} from '@/utils/reportFormatting';
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
.report-detail h2 {
  margin: 0;
  font-size: clamp(1.6rem, 4vw, 2.4rem);
}

.report-detail__badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.report-detail__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin: 0;
}

.report-detail__notice {
  display: grid;
  gap: var(--space-3);
}

.report-detail__notice p {
  margin: 0;
  color: var(--text-secondary);
}

.report-detail__grid > div {
  display: grid;
  gap: var(--space-2);
  min-width: 0;
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.58);
}

.report-detail__wide {
  grid-column: 1 / -1;
}

dt {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

dd {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--text-primary);
  font-weight: 750;
}

@media (max-width: 620px) {
  .report-detail__grid {
    grid-template-columns: 1fr;
  }
}
</style>

