<template>
  <DashboardLayout>
    <header class="command-header animate-fade-up">
      <div>
        <p class="command-label">AI operations</p>
        <h1>Street audit</h1>
        <p class="command-header__sub">Scan routes · Review AI · Convert to tickets</p>
      </div>
    </header>

    <GlassPanel v-if="auditRunsStore.error" label="Error" class="animate-fade-in">
      <p class="command-error">{{ auditRunsStore.error }}</p>
      <AppButton variant="secondary" size="sm" @click="auditRunsStore.fetchRuns">Retry</AppButton>
    </GlassPanel>

    <div class="audit-top animate-fade-up">
      <AuditRunMetrics :metrics="auditRunsStore.metrics" />
      <GlassPanel elevated padding="sm" class="audit-top__form">
        <AuditRunForm
          :error="auditRunsStore.createError"
          :is-creating="auditRunsStore.isCreating"
          @create="auditRunsStore.createRun"
        />
      </GlassPanel>
    </div>

    <section class="audit-deck animate-fade-up">
      <GlassPanel padding="sm" class="audit-deck__queue">
        <AuditRunFilters
          :filters="auditRunsStore.filters"
          @clear="auditRunsStore.clearFilters"
          @update:search="auditRunsStore.setSearch"
          @update:status="auditRunsStore.setStatus"
        />
        <AuditRunQueue
          :is-demo-data="auditRunsStore.usingDemoRuns"
          :is-loading="auditRunsStore.isLoading"
          :runs="auditRunsStore.filteredRuns"
          :selected-run-id="auditRunsStore.selectedRunId"
          @select="auditRunsStore.selectRun"
          @view-street="selectRunForScanner"
        />
      </GlassPanel>
    </section>

    <section class="audit-detail-section animate-fade-in">
      <AuditRunDetailPanel
        :convert-error-by-id="auditSuggestionsStore.convertErrorById"
        :convert-loading-by-id="auditSuggestionsStore.convertLoadingById"
        :converted-report-by-suggestion-id="auditSuggestionsStore.convertedReportBySuggestionId"
        :frames="selectedRunFrames"
        :frames-error="selectedRunFramesError"
        :frames-loading="selectedRunFramesLoading"
        :is-demo-data="auditRunsStore.usingDemoRuns"
        :review-error-by-id="auditSuggestionsStore.reviewErrorById"
        :review-loading-by-id="auditSuggestionsStore.reviewLoadingById"
        :run="auditRunsStore.selectedRun"
        :scan-path="selectedRunScanPath"
        :scan-path-error="selectedRunScanPathError"
        :scan-path-loading="selectedRunScanPathLoading"
        :suggestions="selectedRunSuggestions"
        :suggestions-error="selectedRunSuggestionsError"
        :suggestions-loading="selectedRunSuggestionsLoading"
        @convert-suggestion="auditSuggestionsStore.convertSuggestionToReport"
        @refresh-frames="refreshSelectedRunFrames"
        @refresh-scan-path="refreshSelectedRunScanPath"
        @refresh-suggestions="refreshSelectedRunSuggestions"
        @review-suggestion="auditSuggestionsStore.reviewSuggestion"
        @analyzed="handleAnalyzedFrame"
      />
    </section>

    <DemoAuditSuggestionPanel v-if="uiStore.demoMode" :suggestions="demoAuditSuggestions" />
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import GlassPanel from '@/components/common/GlassPanel.vue';
import { listAuditFrames, listAuditScanPath } from '@/api/auditFrames';
import DemoAuditSuggestionPanel from '@/components/audit/DemoAuditSuggestionPanel.vue';
import AuditRunDetailPanel from '@/components/audit/AuditRunDetailPanel.vue';
import AuditRunFilters from '@/components/audit/AuditRunFilters.vue';
import AuditRunForm from '@/components/audit/AuditRunForm.vue';
import AuditRunMetrics from '@/components/audit/AuditRunMetrics.vue';
import AuditRunQueue from '@/components/audit/AuditRunQueue.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { demoAuditSuggestions } from '@/demo/demoAuditSuggestions';
import {
  buildDemoFrames,
  buildDemoScanPath,
  demoSuggestionsForRun,
} from '@/demo/demoAuditScanPath';
import { useAuditRunsStore } from '@/stores/auditRuns';
import { useAuditSuggestionsStore } from '@/stores/auditSuggestions';
import { useUiStore } from '@/stores/ui';
import type { AuditFrameDetail, AuditFrameSummary, AuditRunSummary, AuditScanPoint } from '@/types/audit';
import { formatAuditDateTime } from '@/utils/auditFormatting';
import {
  frameDetailToScanPoint,
  frameDetailToSummary,
  upsertFrameSummary,
  upsertScanPoint,
} from '@/utils/auditScanPath';

