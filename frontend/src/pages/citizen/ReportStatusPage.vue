<template>
  <CitizenLayout>
    <div class="status-page">
      <GlassPanel v-if="isLoading" padding="lg" class="status-page__panel animate-fade-in">
        <AppLoading label="Loading your report" />
      </GlassPanel>

      <GlassPanel v-else-if="error" padding="lg" class="status-page__panel status-error animate-fade-in">
        <div class="status-hero status-hero--error">
          <div class="status-hero__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8" />
              <path d="M12 8v5M12 16h.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </div>
          <h1>Could not load report</h1>
          <p>{{ error }}</p>
        </div>
        <AppButton class="status-page__retry" variant="secondary" @click="fetchReportDetail">
          Try again
        </AppButton>
      </GlassPanel>

      <div v-else-if="reportDetail" class="status-page__stack animate-scale-in">
        <header class="status-hero" :class="`status-hero--${reportDetail.status}`">
          <div class="status-hero__icon" aria-hidden="true">
            <svg v-if="reportDetail.status === 'rejected'" viewBox="0 0 24 24" fill="none">
              <path d="M8 8l8 8M16 8l-8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
            <svg v-else-if="reportDetail.status === 'resolved'" viewBox="0 0 24 24" fill="none">
              <path
                d="M7 12.5l3 3 7-7.5"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none">
              <path
                d="M7 12.5l3 3 7-7.5"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
          <p class="status-hero__eyebrow">Report confirmed</p>
          <h1>{{ pageTitle }}</h1>
          <p class="status-hero__message">{{ statusMessage }}</p>
          <div class="status-hero__tags">
            <IssueCategoryBadge :category="reportDetail.category" />
            <StatusPill :status="reportDetail.status" />
            <AppBadge v-if="isDemoDetail" tone="warning" size="xs">Demo</AppBadge>
          </div>
        </header>

        <GlassPanel padding="lg" class="status-page__panel status-card" elevated>
          <div v-if="imageUrl" class="status-card__photo">
            <img :src="imageUrl" alt="Report photo" />
          </div>

          <dl class="status-card__facts">
            <div class="status-card__fact">
              <dt>Location</dt>
              <dd>{{ formatCoordinates(reportDetail.latitude, reportDetail.longitude) }}</dd>
            </div>
            <div class="status-card__fact">
              <dt>Submitted</dt>
              <dd>
                {{ formatDateTime(reportDetail.created_at) }}
                <span class="muted">{{ formatRelativeTime(reportDetail.created_at) }}</span>
              </dd>
            </div>
          </dl>

          <div class="status-card__progress">
            <WorkflowDots :current-status="reportDetail.status" />
            <span class="status-card__progress-label">{{ statusLabels[reportDetail.status] }}</span>
          </div>

          <p v-if="reportDetail.description?.trim()" class="status-card__note">
            {{ reportDetail.description }}
          </p>

          <p v-if="reportDetail.resolution_note" class="status-card__update status-card__update--resolved">
            <strong>Resolved:</strong> {{ reportDetail.resolution_note }}
          </p>

          <p v-if="reportDetail.rejection_reason" class="status-card__update status-card__update--rejected">
            <strong>Not accepted:</strong> {{ reportDetail.rejection_reason }}
          </p>

          <div class="status-card__actions">
            <RouterLink class="status-card__action status-card__action--primary" to="/report">
              New report
            </RouterLink>
            <RouterLink class="status-card__action" to="/dashboard">Dashboard</RouterLink>
          </div>
        </GlassPanel>
      </div>
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
import IssueCategoryBadge from '@/components/reports/IssueCategoryBadge.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import WorkflowDots from '@/components/reports/WorkflowDots.vue';
import { getReport } from '@/api/reports';
import { findDemoReport } from '@/demo/demoReports';
import CitizenLayout from '@/layouts/CitizenLayout.vue';
import { useUiStore } from '@/stores/ui';
import type { ReportDetail, TicketStatus } from '@/types/report';
import { resolveApiAssetUrl } from '@/utils/apiAssets';
import {
  formatCoordinates,
  formatDateTime,
  formatRelativeTime,
  statusLabels,
} from '@/utils/reportFormatting';

const route = useRoute();
const uiStore = useUiStore();
const reportId = computed(() => String(route.params.id ?? ''));
const reportDetail = ref<ReportDetail | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const isDemoDetail = ref(false);

const pageTitles: Record<TicketStatus, string> = {
  new: 'Report received',
  verified: 'Report verified',
  assigned: 'Crew assigned',
  in_progress: 'Work in progress',
  resolved: 'Issue resolved',
  rejected: 'Report declined',
};

const statusMessages: Record<TicketStatus, string> = {
  new: 'Your submission is in the municipal queue.',
  verified: 'Staff confirmed your report is valid.',
  assigned: 'A crew has been assigned to handle it.',
  in_progress: 'Repair work is underway.',
  resolved: 'This issue has been marked resolved.',
  rejected: 'This report was not accepted.',
};

const imageUrl = computed(() => {
  const url = reportDetail.value?.image_url;
  return url ? resolveApiAssetUrl(url) : null;
});

const pageTitle = computed(() => {
  if (!reportDetail.value) return '';
  return pageTitles[reportDetail.value.status];
});

const statusMessage = computed(() => {
  if (!reportDetail.value) return '';
  return statusMessages[reportDetail.value.status];
});

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
.status-page {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: calc(100dvh - clamp(6rem, 14vw, 9rem));
  padding-block: var(--space-4);
}

