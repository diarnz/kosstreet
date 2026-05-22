<template>
  <CitizenLayout>
    <AppSectionHeader
      eyebrow="Report submitted"
      title="Your report is now in the municipal workflow."
      description="Keep this tracking ID. Live status lookup will be connected once the report detail endpoint is available."
    />

    <AppCard class="status-card stack" variant="command">
      <div class="cluster-between">
        <div>
          <p class="eyebrow">Tracking ID</p>
          <h2>{{ reportId }}</h2>
        </div>
        <StatusPill status="new" />
      </div>
      <p>
        Your structured report was submitted successfully. The current page explains the standard
        municipal lifecycle without pretending to load live report detail.
      </p>
    </AppCard>

    <AppCard class="stack" variant="inset">
      <div>
        <h2>What happens next</h2>
        <p>The municipality reviews, verifies, assigns, works on, and resolves reports.</p>
      </div>
      <ReportWorkflowTimeline current-status="new" />
    </AppCard>

    <div class="cluster">
      <RouterLink class="status-link status-link--primary" to="/report">Create another report</RouterLink>
      <RouterLink class="status-link" to="/dashboard">Open dashboard</RouterLink>
    </div>
  </CitizenLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppCard from '@/components/common/AppCard.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import ReportWorkflowTimeline from '@/components/reports/ReportWorkflowTimeline.vue';
import StatusPill from '@/components/reports/StatusPill.vue';
import CitizenLayout from '@/layouts/CitizenLayout.vue';

const route = useRoute();
const reportId = computed(() => String(route.params.id ?? 'Unknown'));
</script>

<style scoped>
.status-card h2 {
  max-width: 100%;
  margin: 0;
  overflow-wrap: anywhere;
  font-size: clamp(1.3rem, 5vw, 2rem);
}

.status-card p,
section p {
  color: var(--text-secondary);
}

.status-link {
  display: inline-flex;
  align-items: center;
  min-height: 3rem;
  padding: 0 var(--space-5);
  border: var(--border-strong);
  border-radius: var(--radius-pill);
  font-weight: 850;
}

.status-link--primary {
  color: var(--text-inverse);
  background: var(--action-primary);
  border-color: transparent;
}
</style>
