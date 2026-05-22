<template>
  <DashboardLayout>
    <AppSectionHeader
      eyebrow="AI Suggestion Detail"
      title="Suggestion API not connected yet"
      description="This route is reserved for real AI detections after the backend exposes suggestion endpoints."
    />

    <AppCard class="stack" variant="command">
      <div class="cluster-between">
        <AppBadge tone="source-ai-audit">Real data required</AppBadge>
        <span class="muted">Suggestion ID: {{ suggestionId }}</span>
      </div>
      <p>
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
import DashboardLayout from '@/layouts/DashboardLayout.vue';

const route = useRoute();
const suggestionId = computed(() => String(route.params.suggestionId));
</script>

<style scoped>
p {
  color: var(--text-secondary);
}

code {
  color: var(--source-ai-audit-text);
  font-weight: 800;
}
</style>
