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

    <ReportMap
      :is-loading="reportsStore.isLoading"
      :reports="reportsStore.filteredReports"
      :selected-report-id="reportsStore.selectedReportId"
      @select="reportsStore.selectReport"
    />

    <section class="dashboard-workspace">
      <ReportQueue
        :is-loading="reportsStore.isLoading"
        :reports="reportsStore.filteredReports"
        :selected-report-id="reportsStore.selectedReportId"
        @select="reportsStore.selectReport"
      />

      <ReportDetailPanel :report="reportsStore.selectedReport" />
    </section>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import DashboardFilters from '@/components/dashboard/DashboardFilters.vue';
import DashboardMetrics from '@/components/dashboard/DashboardMetrics.vue';
import ReportDetailPanel from '@/components/dashboard/ReportDetailPanel.vue';
import ReportQueue from '@/components/dashboard/ReportQueue.vue';
import ReportMap from '@/components/maps/ReportMap.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useReportsStore } from '@/stores/reports';
import { formatDateTime } from '@/utils/reportFormatting';

const reportsStore = useReportsStore();

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