const auditRunsStore = useAuditRunsStore();
const auditSuggestionsStore = useAuditSuggestionsStore();
const uiStore = useUiStore();

let pollingTimer: number | undefined;

const selectedRunSuggestions = computed(() => {
  if (auditRunsStore.usingDemoRuns && auditRunsStore.selectedRunId) {
    return demoSuggestionsForRun(auditRunsStore.selectedRunId);
  }
  return auditSuggestionsStore.suggestionsForRun(auditRunsStore.selectedRunId);
});
const selectedRunSuggestionsLoading = computed(() =>
  auditSuggestionsStore.isLoadingForRun(auditRunsStore.selectedRunId),
);
const selectedRunSuggestionsError = computed(() =>
  auditSuggestionsStore.errorForRun(auditRunsStore.selectedRunId),
);

const selectedRunFrames = ref<AuditFrameSummary[]>([]);
const selectedRunScanPath = ref<AuditScanPoint[]>([]);
const selectedRunFramesLoading = ref(false);
const selectedRunScanPathLoading = ref(false);
const selectedRunFramesError = ref<string | null>(null);
const selectedRunScanPathError = ref<string | null>(null);

function selectRunForScanner(run: AuditRunSummary) {
  auditRunsStore.selectRun(run.id);
}

onMounted(() => {
  void auditRunsStore.fetchRuns();
  pollingTimer = window.setInterval(() => {
    const selectedRun = auditRunsStore.selectedRun;
    if (!selectedRun || auditRunsStore.usingDemoRuns) return;
    if (selectedRun.status === 'queued' || selectedRun.status === 'running') {
      void auditRunsStore.fetchRuns();
      void auditSuggestionsStore.fetchForRun(selectedRun.id);
      void loadSelectedRunScanPath(selectedRun.id);
    }
  }, 8000);
});

onUnmounted(() => {
  if (pollingTimer !== undefined) window.clearInterval(pollingTimer);
});

watch(
  () => auditRunsStore.filteredRuns,
  (runs) => {
    if (!runs.some((run) => run.id === auditRunsStore.selectedRunId)) {
      auditRunsStore.selectRun(runs[0]?.id ?? null);
    }
  },
  { immediate: true },
);

watch(
  () => auditRunsStore.selectedRunId,
  (runId) => {
    if (runId && auditRunsStore.usingDemoRuns) {
      loadDemoRunData(runId);
      return;
    }

    if (runId && !auditRunsStore.usingDemoRuns) {
      void auditSuggestionsStore.fetchForRun(runId);
      void loadSelectedRunFrames(runId);
      void loadSelectedRunScanPath(runId);
    } else {
      selectedRunFrames.value = [];
      selectedRunScanPath.value = [];
      selectedRunFramesError.value = null;
      selectedRunScanPathError.value = null;
    }
  },
);

