<template>
  <AppEmptyState
    v-if="allowedStatuses.length === 0"
    tone="dashboard"
    title="No next status available"
    description="This report has no configured next workflow step."
  />

  <form v-else class="status-toolbar" aria-label="Status actions" @submit.prevent="submit">
    <p v-if="isDemoData" class="status-toolbar__demo">Demo — not saved</p>

    <div class="status-toolbar__row">
      <div class="status-toolbar__choices" role="radiogroup" aria-label="Next status">
        <button
          v-for="status in allowedStatuses"
          :key="status"
          type="button"
          class="status-toolbar__choice"
          :class="[
            `status-toolbar__choice--${status}`,
            { 'status-toolbar__choice--active': nextStatus === status },
          ]"
          role="radio"
          :aria-checked="nextStatus === status"
          :title="statusLabels[status]"
          @click="selectStatus(status)"
        >
          <span class="status-toolbar__choice-icon" aria-hidden="true">
            <svg v-if="status === 'verified'" width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <svg v-else-if="status === 'rejected'" width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
            </svg>
            <svg v-else-if="status === 'assigned'" width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              <circle cx="9" cy="7" r="3.5" stroke="currentColor" stroke-width="1.8" />
              <path d="M19 8v6M22 11h-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
            <svg v-else-if="status === 'in_progress'" width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M12 6v6l3.5 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8" />
            </svg>
            <svg v-else-if="status === 'resolved'" width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
              <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8" />
            </svg>
            <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8" />
            </svg>
          </span>
        </button>
      </div>

      <input
        v-if="showNoteArea"
        v-model="note"
        class="status-toolbar__note"
        type="text"
        :disabled="isUpdating"
        maxlength="1000"
        :placeholder="notePlaceholder"
        aria-label="Workflow note"
      />

      <button
        v-else-if="!selectedStatusRequiresNote"
        type="button"
        class="status-toolbar__note-toggle"
        @click="showNoteArea = true"
      >
        Note
      </button>

      <button
        class="status-toolbar__apply"
        type="submit"
        :disabled="isDemoData || isUpdating || !nextStatus"
        :title="isUpdating ? 'Applying' : 'Apply status update'"
      >
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </button>
    </div>

    <p v-if="localError || error" class="status-toolbar__error">
      {{ localError ?? error }}
    </p>
  </form>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import type { ReportStatusUpdatePayload, TicketStatus } from '@/types/report';
import { statusLabels } from '@/utils/reportFormatting';
import { requiresWorkflowNote } from '@/utils/reportWorkflow';

const props = withDefaults(
  defineProps<{
    currentStatus: TicketStatus;
    allowedStatuses: TicketStatus[];
    isUpdating: boolean;
    error?: string | null;
    isDemoData?: boolean;
  }>(),
  {
    error: null,
    isDemoData: false,
  },
);

const emit = defineEmits<{
  update: [payload: ReportStatusUpdatePayload];
}>();

const nextStatus = ref<TicketStatus | null>(props.allowedStatuses[0] ?? null);
const note = ref('');
const submitted = ref(false);
const showNoteArea = ref(false);

const selectedStatusRequiresNote = computed(() =>
  nextStatus.value ? requiresWorkflowNote(nextStatus.value) : false,
);

const notePlaceholder = computed(() =>
  selectedStatusRequiresNote.value ? 'Required note…' : 'Optional note…',
);

const localError = computed(() => {
  if (!submitted.value || !selectedStatusRequiresNote.value || note.value.trim()) {
    return undefined;
  }
  return 'Add a note before closing this report.';
});

watch(
  () => props.allowedStatuses,
  (statuses) => {
    if (!nextStatus.value || !statuses.includes(nextStatus.value)) {
      nextStatus.value = statuses[0] ?? null;
    }
  },
);

watch(selectedStatusRequiresNote, (required) => {
  if (required) {
    showNoteArea.value = true;
  }
});

function selectStatus(status: TicketStatus) {
  nextStatus.value = status;
  submitted.value = false;
}

function submit() {
  if (props.isDemoData) return;
  submitted.value = true;
  if (!nextStatus.value) return;
  if (requiresWorkflowNote(nextStatus.value) && !note.value.trim()) return;
  emit('update', { status: nextStatus.value, note: note.value.trim() || null });
}
</script>

<style scoped>
.status-toolbar {
  display: grid;
  gap: 0.35rem;
  padding-top: 0.55rem;
  border-top: 1px solid var(--status-new-border);
}

.status-toolbar__demo {
  margin: 0;
  font-size: 0.58rem;
  font-weight: 700;
  color: var(--text-muted);
}

.status-toolbar__row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 0;
}

.status-toolbar__choices {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-shrink: 0;
}

.status-toolbar__choice--verified { --action: #0ea5e9; }
.status-toolbar__choice--rejected { --action: #ef4444; }
.status-toolbar__choice--assigned { --action: #16a34a; }
.status-toolbar__choice--in_progress { --action: #f59e0b; }
.status-toolbar__choice--resolved { --action: #059669; }
.status-toolbar__choice--new { --action: #6b7280; }

.status-toolbar__choice {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border: 1px solid color-mix(in srgb, var(--action) 28%, var(--status-new-border));
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--action) 8%, transparent);
  color: var(--action);
  cursor: pointer;
  transition:
    background var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

.status-toolbar__choice:hover {
  background: color-mix(in srgb, var(--action) 16%, transparent);
}

.status-toolbar__choice--active {
  background: var(--action);
  border-color: var(--action);
  color: #fff;
  box-shadow: 0 4px 12px color-mix(in srgb, var(--action) 30%, transparent);
}

.status-toolbar__note {
  flex: 1;
  min-width: 0;
  height: 2rem;
  padding: 0 0.6rem;
  border: 1px solid var(--status-new-border);
  border-radius: var(--radius-md);
  background: var(--surface-inset);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.68rem;
}

.status-toolbar__note:focus {
  outline: none;
  border-color: color-mix(in srgb, var(--color-municipal-green) 45%, var(--status-new-border));
}

.status-toolbar__note-toggle {
  flex: 1;
  min-width: 0;
  height: 2rem;
  padding: 0 0.55rem;
  border: 1px dashed var(--status-new-border);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 750;
  text-align: left;
  cursor: pointer;
}

.status-toolbar__note-toggle:hover {
  color: var(--color-municipal-green);
  border-color: color-mix(in srgb, var(--color-municipal-green) 35%, var(--status-new-border));
}

.status-toolbar__apply {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  flex-shrink: 0;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--color-municipal-green);
  color: #fff;
  cursor: pointer;
  transition: opacity var(--motion-fast) ease, transform var(--motion-fast) ease;
}

.status-toolbar__apply:hover:not(:disabled) {
  transform: translateY(-1px);
}

.status-toolbar__apply:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.status-toolbar__error {
  margin: 0;
  font-size: 0.62rem;
  font-weight: 700;
  color: var(--color-repair-red);
}
</style>
