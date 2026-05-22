<template>
  <DashboardLayout>
    <PageHero
      eyebrow="Audit run"
      :title="run?.route_name ?? 'Run detail'"
      description="Review pipeline progress and AI suggestions."
    />

    <AppCard v-if="error" class="stack animate-fade-in" variant="inset">
      <AppBadge tone="danger">Error</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" @click="loadRun">Retry</AppButton>
    </AppCard>

    <AppCard v-else-if="isLoading" class="stack" variant="inset">
      <AppLoading label="Loading audit run" />
    </AppCard>

    <AuditRunDetailPanel
      v-else-if="run"
      class="animate-fade-up"
      :convert-error-by-id="auditSuggestionsStore.convertErrorById"
      :convert-loading-by-id="auditSuggestionsStore.convertLoadingById"
      :converted-report-by-suggestion-id="auditSuggestionsStore.convertedReportBySuggestionId"
      :frames="frames"
      :frames-error="framesError"
      :frames-loading="framesLoading"
      :review-error-by-id="auditSuggestionsStore.reviewErrorById"
      :review-loading-by-id="auditSuggestionsStore.reviewLoadingById"
      :scan-path="scanPath"
      :scan-path-error="scanPathError"
      :scan-path-loading="scanPathLoading"
      :run="run"
      :suggestions="suggestions"
      :suggestions-error="suggestionsError"
      :suggestions-loading="suggestionsLoading"
      @convert-suggestion="auditSuggestionsStore.convertSuggestionToReport"
      @refresh-frames="refreshFrames"
      @refresh-scan-path="refreshScanPath"
      @refresh-suggestions="refreshSuggestions"
      @review-suggestion="auditSuggestionsStore.reviewSuggestion"
      @analyzed="handleAnalyzedFrame"
    />

    <AppEmptyState
      v-else
      tone="audit"
      title="Run not found"
      description="No audit run matches this link."
    />
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getAuditRun } from '@/api/auditRuns';
import { listAuditFrames, listAuditScanPath } from '@/api/auditFrames';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import PageHero from '@/components/common/PageHero.vue';
import AuditRunDetailPanel from '@/components/audit/AuditRunDetailPanel.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useAuditSuggestionsStore } from '@/stores/auditSuggestions';
import type { AuditFrameDetail, AuditRunSummary, AuditFrameSummary, AuditScanPoint } from '@/types/audit';
import {
  frameDetailToScanPoint,
  frameDetailToSummary,
  upsertFrameSummary,
  upsertScanPoint,
} from '@/utils/auditScanPath';

const route = useRoute();
const auditSuggestionsStore = useAuditSuggestionsStore();

const runId = computed(() => String(route.params.runId));
const run = ref<AuditRunSummary | null>(null);
const frames = ref<AuditFrameSummary[]>([]);
const scanPath = ref<AuditScanPoint[]>([]);
const framesLoading = ref(false);
const scanPathLoading = ref(false);
const framesError = ref<string | null>(null);
const scanPathError = ref<string | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
let pollingTimer: number | undefined;

const suggestions = computed(() => auditSuggestionsStore.suggestionsForRun(runId.value));
const suggestionsLoading = computed(() => auditSuggestionsStore.isLoadingForRun(runId.value));
const suggestionsError = computed(() => auditSuggestionsStore.errorForRun(runId.value));

async function loadRun() {
  isLoading.value = true;
  error.value = null;

  try {
    run.value = await getAuditRun(runId.value);
    await Promise.all([
      auditSuggestionsStore.fetchForRun(runId.value),
      loadFrames(),
      loadScanPath(),
    ]);
  } catch (loadError) {
    error.value = loadError instanceof Error ? loadError.message : 'Could not load audit run.';
    run.value = null;
    frames.value = [];
    scanPath.value = [];
  } finally {
    isLoading.value = false;
  }
}

async function loadScanPath() {
  scanPathLoading.value = true;
  scanPathError.value = null;

  try {
    scanPath.value = await listAuditScanPath(runId.value);
  } catch (loadError) {
    scanPathError.value =
      loadError instanceof Error ? loadError.message : 'Could not load scan path.';
    scanPath.value = [];
  } finally {
    scanPathLoading.value = false;
  }
}

function refreshScanPath() {
  void loadScanPath();
}

async function loadFrames() {
  framesLoading.value = true;
  framesError.value = null;

  try {
    frames.value = await listAuditFrames(runId.value);
  } catch (loadError) {
    framesError.value =
      loadError instanceof Error ? loadError.message : 'Could not load analyzed frames.';
    frames.value = [];
  } finally {
    framesLoading.value = false;
  }
}

function refreshFrames() {
  void loadFrames();
}

function refreshSuggestions() {
  void auditSuggestionsStore.fetchForRun(runId.value);
}

function handleAnalyzedFrame(frame: AuditFrameDetail) {
  scanPath.value = upsertScanPoint(scanPath.value, frameDetailToScanPoint(frame));
  frames.value = upsertFrameSummary(frames.value, frameDetailToSummary(frame));

  if (frame.suggestion_id) {
    void auditSuggestionsStore.fetchSuggestion(frame.suggestion_id);
  }

  refreshScanPath();
  refreshSuggestions();
  refreshFrames();
}

async function refreshActiveRun() {
  try {
    run.value = await getAuditRun(runId.value);
    await Promise.all([
      auditSuggestionsStore.fetchForRun(runId.value),
      loadScanPath(),
    ]);
  } catch {
    // Keep the last good run state while polling.
  }
}

onMounted(() => {
  void loadRun();
  pollingTimer = window.setInterval(() => {
    if (!run.value || (run.value.status !== 'running' && run.value.status !== 'queued')) {
      return;
    }
    void refreshActiveRun();
  }, 8000);
});

onUnmounted(() => {
  if (pollingTimer !== undefined) {
    window.clearInterval(pollingTimer);
  }
});

watch(runId, () => {
  void loadRun();
});
</script>

<style scoped>
p {
  color: var(--text-secondary);
}
</style>
