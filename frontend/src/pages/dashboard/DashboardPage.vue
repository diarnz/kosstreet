<template>
  <DashboardLayout>
    <header class="command-header animate-fade-up">
      <div>
        <p class="command-label">Command center</p>
        <h1>Municipal dashboard</h1>
        <p class="command-header__sub">Real-time triage across Kosovo</p>
      </div>
      <div class="command-header__actions">
        <DashboardMetrics :metrics="reportsStore.metrics" />
        <NotificationsPopover scope="dashboard" />
      </div>
    </header>

    <GlassPanel v-if="reportsStore.error" label="Error" class="animate-fade-in">
      <p class="command-error">{{ reportsStore.error }}</p>
      <AppButton variant="secondary" size="sm" @click="reportsStore.fetchReports">Retry</AppButton>
    </GlassPanel>

    <DashboardFilters
      class="page-command-bar"
      :filters="reportsStore.filters"
      @clear="reportsStore.clearFilters"
      @update:category="reportsStore.setCategory"
      @update:search="reportsStore.setSearch"
      @update:source="reportsStore.setSource"
      @update:status="reportsStore.setStatus"
    />

    <section class="command-deck animate-fade-up">
      <GlassPanel class="command-deck__queue" padding="sm">
        <ReportQueue
          :is-demo-data="reportsStore.usingDemoReports"
          :is-loading="reportsStore.isLoading"
          :reports="reportsStore.filteredReports"
          :selected-report-id="reportsStore.selectedReportId"
          @select="reportsStore.selectReport"
        />
      </GlassPanel>

      <div class="command-deck__inspector">
        <GlassPanel elevated padding="sm">
          <ReportDetailPanel
            :allowed-next-statuses="reportsStore.allowedNextStatuses"
            :detail-error="reportsStore.selectedDetailError"
            :is-detail-loading="reportsStore.selectedDetailIsLoading"
            :is-updating-status="reportsStore.isUpdatingStatus"
            :is-demo-data="reportsStore.usingDemoReports"
            :photo-evidence="selectedReportPhoto"
            :report="reportsStore.selectedReport"
            :report-detail="reportsStore.selectedReportDetail"
            :status-update-error="reportsStore.statusUpdateError"
            @retry-detail="fetchSelectedReportDetail"
            @update-status="reportsStore.updateSelectedReportStatus"
          />
        </GlassPanel>

        <GlassPanel label="Issue map" elevated padding="sm">
          <ReportsProblemMap
            :is-loading="reportsStore.isLoading"
            :reports="reportsStore.filteredReports"
            :selected-report-id="reportsStore.selectedReportId"
            @select="reportsStore.selectReport"
          />
        </GlassPanel>
      </div>
    </section>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import GlassPanel from '@/components/common/GlassPanel.vue';
import NotificationsPopover from '@/components/common/NotificationsPopover.vue';
import DashboardFilters from '@/components/dashboard/DashboardFilters.vue';
import DashboardMetrics from '@/components/dashboard/DashboardMetrics.vue';
import ReportDetailPanel from '@/components/dashboard/ReportDetailPanel.vue';
import ReportQueue from '@/components/dashboard/ReportQueue.vue';
import ReportsProblemMap from '@/components/dashboard/ReportsProblemMap.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useReportsStore } from '@/stores/reports';
import { resolveApiAssetUrl } from '@/utils/apiAssets';
import type { ReportDetectionRegion, ReportSeverity } from '@/types/report';
import type { IssueCategory } from '@/types/report';

const reportsStore = useReportsStore();

const selectedReportPhoto = computed(() => {
  const report = reportsStore.selectedReportDetail ?? reportsStore.selectedReport;
  if (!report?.image_url) {
    return null;
  }

  return {
    imageUrl: resolveApiAssetUrl(report.image_url),
    regions: (report.detection_regions ?? []) as ReportDetectionRegion[],
    severity: (report.severity ?? 'medium') as ReportSeverity,
    category: report.category as IssueCategory,
    confidence: report.confidence ?? null,
    latitude: report.latitude,
    longitude: report.longitude,
  };
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
    if (reportId) void reportsStore.fetchReportDetail(reportId);
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
.command-header {
  position: relative;
  z-index: var(--z-command-bar);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: flex-end;
  justify-content: space-between;
  min-width: 0;
  padding-bottom: var(--space-4);
  padding-left: var(--space-4);
  border-bottom: 1px solid rgba(23, 33, 26, 0.08);
}

.command-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.25rem;
  bottom: var(--space-4);
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--color-municipal-green), var(--color-resolved-blue));
  box-shadow: 0 0 10px rgba(47, 93, 80, 0.35);
}

.command-header h1 {
  margin: 0.15rem 0 0;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.5vw, 2.5rem);
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, var(--color-ink) 0%, rgba(47, 93, 80, 0.85) 100%);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.command-header__sub {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.command-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  min-width: 0;
}

.command-header__sync {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 750;
}

.command-error {
  margin: 0;
  color: var(--color-repair-red);
}

.page-command-bar {
  position: relative;
  z-index: var(--z-command-bar);
  width: 100%;
  min-width: 0;
}

.command-deck {
  position: relative;
  z-index: var(--z-deck);
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  gap: var(--space-4);
  align-items: start;
  min-height: 34rem;
}

.command-deck__queue {
  position: relative;
  z-index: 2;
  min-width: 0;
}

.command-deck__inspector {
  position: relative;
  z-index: 1;
  display: grid;
  gap: var(--space-4);
  min-width: 0;
}

@media (max-width: 1080px) {
  .command-deck {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .command-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    padding-left: var(--space-3);
    padding-bottom: var(--space-3);
  }

  .command-header h1 {
    font-size: clamp(1.45rem, 7vw, 1.85rem);
  }

  .command-header__sub {
    font-size: var(--text-xs);
  }

  .command-header__actions {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    gap: var(--space-2);
  }

  .command-header__actions :deep(.notifications-popover) {
    align-self: flex-end;
  }

  .command-deck {
    gap: var(--space-3);
    min-height: 0;
  }
}
</style>
