<template>

  <AppCard class="audit-run-detail stack" variant="command">

    <template v-if="run">

      <div class="audit-run-detail__hero">

        <div class="audit-run-detail__intro">

          <p class="eyebrow">Review workspace</p>

          <h2>{{ run.route_name }}</h2>

        </div>

        <div class="audit-run-detail__status cluster">

          <AuditRunStatusPill :status="run.status" />

          <AppBadge v-if="isDemoData" tone="warning">Demo</AppBadge>

        </div>

      </div>



      <div class="audit-run-detail__facts">

        <div class="audit-run-detail__fact">

          <span class="audit-run-detail__fact-label">City</span>

          <strong>{{ run.municipality }}</strong>

        </div>

        <div class="audit-run-detail__fact">

          <span class="audit-run-detail__fact-label">Scanned</span>

          <strong>{{ formatAuditDateTime(run.created_at) }}</strong>

        </div>

        <div class="audit-run-detail__fact">

          <span class="audit-run-detail__fact-label">Issues</span>

          <strong>{{ issueCount }}</strong>

        </div>

      </div>



      <p v-if="run.notes" class="audit-run-detail__notes muted">{{ run.notes }}</p>

      <AppCard v-if="isLegacyRun" class="audit-run-detail__legacy stack" variant="muted">
        <AppBadge tone="warning">Legacy scan format</AppBadge>
        <p class="audit-run-detail__legacy-copy">
          This run used the older four-heading capture model. Use the All frames tab for the full
          filmstrip; the scanner timeline reflects route waypoints only.
        </p>
        <AppButton
          v-if="activeTab !== 'frames'"
          size="sm"
          type="button"
          variant="secondary"
          @click="activeTab = 'frames'"
        >
          Open All frames
        </AppButton>
      </AppCard>

      <div class="audit-run-detail__tabs" role="tablist" aria-label="Audit run views">

        <button

          class="audit-run-detail__tab"

          :class="{ 'audit-run-detail__tab--active': activeTab === 'scanner' }"

          type="button"

          role="tab"

          :aria-selected="activeTab === 'scanner'"

          @click="activeTab = 'scanner'"

        >

          Scanner

        </button>

        <button

          class="audit-run-detail__tab"

          :class="{ 'audit-run-detail__tab--active': activeTab === 'frames' }"

          type="button"

          role="tab"

          :aria-selected="activeTab === 'frames'"

          @click="activeTab = 'frames'"

        >

          All frames

        </button>

      </div>



      <div v-if="activeTab === 'scanner'" class="audit-run-detail__workspace">
        <AuditStreetViewScanner
          class="audit-run-detail__scanner"
          :error="scanPathError"
          :is-demo-data="isDemoData"
          :is-loading="scanPathLoading"
          :run="run"
          :scan-path="scanPath"
          :selected-frame-index="selectedFrameIndex"
          :selected-suggestion="selectedSuggestion"
          :suggestions="suggestions"
          @refresh="$emit('refreshScanPath')"
          @analyzed="handleAnalyzed"
          @scan-point-selected="selectScanPoint"
        />



        <AuditSuggestionList
          class="audit-run-detail__suggestions"
          compact-cards
          :convert-error-by-id="convertErrorById"

          :convert-loading-by-id="convertLoadingById"

          :converted-report-by-suggestion-id="convertedReportBySuggestionId"

          :error="suggestionsError"

          :is-loading="suggestionsLoading"

          :review-error-by-id="reviewErrorById"

          :review-loading-by-id="reviewLoadingById"

          :selected-suggestion-id="selectedSuggestionId"

          :show-scanner-actions="true"

          :suggestions="suggestions"

          @convert="$emit('convertSuggestion', $event)"

          @refresh="$emit('refreshSuggestions')"

          @review="(suggestionId, payload) => $emit('reviewSuggestion', suggestionId, payload)"

          @select="selectSuggestion"

        />

      </div>



      <AuditFrameBrowser
        v-else-if="activeTab === 'frames'"
        :error="framesError"
        :frames="frames"
        :is-loading="framesLoading"
        :run-id="run.id"
        @refresh="$emit('refreshFrames')"
      />

    </template>



    <AppEmptyState

      v-else

      tone="audit"

      title="Select an audit run"

      description="Choose a run from the queue to review AI detections."

    />

  </AppCard>

