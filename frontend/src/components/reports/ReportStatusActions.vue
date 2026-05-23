<template>
  <AppEmptyState
    v-if="allowedStatuses.length === 0"
    tone="dashboard"
    title="No next status available"
    description="This report has no configured next workflow step."
  />

  <div v-else class="status-actions">
    <p v-if="isDemoData" class="status-actions__demo">Demo — changes are not persisted.</p>

    <form class="status-actions__form" @submit.prevent="submit">
      <fieldset>
        <legend>Next status</legend>
        <div class="status-actions__options">
          <label
            v-for="status in allowedStatuses"
            :key="status"
            class="status-actions__option"
            :class="[`status-actions__option--${status}`, { 'status-actions__option--selected': nextStatus === status }]"
          >
            <input v-model="nextStatus" :value="status" name="next-status" type="radio" />
            {{ statusLabels[status] }}
          </label>
        </div>
      </fieldset>

      <AppField label="Municipal note" :helper="noteHelper" :error="localError">
        <AppTextarea
          v-model="note"
          aria-label="Municipal workflow note"
          :disabled="isUpdating"
          :maxlength="1000"
          placeholder="Add a concise review, resolution, or rejection note."
        />
      </AppField>

      <p v-if="error" class="status-actions__api-error">{{ error }}</p>

      <AppButton :disabled="isDemoData || isUpdating || !nextStatus" type="submit">
        {{ isUpdating ? 'Updating…' : 'Send status update' }}
      </AppButton>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppButton from '@/components/common/AppButton.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppField from '@/components/common/AppField.vue';
import AppTextarea from '@/components/common/AppTextarea.vue';
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

const selectedStatusRequiresNote = computed(() =>
  nextStatus.value ? requiresWorkflowNote(nextStatus.value) : false,
);

const noteHelper = computed(() =>
  selectedStatusRequiresNote.value
    ? 'Required when resolving or rejecting a report.'
    : 'Optional context for municipal review history.',
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

function submit() {
  if (props.isDemoData) return;
  submitted.value = true;
  if (!nextStatus.value) return;
  if (requiresWorkflowNote(nextStatus.value) && !note.value.trim()) return;
  emit('update', { status: nextStatus.value, note: note.value.trim() || null });
}
</script>

<style scoped>
.status-actions {
  display: grid;
  gap: 0;
}

.status-actions__demo {
  margin: 0 0 var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.status-actions__form {
  display: grid;
  gap: var(--space-4);
}

fieldset {
  padding: 0;
  border: 0;
  margin: 0;
  min-width: 0;
}

legend {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: var(--space-2);
  float: none;
  width: 100%;
  padding: 0;
}

/* ─── Options ─── */
.status-actions__options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* Per-status color tokens */
.status-actions__option--new         { --c: #6b7280; }
.status-actions__option--verified    { --c: #0ea5e9; }
.status-actions__option--assigned    { --c: #16a34a; }
.status-actions__option--in_progress { --c: #f59e0b; }
.status-actions__option--resolved    { --c: #059669; }
.status-actions__option--rejected    { --c: #ef4444; }

.status-actions__option {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.4rem;
  padding: 0 1.2rem;
  border: 1.5px solid color-mix(in srgb, var(--c) 30%, transparent);
  border-radius: var(--radius-pill);
  background: color-mix(in srgb, var(--c) 8%, rgba(255, 253, 247, 0.6));
  color: var(--c);
  font-size: var(--text-sm);
  font-weight: 850;
  letter-spacing: 0.01em;
  cursor: pointer;
  user-select: none;
  transition:
    background var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease,
    transform var(--motion-fast) var(--ease-out-expo),
    color var(--motion-fast) ease;
}

.status-actions__option input[type="radio"] {
  display: none;
}

.status-actions__option:hover {
  background: color-mix(in srgb, var(--c) 15%, rgba(255, 253, 247, 0.9));
  border-color: color-mix(in srgb, var(--c) 55%, transparent);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--c) 16%, transparent);
}

.status-actions__option--selected {
  background: var(--c);
  border-color: var(--c);
  color: #fff;
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--c) 22%, transparent),
    0 6px 20px color-mix(in srgb, var(--c) 32%, transparent);
  transform: translateY(-1px);
}

.status-actions__option--selected:hover {
  background: color-mix(in srgb, var(--c) 88%, #000);
  border-color: color-mix(in srgb, var(--c) 88%, #000);
}

/* ─── API error ─── */
.status-actions__api-error {
  margin: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(200, 76, 58, 0.07);
  border: 1px solid rgba(200, 76, 58, 0.2);
  color: var(--color-repair-red);
  font-size: var(--text-xs);
  line-height: 1.5;
}
</style>
