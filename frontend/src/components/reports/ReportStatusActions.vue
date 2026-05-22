<template>
  <AppCard class="status-actions stack" variant="inset">
    <div class="cluster-between">
      <div>
        <p class="eyebrow">Workflow controls</p>
        <h3>Update municipal status</h3>
      </div>
      <StatusPill :status="currentStatus" />
    </div>

    <p v-if="isDemoData" class="muted">Demo record — changes are not persisted.</p>

    <AppEmptyState
      v-if="allowedStatuses.length === 0"
      tone="dashboard"
      title="No next status available"
      description="This report has no configured next workflow step from its current status."
    />

    <form v-else class="status-actions__form" @submit.prevent="submit">
      <fieldset>
        <legend>Next status</legend>
        <div class="status-actions__options">
          <label
            v-for="status in allowedStatuses"
            :key="status"
            class="status-actions__option"
            :class="{ 'status-actions__option--selected': nextStatus === status }"
          >
            <input v-model="nextStatus" :value="status" name="next-status" type="radio" />
            <StatusPill :status="status" />
          </label>
        </div>
      </fieldset>

      <AppField
        label="Municipal note"
        :helper="noteHelper"
        :error="localError"
      >
        <AppTextarea
          v-model="note"
          aria-label="Municipal workflow note"
          :disabled="isUpdating"
          :maxlength="1000"
          placeholder="Add a concise review, resolution, or rejection note."
        />
      </AppField>

      <AppCard v-if="error" class="status-actions__error" variant="muted">
        <AppBadge tone="danger">Backend workflow unavailable</AppBadge>
        <p>{{ error }}</p>
      </AppCard>

      <AppButton :disabled="isDemoData || isUpdating || !nextStatus" type="submit">
        {{ isUpdating ? 'Updating status...' : 'Send status update' }}
      </AppButton>
    </form>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppField from '@/components/common/AppField.vue';
import AppTextarea from '@/components/common/AppTextarea.vue';
import StatusPill from './StatusPill.vue';
import type { ReportStatusUpdatePayload, TicketStatus } from '@/types/report';
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
  if (props.isDemoData) {
    return;
  }

  submitted.value = true;

  if (!nextStatus.value) {
    return;
  }

  if (requiresWorkflowNote(nextStatus.value) && !note.value.trim()) {
    return;
  }

  emit('update', {
    status: nextStatus.value,
    note: note.value.trim() || null,
  });
}
</script>

<style scoped>
.status-actions h3,
.status-actions p {
  margin: 0;
}

.status-actions p {
  color: var(--text-secondary);
}

.status-actions code {
  color: var(--text-primary);
  font-weight: 850;
}

.status-actions__form {
  display: grid;
  gap: var(--space-4);
}

fieldset {
  display: grid;
  gap: var(--space-3);
  min-width: 0;
  padding: 0;
  border: 0;
  margin: 0;
}

legend {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.status-actions__options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.status-actions__option {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 2.75rem;
  padding: 0 var(--space-3);
  border: var(--border-soft);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.62);
  cursor: pointer;
}

.status-actions__option--selected {
  border-color: rgba(47, 93, 80, 0.42);
  background: rgba(221, 232, 213, 0.58);
}

.status-actions__option input {
  accent-color: var(--action-primary);
}

.status-actions__error {
  display: grid;
  gap: var(--space-2);
}
</style>
