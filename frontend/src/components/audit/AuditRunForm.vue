<template>
  <section class="audit-run-form audit-run-form--launch">
    <form class="filter-bar audit-launch-bar" aria-label="Start street audit scan" @submit.prevent="submit">
      <div class="filter-bar__search-wrap audit-launch-bar__search">
        <svg class="filter-bar__search-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="6.5" cy="6.5" r="4" stroke="currentColor" stroke-width="1.4" />
          <path d="M10 10l3 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
        </svg>
        <LocationSearchField
          v-model:latitude="selectedLatitude"
          v-model:longitude="selectedLongitude"
          v-model:location-label="selectedLabel"
          variant="embedded"
          label=""
          placeholder="Search route to scan…"
          :disabled="isCreating"
          hint=""
        />
      </div>

      <span class="filter-bar__divider" aria-hidden="true" />

      <GpsLocateButton compact :disabled="isCreating" @located="onGpsLocated" />

      <button
        class="audit-launch-bar__submit"
        type="submit"
        :disabled="isCreating || !canSubmit"
      >
        {{ isCreating ? 'Starting…' : 'Start scan' }}
      </button>

      <p v-if="error" class="audit-launch-bar__error">{{ error }}</p>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
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
    municipality: 'Kosovo',
    route_name: selectedLabel.value?.trim() ?? null,
    latitude: selectedLatitude.value,
    longitude: selectedLongitude.value,
    notes: null,
  });
}
</script>

<style scoped>
.audit-run-form--launch {
  overflow: visible;
}

.filter-bar {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  padding: 0.32rem 0.5rem 0.32rem 0.32rem;
  border: 1px solid rgba(23, 33, 26, 0.09);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.6);
  backdrop-filter: blur(14px);
  width: fit-content;
  max-width: 100%;
  overflow: visible;
}

.audit-launch-bar__search {
  flex: 1 1 16rem;
  min-width: min(100%, 14rem);
}

.filter-bar__search-wrap {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  overflow: visible;
}

.filter-bar__search-icon {
  position: absolute;
  left: 0.65rem;
  z-index: 1;
  width: 13px;
  height: 13px;
  color: var(--text-muted);
  pointer-events: none;
  flex-shrink: 0;
}

.audit-launch-bar__search :deep(.location-search) {
  flex: 1;
  min-width: 0;
}

.audit-launch-bar__search :deep(.location-search__shell--embedded) {
  padding-left: 2rem;
}

.filter-bar__divider {
  display: block;
  width: 1px;
  height: 1.25rem;
  background: rgba(23, 33, 26, 0.1);
  flex-shrink: 0;
  margin: 0 0.1rem;
}

.audit-launch-bar__submit {
  height: 2rem;
  padding: 0 0.9rem;
  border: none;
  border-radius: var(--radius-pill);
  background: var(--color-municipal-green);
  color: #fff;
  font-size: var(--text-sm);
  font-weight: 800;
  cursor: pointer;
  flex-shrink: 0;
  transition:
    background var(--motion-fast) ease,
    opacity var(--motion-fast) ease,
    transform var(--motion-fast) ease;
}

.audit-launch-bar__submit:hover:not(:disabled) {
  transform: translateY(-1px);
  background: color-mix(in srgb, var(--color-municipal-green) 88%, #000);
}

.audit-launch-bar__submit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.audit-launch-bar__error {
  flex: 1 1 100%;
  margin: 0.15rem 0 0 0.35rem;
  color: var(--color-repair-red);
  font-size: var(--text-xs);
  font-weight: 700;
}

@media (max-width: 760px) {
  .filter-bar {
    width: 100%;
    border-radius: var(--radius-lg);
  }
}

@media (max-width: 640px) {
  .filter-bar {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.4rem;
    width: 100%;
    padding: 0.5rem;
  }

  .audit-launch-bar__search {
    width: 100%;
    min-width: 0;
  }

  .filter-bar__search-wrap {
    width: 100%;
  }

  .filter-bar__divider {
    display: none;
  }

  .audit-launch-bar__submit {
    width: 100%;
    height: 2.45rem;
    justify-self: stretch;
  }
}
</style>
