<template>
  <DashboardLayout>
    <AppSectionHeader
      eyebrow="AI Suggestion Detail"
      title="Suggestion API not connected yet"
      description="This route is reserved for real AI detections after the backend exposes suggestion endpoints."
    />

    <AppCard class="stack" variant="command">
      <div class="cluster-between">
        <AppBadge :tone="demoSuggestion ? 'warning' : 'source-ai-audit'">
          {{ demoSuggestion ? 'Demo scenario' : 'Real data required' }}
        </AppBadge>
        <span class="muted">Suggestion ID: {{ suggestionId }}</span>
      </div>
      <template v-if="demoSuggestion">
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
      </template>
      <p v-else>
        No AI suggestion is rendered here because the current backend does not yet expose
        <code>GET /api/v1/audit-runs/:id/suggestions</code> or
        <code>GET /api/v1/audit-suggestions/:id</code>.
      </p>
      <AuditSuggestionUnavailablePanel />
    </AppCard>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AuditSuggestionUnavailablePanel from '@/components/audit/AuditSuggestionUnavailablePanel.vue';
import { demoAuditSuggestions } from '@/demo/demoAuditSuggestions';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useUiStore } from '@/stores/ui';
import { categoryLabels, formatConfidence, formatCoordinates } from '@/utils/reportFormatting';

const route = useRoute();
const uiStore = useUiStore();
const suggestionId = computed(() => String(route.params.suggestionId));
const demoSuggestion = computed(() =>
  uiStore.demoMode
    ? demoAuditSuggestions.find((suggestion) => suggestion.id === suggestionId.value) ?? null
    : null,
);
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
