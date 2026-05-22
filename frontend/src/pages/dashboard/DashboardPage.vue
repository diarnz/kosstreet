<template>
  <DashboardLayout>
    <div class="cluster-between">
      <AppSectionHeader
        eyebrow="Municipality Dashboard"
        title="Prishtina issue command center"
        description="The municipal operating surface for real report triage, source separation, department suggestions, and workflow visibility."
      />
      <div class="dashboard-actions">
        <AppBadge v-if="reportsStore.lastFetchedAt" tone="info">
          Fetched {{ formatDateTime(reportsStore.lastFetchedAt) }}
        </AppBadge>
        <AppButton :disabled="reportsStore.isLoading" variant="secondary" @click="reportsStore.fetchReports">
          {{ reportsStore.isLoading ? 'Refreshing...' : 'Refresh reports' }}
        </AppButton>
      </div>
    </div>

    <PitchModeBanner
      v-if="reportsStore.usingDemoReports"
      data-mode="demo"
      message="Prepared demo reports are shown because live backend reports are empty or unavailable."
    />

    <AppCard v-if="reportsStore.error" class="dashboard-error" variant="inset">
      <AppBadge tone="danger">Backend error</AppBadge>
      <p>{{ reportsStore.error }}</p>
      <AppButton variant="secondary" @click="reportsStore.fetchReports">Retry fetch</AppButton>
    </AppCard>

    <DashboardMetrics :metrics="reportsStore.metrics" />

    <DashboardFilters
      :filters="reportsStore.filters"
      @clear="reportsStore.clearFilters"
      @update:category="reportsStore.setCategory"
      @update:search="reportsStore.setSearch"
      @update:source="reportsStore.setSource"
      @update:status="reportsStore.setStatus"
    />

    <StreetViewPanel
      :is-loading="reportsStore.isLoading"
      :record-count="reportsStore.filteredReports.length"
      :target="selectedStreetViewTarget"
    />

    <section class="dashboard-workspace">
      <ReportQueue
        :is-demo-data="reportsStore.usingDemoReports"
        :is-loading="reportsStore.isLoading"
        :reports="reportsStore.filteredReports"
        :selected-report-id="reportsStore.selectedReportId"
        @select="reportsStore.selectReport"
      />

      <ReportDetailPanel
        :allowed-next-statuses="reportsStore.allowedNextStatuses"
        :detail-error="reportsStore.selectedDetailError"
        :is-detail-loading="reportsStore.selectedDetailIsLoading"
        :is-updating-status="reportsStore.isUpdatingStatus"
        :is-demo-data="reportsStore.usingDemoReports"
        :report="reportsStore.selectedReport"
        :report-detail="reportsStore.selectedReportDetail"
        :status-update-error="reportsStore.statusUpdateError"
        @retry-detail="fetchSelectedReportDetail"
        @update-status="reportsStore.updateSelectedReportStatus"
      />
    </section>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import PitchModeBanner from '@/components/common/PitchModeBanner.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import DashboardFilters from '@/components/dashboard/DashboardFilters.vue';
import DashboardMetrics from '@/components/dashboard/DashboardMetrics.vue';
import ReportDetailPanel from '@/components/dashboard/ReportDetailPanel.vue';
import ReportQueue from '@/components/dashboard/ReportQueue.vue';
import StreetViewPanel from '@/components/streetview/StreetViewPanel.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useReportsStore } from '@/stores/reports';
import { formatDateTime } from '@/utils/reportFormatting';
import { hasValidCoordinates, reportToStreetViewTarget } from '@/utils/streetView';

const reportsStore = useReportsStore();

const selectedStreetViewTarget = computed(() => {
  const selectedReport = reportsStore.selectedReport;
  if (selectedReport && hasValidCoordinates(selectedReport)) {
    return reportToStreetViewTarget(selectedReport);
  }

  const firstMappableReport = reportsStore.mappableFilteredReports[0];
  return firstMappableReport ? reportToStreetViewTarget(firstMappableReport) : null;
});

onMounted(() => {
  void reportsStore.fetchReports();
});

watch(
  () => reportsStore.filteredReports,
  (reports) => {
    if (!reports.some((report) => report.id === reportsStore.selectedReportId)) {
      reportsStore.selectReport(reports[0]?.id ?? null);
    }
  },
  { immediate: true },
);

watch(
  () => reportsStore.selectedReportId,
  (reportId) => {
    if (reportId) {
      void reportsStore.fetchReportDetail(reportId);
    }
  },
  { immediate: true },
);

function fetchSelectedReportDetail() {
  if (reportsStore.selectedReportId) {
    void reportsStore.fetchReportDetail(reportsStore.selectedReportId);
  }
}
</script>

<style scoped>
.dashboard-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  justify-content: flex-end;
}

.dashboard-error {
  display: grid;
  gap: var(--space-3);
}

.dashboard-error p,
p {
  color: var(--text-secondary);
}

.dashboard-workspace {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(22rem, 1.05fr);
  gap: var(--space-5);
  align-items: start;
}

@media (max-width: 980px) {
  .dashboard-workspace {
    grid-template-columns: 1fr;
  }
}
</style>
