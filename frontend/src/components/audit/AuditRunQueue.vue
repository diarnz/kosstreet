<template>
  <section class="audit-run-queue">
    <div class="audit-run-queue__head">
      <span class="audit-run-queue__count">{{ runs.length }} run{{ runs.length === 1 ? '' : 's' }}</span>
      <AppLoading v-if="isLoading" label="" tone="audit" />
    </div>

    <AppEmptyState
      v-if="!isLoading && runs.length === 0"
      tone="audit"
      title="No audit runs"
      description="Launch a scan or clear filters."
    />

    <ul v-else class="audit-run-queue__list animate-stagger">
      <li
        v-for="run in runs"
        :key="run.id"
        class="audit-run-queue__item"
        :class="[`audit-run-queue__item--${run.status}`, { 'audit-run-queue__item--selected': run.id === selectedRunId }]"
      >
        <button
          class="audit-run-queue__main"
          type="button"
          :aria-pressed="run.id === selectedRunId"
          :aria-label="`Select ${run.route_name}`"
          @click="$emit('select', run.id)"
        >
          <span class="audit-run-queue__accent" aria-hidden="true" />
          <div class="audit-run-queue__body">
            <div class="audit-run-queue__row">
              <strong class="audit-run-queue__name">{{ run.route_name }}</strong>
              <AuditRunStatusPill :status="run.status" />
            </div>
            <span class="audit-run-queue__meta">
              {{ run.municipality }} &middot; {{ formatAuditDateTime(run.created_at) }}
            </span>
            <div v-if="run.status === 'running' && run.frames_total > 0" class="audit-run-queue__progress">
              <span
                class="audit-run-queue__progress-bar"
                :style="{ width: `${Math.round((run.frames_done / run.frames_total) * 100)}%` }"
              />
            </div>
          </div>
        </button>

        <button
          class="audit-run-queue__view"
          type="button"
          :aria-label="`Open Street View for ${run.route_name}`"
          title="Street View"
          @click="$emit('view-street', run)"
        >
          <svg viewBox="0 0 24 24" fill="none" width="15" height="15" aria-hidden="true">
            <path
              d="M2.036 12.322a1 1 0 0 1 0-.644C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.964-7.178Z"
              stroke="currentColor"
              stroke-width="1.5"
            />
            <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" stroke="currentColor" stroke-width="1.5" />
          </svg>
        </button>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
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

.audit-run-queue__count {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.audit-run-queue__list {
  display: grid;
  gap: var(--space-1);
  max-height: 36rem;
  overflow: auto;
  padding-right: var(--space-1);
  margin: 0;
  padding-inline-start: 0;
  list-style: none;
}

.audit-run-queue__item {
  position: relative;
  display: flex;
  align-items: stretch;
  overflow: hidden;
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 247, 0.45);
  transition:
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.audit-run-queue__item:hover {
  border-color: rgba(23, 33, 26, 0.15);
  box-shadow: 0 4px 16px rgba(23, 33, 26, 0.05);
}

.audit-run-queue__item--selected {
  border-color: var(--source-ai-audit-border);
  background: rgba(232, 226, 212, 0.5);
  box-shadow: 0 8px 24px rgba(140, 108, 58, 0.1);
}

.audit-run-queue__accent {
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
}

.audit-run-queue__item--completed .audit-run-queue__accent { background: var(--color-municipal-green); }
.audit-run-queue__item--running .audit-run-queue__accent { background: var(--color-amber-signal); }
.audit-run-queue__item--failed .audit-run-queue__accent { background: var(--color-repair-red, #c0392b); }
.audit-run-queue__item--queued .audit-run-queue__accent { background: rgba(23, 33, 26, 0.18); }

.audit-run-queue__main {
  flex: 1;
  display: flex;
  min-width: 0;
  padding: var(--space-3) var(--space-3) var(--space-3) var(--space-5);
  border: 0;
  color: var(--text-primary);
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.audit-run-queue__body {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
  width: 100%;
}

.audit-run-queue__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  min-width: 0;
}

.audit-run-queue__name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--text-sm);
  font-weight: 850;
  letter-spacing: -0.01em;
}

.audit-run-queue__meta {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.audit-run-queue__progress {
  height: 3px;
  border-radius: var(--radius-pill);
  background: rgba(23, 33, 26, 0.08);
  overflow: hidden;
  margin-top: var(--space-1);
}

.audit-run-queue__progress-bar {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--color-amber-signal), var(--color-municipal-green));
  transition: width var(--motion-base) var(--ease-out-expo);
}

.audit-run-queue__view {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 2.5rem;
  border: 0;
  border-left: 1px solid rgba(23, 33, 26, 0.06);
  color: var(--text-muted);
  background: transparent;
  cursor: pointer;
  transition: color var(--motion-fast) ease, background var(--motion-fast) ease;
}

.audit-run-queue__view:hover {
  color: var(--color-municipal-green);
  background: rgba(47, 93, 80, 0.06);
}

.audit-run-queue__view:focus-visible {
  outline: 2px solid var(--color-amber-signal);
  outline-offset: -2px;
}
</style>
