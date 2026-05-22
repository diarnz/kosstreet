<template>
  <CitizenLayout>
    <AppSectionHeader
      eyebrow="Report submitted"
      title="Track your municipal report."
      description="Keep this tracking ID. KoStreet checks the report-detail endpoint for live workflow status when it is available."
    />

    <AppCard class="status-card stack" variant="command">
      <div class="cluster-between">
        <div>
          <p class="eyebrow">Tracking ID</p>
          <h2>{{ reportId }}</h2>
        </div>
        <StatusPill v-if="reportDetail" :status="reportDetail.status" />
        <AppBadge v-else tone="warning">Detail pending</AppBadge>
      </div>
      <AppBadge v-if="isDemoDetail" tone="warning">Pitch Mode demo record</AppBadge>
      <p v-if="reportDetail">
        {{
          isDemoDetail
            ? 'This tracking page is showing a prepared demo report for judging reliability.'
            : 'This tracking page is showing the current backend status for your report.'
        }}
      </p>
      <p v-else>
        Your report was submitted. Live detail appears here after
        <code>GET /api/v1/reports/:id</code> is connected by the backend.
      </p>
    </AppCard>

    <AppCard v-if="isLoading" class="stack" variant="inset">
      <AppLoading label="Loading report detail" />
    </AppCard>

    <AppCard v-if="error" class="status-error stack" variant="muted">
      <AppBadge tone="warning">Tracking endpoint pending</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" @click="fetchReportDetail">Retry tracking lookup</AppButton>
    </AppCard>

    <AppCard v-if="reportDetail" class="stack" variant="inset">
      <div class="status-detail-grid">
        <div>
          <dt>Category</dt>
          <dd>{{ categoryLabels[reportDetail.category] }}</dd>
        </div>
        <div>
          <dt>Source</dt>
          <dd>{{ sourceLabels[reportDetail.source] }}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{{ formatDateTime(reportDetail.created_at) }}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>{{ formatDateTime(reportDetail.updated_at) }}</dd>
        </div>
        <div>
          <dt>Coordinates</dt>
          <dd>{{ formatCoordinates(reportDetail.latitude, reportDetail.longitude) }}</dd>
        </div>
        <div v-if="reportDetail.resolution_note">
          <dt>Resolution note</dt>
          <dd>{{ reportDetail.resolution_note }}</dd>
        </div>
        <div v-if="reportDetail.rejection_reason">
          <dt>Rejection reason</dt>
          <dd>{{ reportDetail.rejection_reason }}</dd>
        </div>
      </div>
    </AppCard>

    <AppCard class="stack" variant="inset">
      <div>
        <h2>What happens next</h2>
        <p>The municipality reviews, verifies, assigns, works on, and resolves reports.</p>
      </div>
      <ReportWorkflowTimeline :current-status="reportDetail?.status ?? 'new'" />
    </AppCard>

    <ReportWorkflowHistory v-if="reportDetail" :events="reportDetail.workflow_events" />

    <div class="cluster">
      <RouterLink class="status-link status-link--primary" to="/report">Create another report</RouterLink>
      <RouterLink class="status-link" to="/dashboard">Open dashboard</RouterLink>
    </div>
  </CitizenLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import ReportWorkflowHistory from '@/components/reports/ReportWorkflowHistory.vue';
import ReportWorkflowTimeline from '@/components/reports/ReportWorkflowTimeline.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import { getReport } from '@/api/reports';
import { findDemoReport } from '@/demo/demoReports';
import CitizenLayout from '@/layouts/CitizenLayout.vue';
import { useUiStore } from '@/stores/ui';
import type { ReportDetail } from '@/types/report';
import {
  categoryLabels,
  formatCoordinates,
  formatDateTime,
  sourceLabels,
} from '@/utils/reportFormatting';

const route = useRoute();
const uiStore = useUiStore();
const reportId = computed(() => String(route.params.id ?? 'Unknown'));
const reportDetail = ref<ReportDetail | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const isDemoDetail = ref(false);

onMounted(() => {
  void fetchReportDetail();
});

async function fetchReportDetail() {
  isLoading.value = true;
  error.value = null;

  try {
    reportDetail.value = await getReport(reportId.value);
    isDemoDetail.value = false;
  } catch (unknownError) {
    const demoReport = uiStore.demoMode ? findDemoReport(reportId.value) : null;

    if (demoReport) {
      reportDetail.value = demoReport;
      isDemoDetail.value = true;
      error.value = null;
      isLoading.value = false;
      return;
    }

    reportDetail.value = null;
    isDemoDetail.value = false;
    error.value =
      unknownError instanceof Error
        ? unknownError.message
        : 'Report detail endpoint is not connected yet. Keep the tracking ID and retry later.';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.status-card h2 {
  max-width: 100%;
  margin: 0;
  overflow-wrap: anywhere;
  font-size: clamp(1.3rem, 5vw, 2rem);
}

.status-card p,
section p,
.status-error p {
  color: var(--text-secondary);
}

.status-card code {
  color: var(--text-primary);
  font-weight: 850;
}

.status-error {
  display: grid;
  gap: var(--space-3);
}

.status-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.status-detail-grid > div {
  display: grid;
  gap: var(--space-2);
  min-width: 0;
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.58);
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

.status-link {
  display: inline-flex;
  align-items: center;
  min-height: 3rem;
  padding: 0 var(--space-5);
  border: var(--border-strong);
  border-radius: var(--radius-pill);
  font-weight: 850;
}

.status-link--primary {
  color: var(--text-inverse);
  background: var(--action-primary);
  border-color: transparent;
}

@media (max-width: 620px) {
  .status-detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
