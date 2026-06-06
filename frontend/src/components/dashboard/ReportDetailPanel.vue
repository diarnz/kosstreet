<template>
  <section v-if="displayReport" class="report-detail" :class="`report-detail--${displayReport.status}`">
    <span class="report-detail__accent" aria-hidden="true" />

    <div class="report-detail__shell" :class="{ 'report-detail__shell--with-photo': photoEvidence }">
      <aside v-if="photoEvidence" class="report-detail__evidence" aria-label="Photo evidence">
        <AnalyzedFrameViewer
          layout="inspector"
          :image-url="photoEvidence.imageUrl"
          :regions="photoEvidence.regions"
          :severity="photoEvidence.severity"
          :category="photoEvidence.category"
          :confidence="photoEvidence.confidence"
          :latitude="photoEvidence.latitude"
          :longitude="photoEvidence.longitude"
          alt="Citizen report photo with AI detection overlay"
          aria-label="Report photo evidence"
        />
      </aside>

      <div class="report-detail__body">
        <header class="report-detail__head">
          <div class="report-detail__head-main">
            <div class="report-detail__title-row">
              <p class="report-detail__eyebrow">Inspector</p>
              <WorkflowDots :current-status="displayReport.status" />
            </div>
            <h2 class="report-detail__title">{{ categoryLabels[displayReport.category] }}</h2>
            <div class="report-detail__meta">
              <ReportSourceBadge :source="displayReport.source" />
              <IssueCategoryBadge :category="displayReport.category" />
              <DepartmentSuggestion :category="displayReport.category" />
              <span v-if="photoEvidence?.confidence != null" class="report-detail__signal">
                AI {{ formatConfidence(photoEvidence.confidence) }}
              </span>
              <AppBadge v-if="isDemoData" tone="warning" size="xs">Demo</AppBadge>
            </div>
          </div>
          <div class="report-detail__head-side">
            <StatusPill :status="displayReport.status" />
            <time class="report-detail__date">{{ formatDateTime(displayReport.created_at) }}</time>
          </div>
        </header>

        <p v-if="displayReport.description" class="report-detail__description">
          {{ displayReport.description }}
        </p>

        <div
          v-if="reportDetail?.resolution_note || reportDetail?.rejection_reason"
          class="report-detail__note"
          :class="{ 'report-detail__note--danger': reportDetail?.rejection_reason }"
        >
          <span class="report-detail__note-label">
            {{ reportDetail?.rejection_reason ? 'Rejected' : 'Resolution' }}
          </span>
          <p>{{ reportDetail?.rejection_reason ?? reportDetail?.resolution_note }}</p>
        </div>

        <AppLoading v-if="isDetailLoading" label="Loading detail" />

        <div v-if="detailError" class="report-detail__error">
          <span>{{ detailError }}</span>
          <button type="button" class="report-detail__retry" @click="$emit('retry-detail')">Retry</button>
        </div>

        <ReportStatusActions
          :allowed-statuses="allowedNextStatuses"
          :current-status="displayReport.status"
          :error="statusUpdateError"
          :is-demo-data="isDemoData"
          :is-updating="isUpdatingStatus"
          @update="$emit('update-status', $event)"
        />
      </div>
    </div>
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
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import IssueCategoryBadge from '@/components/reports/IssueCategoryBadge.vue';
import ReportStatusActions from '@/components/reports/ReportStatusActions.vue';
import WorkflowDots from '@/components/reports/WorkflowDots.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import DepartmentSuggestion from './DepartmentSuggestion.vue';
import ReportSourceBadge from './ReportSourceBadge.vue';
import type {
  ReportDetail,
  ReportDetectionRegion,
  ReportSeverity,
  ReportStatusUpdatePayload,
  ReportSummary,
  TicketStatus,
} from '@/types/report';
import type { IssueCategory } from '@/types/report';
import { categoryLabels, formatConfidence, formatDateTime } from '@/utils/reportFormatting';
import { computed } from 'vue';

export type ReportPhotoEvidence = {
  imageUrl: string;
  regions: ReportDetectionRegion[];
  severity: ReportSeverity;
  category: IssueCategory;
  confidence: number | null;
  latitude: number;
  longitude: number;
};

