<template>
  <DashboardLayout>
    <AppSectionHeader
      eyebrow="Audit Run Detail"
      title="Audit run lookup"
      description="Direct run URLs are resolved from the current backend audit-run list until a dedicated detail endpoint exists."
    />

    <AppCard v-if="auditRunsStore.error" class="stack" variant="inset">
      <AppBadge tone="danger">Backend error</AppBadge>
      <p>{{ auditRunsStore.error }}</p>
      <AppButton variant="secondary" @click="auditRunsStore.fetchRuns">Retry fetch</AppButton>
    </AppCard>

    <AuditRunDetailPanel v-else-if="matchedRun" :run="matchedRun" />

    <AppEmptyState
      v-else
      tone="audit"
      title="Run not found in current backend response"
      description="The frontend can only resolve direct audit-run URLs from `GET /api/v1/audit-runs` until a backend detail endpoint is available."
    />
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AuditRunDetailPanel from '@/components/audit/AuditRunDetailPanel.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useAuditRunsStore } from '@/stores/auditRuns';

const route = useRoute();
const auditRunsStore = useAuditRunsStore();

const runId = computed(() => String(route.params.runId));
const matchedRun = computed(() => auditRunsStore.runs.find((run) => run.id === runId.value) ?? null);

onMounted(async () => {
  await auditRunsStore.fetchRuns();
  auditRunsStore.selectRun(matchedRun.value?.id ?? null);
});
</script>

<style scoped>
p {
  color: var(--text-secondary);
}
</style>
