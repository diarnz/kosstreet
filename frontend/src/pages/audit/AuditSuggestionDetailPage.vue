<template>
  <DashboardLayout>
    <PageHero
      eyebrow="AI suggestion"
      :title="suggestion ? categoryLabels[suggestion.category] : 'Suggestion review'"
      description="Inspect evidence, review, or convert to a municipal ticket."
    />

    <AppCard v-if="error" class="stack animate-fade-in" variant="inset">
      <AppBadge tone="danger">Error</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" @click="loadSuggestion">Retry</AppButton>
    </AppCard>

    <AppCard v-else-if="isLoading" class="stack" variant="inset">
      <AppLoading label="Loading suggestion" />
    </AppCard>

    <AppCard v-else-if="demoSuggestion" class="stack animate-scale-in" variant="command">
      <div class="cluster-between">
        <AppBadge tone="warning">Demo scenario</AppBadge>
        <span class="muted">{{ suggestionId }}</span>
      </div>

      <AuditSeverityLegend />

      <AnalyzedFrameViewer
        layout="detail"
        show-metadata
        :category="demoSuggestion.category"
        :confidence="demoSuggestion.confidence"
        :description="demoSuggestion.description ?? undefined"
        :frame-index="demoSuggestion.frame_index ?? undefined"
        :frames-total="16"
        :heading="demoSuggestion.heading ?? undefined"
        :image-url="demoSuggestionImageUrl(demoSuggestion)"
        :is-civic-issue="true"
        :latitude="demoSuggestion.latitude"
        :longitude="demoSuggestion.longitude"
        :pitch="demoSuggestion.pitch ?? undefined"
        :regions="demoSuggestion.detection_regions ?? []"
        :severity="demoSuggestion.severity ?? undefined"
      />

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
          <dt>Location</dt>
          <dd>{{ formatCoordinates(demoSuggestion.latitude, demoSuggestion.longitude) }}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{{ demoSuggestion.status.replace(/_/g, ' ') }}</dd>
        </div>
      </dl>
    </AppCard>

    <div v-else-if="suggestion" class="suggestion-detail stack-lg animate-fade-up">
      <AuditSeverityLegend />

      <AnalyzedFrameViewer
        layout="detail"
        show-metadata
        :category="suggestion.category"
        :confidence="suggestion.confidence"
        :description="suggestion.description ?? undefined"
        :frame-index="suggestion.frame_index ?? undefined"
        :heading="suggestion.heading ?? undefined"
        :image-url="suggestion.frame_image_url ?? undefined"
        :is-civic-issue="true"
        :latitude="suggestion.latitude"
        :longitude="suggestion.longitude"
        :pitch="suggestion.pitch ?? undefined"
        :regions="suggestion.detection_regions ?? []"
        :severity="suggestion.severity ?? undefined"
      />

      <StreetViewPanel
        compact
        eyebrow="Explore"
        title="Street context"
        :record-count="1"
        :target="streetViewTarget"
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
    </div>

    <AppEmptyState
      v-else
      description="No suggestion matches this link."
      title="Not found"
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
import AppLoading from '@/components/common/AppLoading.vue';
import PageHero from '@/components/common/PageHero.vue';
import AnalyzedFrameViewer from '@/components/audit/AnalyzedFrameViewer.vue';
import AuditSeverityLegend from '@/components/audit/AuditSeverityLegend.vue';
import AuditSuggestionCard from '@/components/audit/AuditSuggestionCard.vue';
import StreetViewPanel from '@/components/streetview/StreetViewPanel.vue';
import { demoAuditSuggestions, demoSuggestionImageUrl } from '@/demo/demoAuditSuggestions';
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
    ? demoAuditSuggestions.find((item) => item.id === suggestionId.value) ?? null
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
    error.value = loadError instanceof Error ? loadError.message : 'Could not load suggestion.';
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
  padding: var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.58);
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
