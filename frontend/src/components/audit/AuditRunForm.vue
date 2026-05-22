<template>
  <section class="audit-run-form">
    <form class="audit-run-form__form" @submit.prevent="submit">
      <AppField label="Municipality">
        <AppInput
          v-model="municipality"
          aria-label="Municipality"
          :disabled="isCreating"
          placeholder="Prizren"
        />
      </AppField>

      <LocationSearchField
        v-model:latitude="selectedLatitude"
        v-model:longitude="selectedLongitude"
        v-model:location-label="selectedLabel"
        label="Route or location"
        placeholder="Search streets, landmarks, or neighborhoods in Prizren"
        :disabled="isCreating"
        hint=""
      />

      <div class="audit-run-form__gps-row">
        <GpsLocateButton :disabled="isCreating" @located="onGpsLocated" />
      </div>

      <AppField label="Notes">
        <AppTextarea
          v-model="notes"
          aria-label="Audit notes"
          :disabled="isCreating"
          :maxlength="1000"
          placeholder="Optional context for reviewers."
        />
      </AppField>

      <div v-if="error" class="audit-run-form__error glass-panel">
        <AppBadge tone="danger">Create failed</AppBadge>
        <p>{{ error }}</p>
      </div>

      <AppButton :disabled="isCreating || !canSubmit" type="submit">
        {{ isCreating ? 'Creating…' : 'Start audit run' }}
      </AppButton>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppField from '@/components/common/AppField.vue';
import AppInput from '@/components/common/AppInput.vue';
import AppTextarea from '@/components/common/AppTextarea.vue';
import GpsLocateButton from '@/components/maps/GpsLocateButton.vue';
import LocationSearchField from '@/components/maps/LocationSearchField.vue';
import type { AuditRunCreatePayload } from '@/types/audit';
import { snapToStreetViewAtCoordinates } from '@/utils/streetView';

const props = defineProps<{
  isCreating: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  create: [payload: AuditRunCreatePayload];
}>();

const municipality = ref('Prizren');
const selectedLatitude = ref<number | null>(null);
const selectedLongitude = ref<number | null>(null);
const selectedLabel = ref<string | null>(null);
const notes = ref('');

const hasCoordinates = computed(
  () =>
    selectedLatitude.value !== null &&
    selectedLongitude.value !== null &&
    selectedLatitude.value >= -90 &&
    selectedLatitude.value <= 90 &&
    selectedLongitude.value >= -180 &&
    selectedLongitude.value <= 180,
);

const hasRoute = computed(() => Boolean(selectedLabel.value?.trim()));
const canSubmit = computed(
  () => municipality.value.trim().length > 0 && hasRoute.value && hasCoordinates.value,
);

function onGpsLocated(payload: {
  latitude: number;
  longitude: number;
  label: string;
}) {
  void applyLocatedSelection(payload);
}

async function applyLocatedSelection(payload: {
  latitude: number;
  longitude: number;
  label: string;
}) {
  const snapped = await snapToStreetViewAtCoordinates(payload.latitude, payload.longitude);
  selectedLatitude.value = snapped?.latitude ?? payload.latitude;
  selectedLongitude.value = snapped?.longitude ?? payload.longitude;
  selectedLabel.value = snapped?.description?.trim() || payload.label;
}

function submit() {
  if (!canSubmit.value || props.isCreating) {
    return;
  }

  emit('create', {
    municipality: municipality.value.trim(),
    route_name: selectedLabel.value?.trim() ?? null,
    latitude: selectedLatitude.value,
    longitude: selectedLongitude.value,
    notes: notes.value.trim() ? notes.value.trim() : null,
  });
}
</script>

<style scoped>
.audit-run-form h2 {
  margin: 0;
}

.audit-run-form__form {
  display: grid;
  gap: var(--space-4);
}

.audit-run-form__gps-row {
  display: flex;
  justify-content: center;
  padding: var(--space-1) 0 var(--space-2);
}

.audit-run-form__error {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-4);
}

.audit-run-form__error p {
  color: var(--text-secondary);
}
</style>
