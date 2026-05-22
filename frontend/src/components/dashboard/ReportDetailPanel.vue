<template>
  <AppCard class="report-detail stack" variant="command">
    <template v-if="report">
      <div class="cluster-between">
        <div>
          <p class="eyebrow">Selected Report</p>
          <h2>{{ categoryLabels[report.category] }}</h2>
        </div>
        <StatusPill :status="report.status" />
      </div>

      <div class="report-detail__badges">
        <IssueCategoryBadge :category="report.category" />
        <ReportSourceBadge :source="report.source" />
      </div>

      <dl class="report-detail__grid">
        <div>
          <dt>Tracking ID</dt>
          <dd>{{ report.id }}</dd>
        </div>
        <div>
          <dt>Coordinates</dt>
          <dd>{{ formatCoordinates(report.latitude, report.longitude) }}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{{ formatDateTime(report.created_at) }}</dd>
        </div>
        <div>
          <dt>AI confidence</dt>
          <dd>{{ formatConfidence(report.confidence) }}</dd>
        </div>
        <div class="report-detail__wide">
          <dt>Description</dt>
          <dd>{{ report.description || 'No description provided.' }}</dd>
        </div>
      </dl>

      <DepartmentSuggestion :category="report.category" />

      <AppCard variant="inset" class="stack">
        <div class="cluster-between">
          <AppBadge tone="neutral">Read-only workflow</AppBadge>
          <span class="muted">Status mutation requires backend PATCH support</span>
        </div>
        <ReportWorkflowTimeline :current-status="report.status" />
      </AppCard>
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
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import IssueCategoryBadge from '@/components/reports/IssueCategoryBadge.vue';
import ReportWorkflowTimeline from '@/components/reports/ReportWorkflowTimeline.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import DepartmentSuggestion from './DepartmentSuggestion.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type { ReportSummary } from '@/types/report';
import {
  categoryLabels,
  formatConfidence,
  formatCoordinates,
  formatDateTime,
} from '@/utils/reportFormatting';

defineProps<{
  report: ReportSummary | null;
}>();
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