function loadDemoRunData(runId: string) {
  selectedRunScanPathLoading.value = true;
  selectedRunFramesLoading.value = true;
  selectedRunScanPathError.value = null;
  selectedRunFramesError.value = null;

  try {
    selectedRunScanPath.value = buildDemoScanPath(runId);
    selectedRunFrames.value = buildDemoFrames(runId);
  } catch (loadError) {
    const message =
      loadError instanceof Error ? loadError.message : 'Could not load demo scan data.';
    selectedRunScanPathError.value = message;
    selectedRunFramesError.value = message;
    selectedRunScanPath.value = [];
    selectedRunFrames.value = [];
  } finally {
    selectedRunScanPathLoading.value = false;
    selectedRunFramesLoading.value = false;
  }
}

async function loadSelectedRunScanPath(runId: string) {
  selectedRunScanPathLoading.value = true;
  selectedRunScanPathError.value = null;

  try {
    selectedRunScanPath.value = await listAuditScanPath(runId);
  } catch (loadError) {
    selectedRunScanPathError.value =
      loadError instanceof Error ? loadError.message : 'Could not load scan path.';
    selectedRunScanPath.value = [];
  } finally {
    selectedRunScanPathLoading.value = false;
  }
}

async function loadSelectedRunFrames(runId: string) {
  selectedRunFramesLoading.value = true;
  selectedRunFramesError.value = null;

  try {
    selectedRunFrames.value = await listAuditFrames(runId);
  } catch (loadError) {
    selectedRunFramesError.value =
      loadError instanceof Error ? loadError.message : 'Could not load analyzed frames.';
    selectedRunFrames.value = [];
  } finally {
    selectedRunFramesLoading.value = false;
  }
}

function refreshSelectedRunSuggestions() {
  if (auditRunsStore.selectedRunId && !auditRunsStore.usingDemoRuns) {
    void auditSuggestionsStore.fetchForRun(auditRunsStore.selectedRunId);
  }
}

function refreshSelectedRunFrames() {
  if (!auditRunsStore.selectedRunId) return;
  if (auditRunsStore.usingDemoRuns) {
    loadDemoRunData(auditRunsStore.selectedRunId);
    return;
  }
  void loadSelectedRunFrames(auditRunsStore.selectedRunId);
}

function refreshSelectedRunScanPath() {
  if (!auditRunsStore.selectedRunId) return;
  if (auditRunsStore.usingDemoRuns) {
    loadDemoRunData(auditRunsStore.selectedRunId);
    return;
  }
  void loadSelectedRunScanPath(auditRunsStore.selectedRunId);
}

function handleAnalyzedFrame(frame: AuditFrameDetail) {
  selectedRunScanPath.value = upsertScanPoint(
    selectedRunScanPath.value,
    frameDetailToScanPoint(frame),
  );
  selectedRunFrames.value = upsertFrameSummary(
    selectedRunFrames.value,
    frameDetailToSummary(frame),
  );

  if (frame.suggestion_id && !auditRunsStore.usingDemoRuns) {
    void auditSuggestionsStore.fetchSuggestion(frame.suggestion_id);
  }

  refreshSelectedRunScanPath();
  refreshSelectedRunSuggestions();
  refreshSelectedRunFrames();
}
</script>

<style scoped>
.command-header {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: flex-end;
  justify-content: space-between;
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
  background: linear-gradient(180deg, var(--color-amber-signal), var(--color-municipal-green));
  box-shadow: 0 0 10px rgba(217, 144, 47, 0.35);
}

.command-header h1 {
  margin: 0.15rem 0 0;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.5vw, 2.5rem);
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, var(--color-ink) 0%, rgba(47, 93, 80, 0.8) 100%);
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

.audit-top {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  flex-wrap: wrap;
}

.audit-top__form {
  flex: 1;
  min-width: 0;
}

.audit-deck {
  display: grid;
  gap: var(--space-4);
  align-items: start;
}

.audit-deck__queue {
  display: grid;
  gap: var(--space-3);
}

.audit-detail-section {
  padding-top: var(--space-2);
  border-top: 1px solid rgba(23, 33, 26, 0.08);
}

@media (max-width: 640px) {
  .audit-top {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