</template>



<script setup lang="ts">

import { computed, ref, watch } from 'vue';

import AppButton from '@/components/common/AppButton.vue';
import AppBadge from '@/components/common/AppBadge.vue';

import AppCard from '@/components/common/AppCard.vue';

import AppEmptyState from '@/components/common/AppEmptyState.vue';

import type { AuditRunSummary, AuditFrameDetail, AuditFrameSummary, AuditScanPoint } from '@/types/audit';

import type { AuditSuggestion, AuditSuggestionReviewPayload } from '@/types/detection';

import { formatAuditDateTime } from '@/utils/auditFormatting';
import { isLegacyAuditRun } from '@/utils/auditLegacy';
import { pickInitialScanPoint } from '@/utils/streetView';

import AuditSuggestionList from './AuditSuggestionList.vue';

import AuditFrameBrowser from './AuditFrameBrowser.vue';

import AuditRunStatusPill from './AuditRunStatusPill.vue';

import AuditStreetViewScanner from './AuditStreetViewScanner.vue';



const props = withDefaults(

  defineProps<{

    run: AuditRunSummary | null;

    isDemoData?: boolean;

    suggestions?: AuditSuggestion[];

    scanPath?: AuditScanPoint[];

    scanPathLoading?: boolean;

    scanPathError?: string | null;

    frames?: AuditFrameSummary[];

    framesLoading?: boolean;

    framesError?: string | null;

    suggestionsLoading?: boolean;

    suggestionsError?: string | null;

    reviewLoadingById?: Record<string, boolean>;

    reviewErrorById?: Record<string, string | null>;

    convertLoadingById?: Record<string, boolean>;

    convertErrorById?: Record<string, string | null>;

    convertedReportBySuggestionId?: Record<string, string>;

  }>(),

  {

    isDemoData: false,

    suggestions: () => [],

    scanPath: () => [],

    scanPathLoading: false,

    scanPathError: null,

    frames: () => [],

    framesLoading: false,

    framesError: null,

    suggestionsLoading: false,

    suggestionsError: null,

    reviewLoadingById: () => ({}),

    reviewErrorById: () => ({}),

    convertLoadingById: () => ({}),

    convertErrorById: () => ({}),

    convertedReportBySuggestionId: () => ({}),

  },

);



const emit = defineEmits<{

  refreshSuggestions: [];

  refreshFrames: [];

  refreshScanPath: [];

  reviewSuggestion: [suggestionId: string, payload: AuditSuggestionReviewPayload];

  convertSuggestion: [suggestionId: string];

  analyzed: [frame: AuditFrameDetail];

}>();



const activeTab = ref<'scanner' | 'frames'>('scanner');

const selectedFrameIndex = ref<number | null>(null);

const selectedSuggestionId = ref<string | null>(null);



const selectedSuggestion = computed(() =>

  props.suggestions.find((suggestion) => suggestion.id === selectedSuggestionId.value) ?? null,

);



const isLegacyRun = computed(() =>
  props.run ? isLegacyAuditRun(props.run, props.scanPath.length) : false,
);

const issueCount = computed(() => {

  const fromScanPath = props.scanPath.filter((point) => point.is_civic_issue).length;

  if (fromScanPath > 0) {

    return fromScanPath;

  }

  const fromFrames = props.frames.filter((frame) => frame.is_civic_issue).length;

  if (fromFrames > 0) {

    return fromFrames;

  }

  return props.suggestions.length;

});



watch(
  () => props.run?.id,
  () => {
    activeTab.value =
      props.run && isLegacyAuditRun(props.run, props.scanPath.length) ? 'frames' : 'scanner';
    selectedFrameIndex.value = null;
    selectedSuggestionId.value = null;
  },
);



