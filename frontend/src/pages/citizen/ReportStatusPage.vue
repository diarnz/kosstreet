<template>
  <CitizenLayout>
    <PageHero
      align="center"
      eyebrow="Tracking"
      title="Report status"
      description="Follow your submission through municipal review."
      gradient
    />

    <GlassPanel class="status-card animate-scale-in" elevated padding="lg">
      <div class="cluster-between">
        <div>
          <p class="command-label">Tracking ID</p>
          <h2>{{ reportId }}</h2>
        </div>
        <StatusPill v-if="reportDetail" :status="reportDetail.status" />
        <AppBadge v-else tone="warning">Pending</AppBadge>
      </div>
      <AppBadge v-if="isDemoDetail" tone="warning">Demo record</AppBadge>
    </GlassPanel>

    <GlassPanel v-if="isLoading" padding="lg" class="animate-fade-in">
      <AppLoading label="Loading report" />
    </GlassPanel>

    <GlassPanel v-if="error" padding="lg" class="status-error animate-fade-in">
      <AppBadge tone="warning">Unavailable</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" @click="fetchReportDetail">Retry</AppButton>
    </GlassPanel>

    <GlassPanel v-if="reportDetail" padding="lg" class="animate-fade-in">
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
          <dt>Location</dt>
          <dd>{{ formatCoordinates(reportDetail.latitude, reportDetail.longitude) }}</dd>
        </div>
        <div v-if="reportDetail.resolution_note">
          <dt>Resolution</dt>
          <dd>{{ reportDetail.resolution_note }}</dd>
        </div>
        <div v-if="reportDetail.rejection_reason">
          <dt>Rejection</dt>
          <dd>{{ reportDetail.rejection_reason }}</dd>
        </div>
      </div>
    </GlassPanel>

    <GlassPanel padding="lg" class="animate-fade-in">
      <p class="command-label">Workflow</p>
      <ReportWorkflowTimeline :current-status="reportDetail?.status ?? 'new'" />
    </GlassPanel>

    <ReportWorkflowHistory v-if="reportDetail" :events="reportDetail.workflow_events" />

    <div class="cluster status-actions animate-fade-in">
      <RouterLink class="status-link status-link--primary" to="/report">New report</RouterLink>
      <RouterLink class="status-link" to="/dashboard">Dashboard</RouterLink>
    </div>
  </CitizenLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import GlassPanel from '@/components/common/GlassPanel.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import PageHero from '@/components/common/PageHero.vue';
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
      unknownError instanceof Error ? unknownError.message : 'Could not load report details.';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.status-card h2 {
  max-width: 100%;
  margin: 0.15rem 0 0;
  overflow-wrap: anywhere;
  font-family: var(--font-display);
  font-size: clamp(1.3rem, 5vw, 2rem);
  letter-spacing: -0.03em;
}

.status-error {
  display: grid;
  gap: var(--space-3);
}

.status-error p {
  color: var(--text-secondary);
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
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.45);
  transition: transform var(--motion-fast) var(--ease-out-expo);
}

.status-detail-grid > div:hover {
  transform: translateY(-2px);
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

.status-actions {
  padding-top: var(--space-2);
}

.status-link {
  display: inline-flex;
  align-items: center;
  min-height: 3rem;
  padding: 0 var(--space-5);
  border: var(--border-strong);
  border-radius: var(--radius-pill);
  font-weight: 850;
  transition: transform var(--motion-fast) var(--ease-out-expo), box-shadow var(--motion-fast) ease;
}

.status-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(23, 33, 26, 0.1);
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
