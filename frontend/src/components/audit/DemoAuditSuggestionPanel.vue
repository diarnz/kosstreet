<template>
  <AppCard class="demo-suggestion-panel stack" variant="command">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Pitch Mode</p>
        <h2>Demo AI suggestion scenarios</h2>
      </div>
      <AppBadge tone="source-ai-audit">Review-only fixtures</AppBadge>
    </div>

    <p>
      These are prepared frontend scenarios for the hackathon walkthrough. Real suggestions will
      come from <code>GET /api/v1/audit-runs/:id/suggestions</code> after backend and AI endpoints
      are connected.
    </p>

    <div class="demo-suggestion-panel__grid">
      <DemoAuditSuggestionCard
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        :suggestion="suggestion"
      />
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import DemoAuditSuggestionCard from './DemoAuditSuggestionCard.vue';
import type { AuditSuggestion } from '@/types/detection';

defineProps<{
  suggestions: AuditSuggestion[];
}>();
</script>

<style scoped>
.demo-suggestion-panel h2,
.demo-suggestion-panel p {
  margin: 0;
}

.demo-suggestion-panel p {
  color: var(--text-secondary);
}

.demo-suggestion-panel code {
  color: var(--text-primary);
  font-weight: 850;
}

.demo-suggestion-panel__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: var(--space-4);
}
</style>