.status-page__stack {
  display: grid;
  gap: var(--space-4);
  width: 100%;
  max-width: 26rem;
  margin-inline: auto;
}

.status-page__panel {
  width: 100%;
  max-width: 26rem;
  margin-inline: auto;
}

.status-hero {
  display: grid;
  gap: 0.45rem;
  justify-items: center;
  text-align: center;
}

.status-hero__eyebrow {
  margin: 0;
  color: var(--color-municipal-green);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.status-hero--rejected .status-hero__eyebrow {
  color: var(--color-repair-red);
}

.status-hero--in_progress .status-hero__eyebrow,
.status-hero--assigned .status-hero__eyebrow {
  color: var(--color-amber-signal);
}

.status-hero__icon {
  display: grid;
  place-items: center;
  width: 3.75rem;
  height: 3.75rem;
  margin-bottom: 0.15rem;
  border-radius: 50%;
  color: var(--color-municipal-green);
  background: color-mix(in srgb, var(--color-municipal-green) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-municipal-green) 28%, transparent);
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-municipal-green) 8%, transparent);
}

.status-hero__icon svg {
  width: 1.55rem;
  height: 1.55rem;
}

.status-hero--rejected .status-hero__icon {
  color: var(--color-repair-red);
  background: color-mix(in srgb, var(--color-repair-red) 12%, transparent);
  border-color: color-mix(in srgb, var(--color-repair-red) 26%, transparent);
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-repair-red) 7%, transparent);
}

.status-hero--in_progress .status-hero__icon,
.status-hero--assigned .status-hero__icon {
  color: var(--color-amber-signal);
  background: color-mix(in srgb, var(--color-amber-signal) 12%, transparent);
  border-color: color-mix(in srgb, var(--color-amber-signal) 26%, transparent);
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-amber-signal) 7%, transparent);
}

.status-hero h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.55rem, 5vw, 2rem);
  line-height: 1.1;
  letter-spacing: -0.03em;
  text-wrap: balance;
}

.status-hero__message {
  max-width: 22rem;
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.status-hero__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  justify-content: center;
  padding-top: 0.2rem;
}

.status-hero--error .status-hero__icon {
  color: var(--color-amber-signal);
  background: color-mix(in srgb, var(--color-amber-signal) 12%, transparent);
  border-color: color-mix(in srgb, var(--color-amber-signal) 26%, transparent);
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-amber-signal) 7%, transparent);
}

.status-card {
  display: grid;
  gap: var(--space-4);
  text-align: center;
}

.status-card__photo {
  width: 7.5rem;
  height: 7.5rem;
  margin-inline: auto;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-muted);
  box-shadow: 0 8px 24px rgba(23, 33, 26, 0.12);
}

.status-card__photo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-card__facts {
  display: grid;
  gap: var(--space-3);
  margin: 0;
  padding: var(--space-3) 0 0;
  border-top: 1px solid color-mix(in srgb, var(--text-muted) 16%, transparent);
}

.status-card__fact {
  display: grid;
  gap: 0.2rem;
}

dt {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

dd {
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 750;
  line-height: 1.4;
}

dd .muted {
  display: block;
  margin-top: 0.15rem;
  font-size: var(--text-xs);
  font-weight: 650;
}

.status-card__progress {
  display: grid;
  gap: 0.45rem;
  justify-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--surface-muted) 70%, transparent);
}

.status-card__progress-label {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 800;
}

.status-card__note {
  margin: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
  text-align: left;
  background: color-mix(in srgb, var(--surface-muted) 55%, transparent);
}

.status-card__update {
  margin: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: 1.45;
  text-align: left;
}

.status-card__update strong {
  font-weight: 850;
}

.status-card__update--resolved {
  color: var(--text-secondary);
  background: color-mix(in srgb, var(--color-municipal-green) 12%, transparent);
}

.status-card__update--rejected {
  color: var(--text-secondary);
  background: color-mix(in srgb, var(--color-repair-red) 10%, transparent);
}

.status-card__actions {
  display: grid;
  gap: var(--space-2);
  padding-top: var(--space-1);
}

.status-card__action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.75rem;
  padding: 0 var(--space-4);
  border: 1px solid color-mix(in srgb, var(--text-muted) 22%, transparent);
  border-radius: var(--radius-pill);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 800;
  transition: transform var(--motion-fast) var(--ease-out-expo);
}

.status-card__action:hover {
  transform: translateY(-1px);
}

.status-card__action--primary {
  color: var(--text-inverse);
  background: var(--action-primary);
  border-color: transparent;
}

.status-error {
  display: grid;
  gap: var(--space-4);
  justify-items: center;
  text-align: center;
}

.status-page__retry {
  width: 100%;
}

@media (max-width: 640px) {
  .status-page {
    align-items: flex-start;
    justify-content: flex-start;
    min-height: calc(100dvh - clamp(5.5rem, 20vw, 8.5rem));
    padding:
      max(var(--space-2), env(safe-area-inset-top, 0px))
      max(var(--space-3), env(safe-area-inset-right, 0px))
      max(calc(clamp(5rem, 10vw, 7rem) + env(safe-area-inset-bottom, 0px)), var(--space-4))
      max(var(--space-3), env(safe-area-inset-left, 0px));
  }

  .status-page__stack,
  .status-page__panel {
    max-width: none;
    gap: var(--space-3);
  }

  .status-hero h1 {
    font-size: clamp(1.4rem, 7vw, 1.75rem);
  }

  .status-hero__message {
    padding-inline: var(--space-2);
  }

  .status-card__photo {
    width: 6.5rem;
    height: 6.5rem;
  }
}
</style>
