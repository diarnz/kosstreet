<template>
  <DashboardLayout>
    <AppSectionHeader
      eyebrow="AI Suggestion Detail"
      title="AI suggestion review"
      description="Inspect one backend-persisted model detection, review it, or convert it into a municipal report."
    />

    <AppCard v-if="error" class="stack" variant="inset">
      <AppBadge tone="danger">Backend error</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" @click="loadSuggestion">Retry fetch</AppButton>
    </AppCard>

    <p v-else-if="isLoading" class="muted">Loading AI suggestion from backend...</p>

    <AppCard v-else-if="demoSuggestion" class="stack" variant="command">
      <div class="cluster-between">
        <AppBadge tone="warning">Demo scenario</AppBadge>
        <span class="muted">Suggestion ID: {{ suggestionId }}</span>
      </div>
      <p>
        Pitch Mode is showing this prepared AI suggestion scenario. It is not a live model result
        and does not include restricted imagery.
      </p>
      <dl class="suggestion-detail-grid">
        <div>
          <dt>Category</dt>
          <dd>{{ categoryLabels[demoSuggestion.category] }}</dd>
        </div>
        <div>
          <dt>Confidence</dt>
          <dd>{{ formatConfidence(demoSuggestion.confidence) }}</dd>
        </div>
        <div>
          <dt>Coordinates</dt>
          <dd>{{ formatCoordinates(demoSuggestion.latitude, demoSuggestion.longitude) }}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{{ demoSuggestion.status.replace(/_/g, ' ') }}</dd>
        </div>
      </dl>
    </AppCard>

    <template v-else-if="suggestion">
      <AnalyzedFrameViewer
        :category="suggestion.category"
        :confidence="suggestion.confidence"
        :description="suggestion.description"
        :frame-index="suggestion.frame_index"
        :heading="suggestion.heading"
        :image-url="suggestion.frame_image_url"
        :pitch="suggestion.pitch"
        :regions="suggestion.detection_regions"
        :severity="suggestion.severity"
      />

      <StreetViewPanel
        compact
        eyebrow="Geographic context"
        :record-count="1"
        :target="streetViewTarget"
        title="Interactive Street View"
      />

      <AuditSuggestionCard
        :convert-error="auditSuggestionsStore.convertErrorById[suggestion.id] ?? null"
        :converted-report-id="auditSuggestionsStore.convertedReportBySuggestionId[suggestion.id] ?? null"
        :is-converting="auditSuggestionsStore.convertLoadingById[suggestion.id] ?? false"
        :is-reviewing="auditSuggestionsStore.reviewLoadingById[suggestion.id] ?? false"
        :review-error="auditSuggestionsStore.reviewErrorById[suggestion.id] ?? null"
        :suggestion="suggestion"
        @convert="auditSuggestionsStore.convertSuggestionToReport"
        @review="auditSuggestionsStore.reviewSuggestion"
      />
    </template>

    <AppEmptyState
      v-else
      description="The backend did not return an AI suggestion for this URL."
      title="Suggestion not found"
      tone="audit"
    />
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AuditSuggestionCard from '@/components/audit/AuditSuggestionCard.vue';
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import StreetViewPanel from '@/components/streetview/StreetViewPanel.vue';
import { demoAuditSuggestions } from '@/demo/demoAuditSuggestions';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useAuditSuggestionsStore } from '@/stores/auditSuggestions';
import { useUiStore } from '@/stores/ui';
import type { AuditSuggestion } from '@/types/detection';
import { categoryLabels, formatConfidence, formatCoordinates } from '@/utils/reportFormatting';
import { suggestionToStreetViewTarget } from '@/utils/streetView';

const route = useRoute();
const uiStore = useUiStore();
const auditSuggestionsStore = useAuditSuggestionsStore();
const suggestionId = computed(() => String(route.params.suggestionId));
const suggestion = ref<AuditSuggestion | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const streetViewTarget = computed(() =>
  suggestion.value ? suggestionToStreetViewTarget(suggestion.value) : null,
);
const demoSuggestion = computed(() =>
  uiStore.demoMode
    ? demoAuditSuggestions.find((suggestion) => suggestion.id === suggestionId.value) ?? null
    : null,
);

async function loadSuggestion() {
  if (demoSuggestion.value) {
    suggestion.value = null;
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    suggestion.value = await auditSuggestionsStore.fetchSuggestion(suggestionId.value);
  } catch (loadError) {
    error.value = loadError instanceof Error ? loadError.message : 'Could not load AI suggestion.';
    suggestion.value = null;
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  void loadSuggestion();
});

watch(suggestionId, () => {
  void loadSuggestion();
});
</script>

<style scoped>
p {
  color: var(--text-secondary);
}

code {
  color: var(--source-ai-audit-text);
  font-weight: 800;
}

.suggestion-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin: 0;
}

.suggestion-detail-grid > div {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
}

dt {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

dd {
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--text-primary);
  font-weight: 750;
  text-transform: capitalize;
}

@media (max-width: 620px) {
  .suggestion-detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
