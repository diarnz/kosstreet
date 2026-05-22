<template>
  <section class="audit-run-queue">
    <div class="audit-run-queue__head">
      <p class="audit-run-queue__sub">{{ runs.length }} run{{ runs.length === 1 ? '' : 's' }}</p>
      <AppLoading v-if="isLoading" label="Loading" tone="audit" />
    </div>

    <AppEmptyState
      v-if="!isLoading && runs.length === 0"
      tone="audit"
      title="No audit runs"
      description="Launch a scan or clear filters."
    />

    <div v-else class="audit-run-queue__list animate-stagger" role="list">
      <div
        v-for="run in runs"
        :key="run.id"
        class="audit-run-queue__item"
        :class="{ 'audit-run-queue__item--selected': run.id === selectedRunId }"
        role="listitem"
      >
        <button
          class="audit-run-queue__main"
          type="button"
          :aria-pressed="run.id === selectedRunId"
          :aria-label="`Select audit run ${run.route_name}`"
          @click="$emit('select', run.id)"
        >
          <span class="audit-run-queue__accent" aria-hidden="true" />
          <span class="cluster">
            <AuditRunStatusPill :status="run.status" />
            <AppBadge tone="source-ai-audit" size="sm">AI</AppBadge>
            <AppBadge v-if="isDemoData" tone="warning" size="sm">Demo</AppBadge>
          </span>
          <strong>{{ run.route_name }}</strong>
          <span class="audit-run-queue__meta">
            {{ run.municipality }} · {{ formatAuditDateTime(run.created_at) }}
          </span>
          <div v-if="run.frames_total > 0" class="audit-run-queue__progress">
            <span
              class="audit-run-queue__progress-bar"
              :style="{ width: `${Math.round((run.frames_done / run.frames_total) * 100)}%` }"
            />
          </div>
          <span v-if="run.notes" class="audit-run-queue__notes">{{ run.notes }}</span>
        </button>

        <button
          class="audit-run-queue__view"
          type="button"
          :aria-label="`Open Street View for ${run.route_name}`"
          title="Open Street View"
          @click="$emit('view-street', run)"
        >
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M2.036 12.322a1 1 0 0 1 0-.644C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.964-7.178Z"
              stroke="currentColor"
              stroke-width="1.5"
            />
            <path
              d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
              stroke="currentColor"
              stroke-width="1.5"
            />
          </svg>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import type { AuditRunSummary } from '@/types/audit';
import { formatAuditDateTime } from '@/utils/auditFormatting';
import AuditRunStatusPill from './AuditRunStatusPill.vue';

defineProps<{
  runs: AuditRunSummary[];
  selectedRunId: string | null;
  isLoading: boolean;
  isDemoData?: boolean;
}>();

defineEmits<{
  select: [runId: string];
  'view-street': [run: AuditRunSummary];
}>();
</script>

<style scoped>
.audit-run-queue {
  display: grid;
  gap: var(--space-3);
}

.audit-run-queue__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.audit-run-queue__sub {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.audit-run-queue__list {
  display: grid;
  gap: var(--space-2);
  max-height: 36rem;
  overflow: auto;
  padding-right: var(--space-1);
}

.audit-run-queue__item {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--space-2);
  align-items: stretch;
  overflow: hidden;
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.45);
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.audit-run-queue__main {
  position: relative;
  display: grid;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-4);
  border: 0;
  color: var(--text-primary);
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.audit-run-queue__accent {
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: transparent;
  transition: background var(--motion-fast) ease;
}

.audit-run-queue__item:hover {
  transform: translateX(4px);
  border-color: rgba(140, 108, 58, 0.25);
  box-shadow: 0 12px 32px rgba(23, 33, 26, 0.08);
}

.audit-run-queue__item--selected {
  border-color: var(--source-ai-audit-border);
  background: rgba(232, 226, 212, 0.5);
  box-shadow: 0 16px 36px rgba(140, 108, 58, 0.12);
  transform: translateX(6px);
}

.audit-run-queue__item--selected .audit-run-queue__accent {
  background: var(--color-amber-signal);
}

.audit-run-queue__view {
  display: grid;
  place-items: center;
  align-self: center;
  width: 2.5rem;
  height: 2.5rem;
  margin-right: var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.88);
  cursor: pointer;
  transition:
    color var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    background var(--motion-fast) ease,
    transform var(--motion-fast) ease;
}

.audit-run-queue__view svg {
  width: 1.15rem;
  height: 1.15rem;
}

.audit-run-queue__view:hover {
  color: var(--color-municipal-green);
  border-color: rgba(140, 108, 58, 0.35);
  background: #fff;
  transform: scale(1.05);
}

.audit-run-queue__view:focus-visible {
  outline: 2px solid var(--color-amber-signal);
  outline-offset: 2px;
}

.audit-run-queue__progress {
  height: 4px;
  border-radius: var(--radius-pill);
  background: rgba(23, 33, 26, 0.08);
  overflow: hidden;
}

.audit-run-queue__progress-bar {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--color-amber-signal), var(--color-municipal-green));
  transition: width var(--motion-base) var(--ease-out-expo);
}

.audit-run-queue__meta,
.audit-run-queue__notes {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
</style>