const props = withDefaults(
  defineProps<{
    report: ReportSummary | null;
    reportDetail?: ReportDetail | null;
    photoEvidence?: ReportPhotoEvidence | null;
    isDetailLoading?: boolean;
    detailError?: string | null;
    allowedNextStatuses?: TicketStatus[];
    isUpdatingStatus?: boolean;
    statusUpdateError?: string | null;
    isDemoData?: boolean;
  }>(),
  {
    reportDetail: null,
    photoEvidence: null,
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
  position: relative;
  padding-left: var(--space-2);
}

.report-detail__accent {
  position: absolute;
  left: 0;
  top: 0.15rem;
  bottom: 0.15rem;
  width: 3px;
  border-radius: 999px;
  background: rgba(23, 33, 26, 0.15);
  transition: background var(--motion-base) ease, box-shadow var(--motion-base) ease;
}

.report-detail--new .report-detail__accent { background: var(--color-road-graphite); }
.report-detail--verified .report-detail__accent { background: var(--color-resolved-blue); box-shadow: 0 0 8px rgba(63, 110, 140, 0.4); }
.report-detail--assigned .report-detail__accent { background: var(--color-municipal-green); box-shadow: 0 0 8px rgba(47, 93, 80, 0.4); }
.report-detail--in_progress .report-detail__accent { background: var(--color-amber-signal); box-shadow: 0 0 8px rgba(217, 144, 47, 0.4); }
.report-detail--resolved .report-detail__accent { background: #245143; box-shadow: 0 0 8px rgba(36, 81, 67, 0.4); }
.report-detail--rejected .report-detail__accent { background: var(--color-repair-red); box-shadow: 0 0 8px rgba(200, 76, 58, 0.4); }

.report-detail__shell {
  display: grid;
  gap: 0;
  min-width: 0;
}

.report-detail__shell--with-photo {
  grid-template-columns: minmax(4.8rem, 5.6rem) minmax(0, 1fr);
  gap: 0.75rem;
  align-items: stretch;
}

.report-detail__evidence {
  min-width: 0;
}

.report-detail__body {
  display: grid;
  gap: 0.55rem;
  min-width: 0;
}

.report-detail__head {
  display: flex;
  gap: 0.55rem;
  align-items: flex-start;
  justify-content: space-between;
}

.report-detail__head-main {
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.report-detail__title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.report-detail__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.report-detail__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.05rem, 2vw, 1.35rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.15;
  color: var(--text-primary);
}

.report-detail__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  align-items: center;
}

.report-detail__signal {
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-municipal-green) 14%, transparent);
  color: var(--color-municipal-green);
  font-size: 0.58rem;
  font-weight: 800;
}

.report-detail__head-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  flex-shrink: 0;
}

.report-detail__date {
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 750;
  white-space: nowrap;
}

.report-detail__description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.report-detail__note {
  display: grid;
  gap: 0.15rem;
  padding: 0.45rem 0.55rem;
  border-radius: var(--radius-md);
  background: rgba(36, 81, 67, 0.07);
  border: 1px solid rgba(36, 81, 67, 0.15);
}

.report-detail__note--danger {
  background: rgba(200, 76, 58, 0.06);
  border-color: rgba(200, 76, 58, 0.18);
}

.report-detail__note-label {
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.report-detail__note--danger .report-detail__note-label {
  color: var(--color-repair-red);
}

.report-detail__note p {
  margin: 0;
  font-size: 0.68rem;
  color: var(--text-secondary);
  line-height: 1.45;
}

.report-detail__error {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  padding: 0.45rem 0.55rem;
  border-radius: var(--radius-md);
  background: rgba(200, 76, 58, 0.06);
  color: var(--color-repair-red);
  font-size: 0.68rem;
  font-weight: 750;
}

.report-detail__retry {
  padding: 0.2rem 0.55rem;
  border: 1px solid rgba(200, 76, 58, 0.3);
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--color-repair-red);
  font-size: 0.65rem;
  font-weight: 850;
  cursor: pointer;
}

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

@media (max-width: 640px) {
  .report-detail__shell--with-photo {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .report-detail__head {
    flex-direction: column;
    gap: 0.4rem;
  }

  .report-detail__head-side {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  .report-detail__date {
    white-space: normal;
  }
}
</style>
