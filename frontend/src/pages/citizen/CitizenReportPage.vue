<template>
  <CitizenLayout>
    <AppSectionHeader
      eyebrow="Citizen Flow"
      title="Report a street issue"
      description="Create a structured, geolocated civic issue report for Prishtina municipal review."
    />

    <ReportProgress :completed-steps="completedSteps" :current-step="currentStep" :steps="steps" />

    <PhotoCaptureField v-model="imageFile" />

    <LocationCaptureField
      v-model:accuracy="draft.locationAccuracy"
      v-model:latitude="draft.latitude"
      v-model:longitude="draft.longitude"
    />

    <IssueCategorySelector v-model="draft.category" />

    <AppCard variant="inset" class="description-card stack">
      <div class="cluster-between">
        <div>
          <h2>Description</h2>
          <p>Add context such as lane, nearby landmark, or urgency.</p>
        </div>
        <AppBadge :tone="description.length > maxDescriptionLength ? 'danger' : 'neutral'">
          {{ description.length }}/{{ maxDescriptionLength }}
        </AppBadge>
      </div>
      <AppTextarea
        v-model="description"
        :maxlength="maxDescriptionLength"
        aria-label="Issue description"
        placeholder="Example: Large pothole near the right lane, close to the bus stop."
      />
    </AppCard>

    <ReportReviewCard
      :can-submit="canSubmit"
      :draft="draft"
      :error="submitError"
      :is-submitting="isSubmitting"
      @submit="submitReport"
    />

    <AppCard variant="inset" class="trust-note">
      <AppBadge tone="info">Citizen trust note</AppBadge>
      <p>
        The selected image is previewed locally only. It is not uploaded until a backend image
        endpoint is connected. The structured report data is submitted now.
      </p>
    </AppCard>
  </CitizenLayout>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AppTextarea from '@/components/common/AppTextarea.vue';
import IssueCategorySelector from '@/components/reports/IssueCategorySelector.vue';
import LocationCaptureField from '@/components/reports/LocationCaptureField.vue';
import PhotoCaptureField from '@/components/reports/PhotoCaptureField.vue';
import ReportProgress, { type ReportStep } from '@/components/reports/ReportProgress.vue';
import ReportReviewCard from '@/components/reports/ReportReviewCard.vue';
import { createReport } from '@/api/reports';
import CitizenLayout from '@/layouts/CitizenLayout.vue';
import { useImagePreview } from '@/composables/useImagePreview';
import type { ReportDraft } from '@/types/reportDraft';

const router = useRouter();
const maxDescriptionLength = 1000;

const imageFile = ref<File | null>(null);
const { previewUrl } = useImagePreview(imageFile);
const description = ref('');
const isSubmitting = ref(false);
const submitError = ref<string | null>(null);

const draft = reactive<ReportDraft>({
  imageFile: null,
  imagePreviewUrl: null,
  category: null,
  latitude: null,
  longitude: null,
  locationAccuracy: null,
  description: '',
  aiSuggestion: null,
});

watch(imageFile, (file) => {
  draft.imageFile = file;
});

watch(previewUrl, (url) => {
  draft.imagePreviewUrl = url;
});

watch(description, (value) => {
  draft.description = value;
});

const steps: ReportStep[] = [
  { id: 'photo', label: 'Photo' },
  { id: 'location', label: 'Location' },
  { id: 'category', label: 'Category' },
  { id: 'review', label: 'Review' },
];

const hasValidLatitude = computed(
  () => draft.latitude !== null && draft.latitude >= -90 && draft.latitude <= 90,
);
const hasValidLongitude = computed(
  () => draft.longitude !== null && draft.longitude >= -180 && draft.longitude <= 180,
);
const hasValidLocation = computed(() => hasValidLatitude.value && hasValidLongitude.value);
const hasValidDescription = computed(() => description.value.length <= maxDescriptionLength);
const canSubmit = computed(() => Boolean(draft.category) && hasValidLocation.value && hasValidDescription.value);

const completedSteps = computed(() => {
  const completed: string[] = [];
  if (draft.imageFile) completed.push('photo');
  if (hasValidLocation.value) completed.push('location');
  if (draft.category) completed.push('category');
  if (canSubmit.value) completed.push('review');
  return completed;
});

const currentStep = computed(() => {
  if (!draft.imageFile) return 'photo';
  if (!hasValidLocation.value) return 'location';
  if (!draft.category) return 'category';
  return 'review';
});

async function submitReport() {
  if (!canSubmit.value || !draft.category || draft.latitude === null || draft.longitude === null) {
    submitError.value = 'Please complete the required category and location fields.';
    return;
  }

  isSubmitting.value = true;
  submitError.value = null;

  try {
    const report = await createReport({
      category: draft.category,
      latitude: draft.latitude,
      longitude: draft.longitude,
      source: 'citizen',
      description: description.value.trim() || undefined,
    });

    await router.push({ name: 'report-status', params: { id: report.id } });
  } catch (error) {
    submitError.value =
      error instanceof Error
        ? error.message
        : 'Could not submit the report. Check the connection and try again.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
h2 {
  margin: 0;
}

.description-card p,
.trust-note p {
  color: var(--text-secondary);
}

.description-card,
.trust-note {
  display: grid;
  gap: var(--space-3);
}
</style>