watch(

  () => [props.run?.id, props.scanPath] as const,

  ([runId, scanPath]) => {

    if (!runId || !scanPath.length || selectedFrameIndex.value != null) {

      return;

    }

    const initial = pickInitialScanPoint(scanPath);

    selectedFrameIndex.value = initial?.frame_index ?? null;

  },

  { immediate: true },

);



function handleAnalyzed(frame: AuditFrameDetail) {
  selectedFrameIndex.value = frame.frame_index;

  if (frame.suggestion_id) {
    selectedSuggestionId.value = frame.suggestion_id;
  }

  emit('analyzed', frame);
  emit('refreshScanPath');
  emit('refreshSuggestions');
  emit('refreshFrames');
}



function selectScanPoint(frameIndex: number) {

  selectedFrameIndex.value = frameIndex;

  selectedSuggestionId.value = null;



  const linkedSuggestionId = props.scanPath.find(

    (point) => point.frame_index === frameIndex,

  )?.suggestion_id;

  if (linkedSuggestionId) {

    selectedSuggestionId.value = linkedSuggestionId;

  }

}



function selectSuggestion(suggestionId: string) {

  selectedSuggestionId.value = suggestionId;

  const suggestion = props.suggestions.find((entry) => entry.id === suggestionId);

  if (suggestion?.frame_index != null) {

    selectedFrameIndex.value = suggestion.frame_index;

  }

}

</script>



<style scoped>

.audit-run-detail__hero {

  display: flex;

  flex-wrap: wrap;

  align-items: flex-start;

  justify-content: space-between;

  gap: var(--space-4);

}



.audit-run-detail__intro h2 {

  margin: 0.15rem 0 0;

  font-size: clamp(1.5rem, 3vw, 2.1rem);

  letter-spacing: -0.03em;

}



.audit-run-detail__facts {

  display: grid;

  grid-template-columns: repeat(3, minmax(0, 1fr));

  gap: var(--space-3);

}



.audit-run-detail__fact {

  display: grid;

  gap: var(--space-1);

  padding: var(--space-3) var(--space-4);

  border: var(--border-soft);

  border-radius: var(--radius-md);

  background: rgba(255, 253, 247, 0.62);

}



.audit-run-detail__fact-label {

  color: var(--text-muted);

  font-size: var(--text-xs);

  font-weight: 900;

  letter-spacing: 0.08em;

  text-transform: uppercase;

}



.audit-run-detail__fact strong {

  color: var(--text-primary);

  font-size: var(--text-sm);

  font-weight: 850;

}



.audit-run-detail__notes {

  margin: 0;

  padding: var(--space-3) var(--space-4);

  border-left: 3px solid rgba(47, 93, 80, 0.35);

  font-size: var(--text-sm);

  line-height: 1.45;

}



.audit-run-detail__legacy-copy {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.45;
}

.audit-run-detail__tabs {

  display: flex;

  flex-wrap: wrap;

  gap: var(--space-2);

  padding-top: var(--space-2);

  border-top: 1px solid rgba(23, 33, 26, 0.08);

}



.audit-run-detail__tab {

  border: var(--border-soft);

  border-radius: var(--radius-pill);

  padding: var(--space-2) var(--space-4);

  color: var(--text-secondary);

  background: rgba(255, 253, 247, 0.72);

  font-size: var(--text-sm);

  font-weight: 800;

  cursor: pointer;

}



.audit-run-detail__tab--active {

  border-color: rgba(47, 93, 80, 0.35);

  color: var(--text-primary);

  background: rgba(47, 93, 80, 0.1);

}



.audit-run-detail__workspace {

  display: grid;

  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.75fr);

  gap: var(--space-4);

  align-items: start;

}



.audit-run-detail__scanner {

  min-width: 0;

}



.audit-run-detail__suggestions {

  max-height: clamp(28rem, 70vh, 42rem);

  overflow: auto;

  padding-right: var(--space-1);

}



@media (max-width: 980px) {

  .audit-run-detail__workspace {

    grid-template-columns: 1fr;

  }



  .audit-run-detail__suggestions {

    max-height: none;

  }

}



@media (max-width: 720px) {

  .audit-run-detail__facts {

    grid-template-columns: 1fr;

  }

}

</style>

