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
          placeholder="Bill Clinton Boulevard, or leave empty if using coordinates"
        />
      </AppField>

      <div class="audit-run-form__coordinate-grid">
        <AppField label="Latitude">
          <AppInput
            v-model="latitude"
            aria-label="Audit latitude"
            :disabled="isCreating"
            placeholder="42.6596"
          />
        </AppField>

        <AppField label="Longitude">
          <AppInput
            v-model="longitude"
            aria-label="Audit longitude"
            :disabled="isCreating"
            placeholder="21.1545"
          />
        </AppField>
      </div>

      <p class="audit-run-form__hint">
        Use either a route name or both coordinates. Coordinate audits scan that exact point across
        the configured Street View headings.
      </p>

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
const latitude = ref('');
const longitude = ref('');
const notes = ref('');

const parsedLatitude = computed(() => Number(latitude.value.trim()));
const parsedLongitude = computed(() => Number(longitude.value.trim()));
const hasRoute = computed(() => routeName.value.trim().length > 0);
const hasCoordinates = computed(
  () =>
    latitude.value.trim().length > 0 &&
    longitude.value.trim().length > 0 &&
    Number.isFinite(parsedLatitude.value) &&
    Number.isFinite(parsedLongitude.value) &&
    parsedLatitude.value >= -90 &&
    parsedLatitude.value <= 90 &&
    parsedLongitude.value >= -180 &&
    parsedLongitude.value <= 180,
);
const canSubmit = computed(() => municipality.value.trim().length > 0 && (hasRoute.value || hasCoordinates.value));

function submit() {
  if (!canSubmit.value || props.isCreating) {
    return;
  }

  emit('create', {
    municipality: municipality.value.trim(),
    route_name: hasRoute.value ? routeName.value.trim() : null,
    latitude: hasCoordinates.value ? parsedLatitude.value : null,
    longitude: hasCoordinates.value ? parsedLongitude.value : null,
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

.audit-run-form__coordinate-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.audit-run-form__hint {
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.audit-run-form__error {
  display: grid;
  gap: var(--space-2);
}

@media (max-width: 620px) {
  .audit-run-form__coordinate-grid {
    grid-template-columns: 1fr;
  }
}
</style>
