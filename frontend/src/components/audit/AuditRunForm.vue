<template>
  <AppCard class="audit-run-form stack" variant="command">
    <div>
      <p class="eyebrow">Create audit run</p>
      <h2>Start a backend street-audit job</h2>
      <p>
        The frontend submits the route request. Backend orchestration and the AI pipeline own imagery
        retrieval, model inference, and status progression.
      </p>
    </div>

    <form class="audit-run-form__form" @submit.prevent="submit">
      <AppField label="Municipality">
        <AppInput
          v-model="municipality"
          aria-label="Municipality"
          :disabled="isCreating"
          placeholder="Prishtina"
        />
      </AppField>

      <AppField label="Route or segment name">
        <AppInput
          v-model="routeName"
          aria-label="Route or segment name"
          :disabled="isCreating"
          placeholder="Bill Clinton Boulevard demo segment"
        />
      </AppField>

      <AppField label="Notes">
        <AppTextarea
          v-model="notes"
          aria-label="Audit notes"
          :disabled="isCreating"
          :maxlength="1000"
          placeholder="Optional context for the backend and AI team."
        />
      </AppField>

      <AppCard v-if="error" class="audit-run-form__error" variant="inset">
        <AppBadge tone="danger">Create failed</AppBadge>
        <p>{{ error }}</p>
      </AppCard>

      <AppButton :disabled="isCreating || !canSubmit" type="submit">
        {{ isCreating ? 'Creating run...' : 'Create audit run' }}
      </AppButton>
    </form>
  </AppCard>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppField from '@/components/common/AppField.vue';
import AppInput from '@/components/common/AppInput.vue';
import AppTextarea from '@/components/common/AppTextarea.vue';
import type { AuditRunCreatePayload } from '@/types/audit';

const props = defineProps<{
  isCreating: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  create: [payload: AuditRunCreatePayload];
}>();

const municipality = ref('Prishtina');
const routeName = ref('');
const notes = ref('');

const canSubmit = computed(() => municipality.value.trim().length > 0 && routeName.value.trim().length > 0);

function submit() {
  if (!canSubmit.value || props.isCreating) {
    return;
  }

  emit('create', {
    municipality: municipality.value.trim(),
    route_name: routeName.value.trim(),
    notes: notes.value.trim() ? notes.value.trim() : null,
  });
}
</script>

<style scoped>
.audit-run-form h2,
.audit-run-form p {
  margin: 0;
}

.audit-run-form p {
  color: var(--text-secondary);
}

.audit-run-form__form {
  display: grid;
  gap: var(--space-4);
}

.audit-run-form__error {
  display: grid;
  gap: var(--space-2);
}
</style>
