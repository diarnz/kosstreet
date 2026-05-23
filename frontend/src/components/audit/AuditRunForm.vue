<template>
  <section class="audit-run-form">
    <form class="audit-run-form__form" @submit.prevent="submit">
      <div class="audit-run-form__search-row">
        <LocationSearchField
          v-model:latitude="selectedLatitude"
          v-model:longitude="selectedLongitude"
          v-model:location-label="selectedLabel"
          label=""
          placeholder="Search streets, landmarks, or neighborhoods…"
          :disabled="isCreating"
          hint=""
        />
        <GpsLocateButton :disabled="isCreating" @located="onGpsLocated" />
      </div>

      <div v-if="error" class="audit-run-form__error">
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
import AppButton from '@/components/common/AppButton.vue';
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

const selectedLatitude = ref<number | null>(null);
const selectedLongitude = ref<number | null>(null);
const selectedLabel = ref<string | null>(null);

const hasCoordinates = computed(
  () =>
    selectedLatitude.value !== null &&
    selectedLongitude.value !== null &&
    selectedLatitude.value >= -90 &&
    selectedLatitude.value <= 90 &&
    selectedLongitude.value >= -180 &&
    selectedLongitude.value <= 180,
);

const canSubmit = computed(
  () => Boolean(selectedLabel.value?.trim()) && hasCoordinates.value,
);

function onGpsLocated(payload: { latitude: number; longitude: number; accuracy: number; label: string }) {
  void applyLocatedSelection(payload);
}

async function applyLocatedSelection(payload: { latitude: number; longitude: number; label: string }) {
  const snapped = await snapToStreetViewAtCoordinates(payload.latitude, payload.longitude);
  selectedLatitude.value = snapped?.latitude ?? payload.latitude;
  selectedLongitude.value = snapped?.longitude ?? payload.longitude;
  selectedLabel.value = snapped?.description?.trim() || payload.label;
}

function submit() {
  if (!canSubmit.value || props.isCreating) return;
  emit('create', {
    municipality: 'Prizren',
    route_name: selectedLabel.value?.trim() ?? null,
    latitude: selectedLatitude.value,
    longitude: selectedLongitude.value,
    notes: null,
  });
}
</script>

<style scoped>
.audit-run-form__form {
  display: grid;
  gap: var(--space-3);
}

.audit-run-form__search-row {
  display: flex;
  gap: var(--space-2);
  align-items: flex-end;
}

.audit-run-form__search-row > :first-child {
  flex: 1;
  min-width: 0;
}

.audit-run-form__error {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(200, 76, 58, 0.07);
  border: 1px solid rgba(200, 76, 58, 0.2);
}

.audit-run-form__error p {
  margin: 0;
  color: var(--color-repair-red);
  font-size: var(--text-sm);
}
</style>
