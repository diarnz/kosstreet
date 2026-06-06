<template>
  <CitizenLayout>
    <div class="report-page">
      <div class="report-page__stack">
        <PageHero
          align="center"
          eyebrow="Citizen report"
          title="Report a street issue"
          description="Snap a photo, pin the location — AI handles the rest."
        />

        <ReportProgress
          :completed-steps="completedSteps"
          :current-step="activeStep"
          :steps="steps"
          @navigate="goToStep"
        />

        <GlassPanel class="report-wizard-shell animate-fade-in" elevated padding="lg">
          <div class="report-wizard">
            <Transition name="step" mode="out-in">
              <PhotoCaptureField
                v-if="activeStep === 'photo'"
                key="photo"
                v-model="imageFile"
                :analysis="draft.imageAnalysis"
                :analysis-error="draft.imageAnalysisError"
                :is-analyzing="draft.isAnalyzingImage"
              />

              <LocationCaptureField
                v-else-if="activeStep === 'location'"
                key="location"
                v-model:accuracy="draft.locationAccuracy"
                v-model:latitude="draft.latitude"
                v-model:location-label="draft.locationLabel"
                v-model:longitude="draft.longitude"
              />

              <ReportReviewCard
                v-else
                key="review"
                :can-submit="canSubmit"
                :description="description"
                :draft="draft"
                :error="submitError"
                :is-submitting="isSubmitting"
                :max-description-length="maxDescriptionLength"
                @submit="submitReport"
                @update:description="description = $event"
              />
            </Transition>
          </div>

          <div v-if="activeStep !== 'review'" class="report-wizard__nav cluster-between">
            <AppButton :disabled="activeStep === 'photo'" variant="secondary" @click="goBack">
              Back
            </AppButton>
            <AppButton :disabled="!canAdvance" @click="goNext">
              Continue
            </AppButton>
          </div>
        </GlassPanel>
      </div>
    </div>
  </CitizenLayout>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import AppButton from '@/components/common/AppButton.vue';
import GlassPanel from '@/components/common/GlassPanel.vue';
import PageHero from '@/components/common/PageHero.vue';
import LocationCaptureField from '@/components/reports/LocationCaptureField.vue';
import PhotoCaptureField from '@/components/reports/PhotoCaptureField.vue';
import ReportProgress, { type ReportStep } from '@/components/reports/ReportProgress.vue';
import ReportReviewCard from '@/components/reports/ReportReviewCard.vue';
import { analyzeReportImage, createReport } from '@/api/reports';
import CitizenLayout from '@/layouts/CitizenLayout.vue';
import { useImagePreview } from '@/composables/useImagePreview';
import type { IssueCategory } from '@/types/report';
import type { ReportDraft } from '@/types/reportDraft';

const router = useRouter();
const maxDescriptionLength = 1000;

const imageFile = ref<File | null>(null);
const { previewUrl } = useImagePreview(imageFile);
const description = ref('');
const isSubmitting = ref(false);
const submitError = ref<string | null>(null);
const activeStep = ref<'photo' | 'location' | 'review'>('photo');

const draft = reactive<ReportDraft>({
  imageFile: null,
  imagePreviewUrl: null,
  category: null,
  latitude: null,
  longitude: null,
  locationAccuracy: null,
  locationLabel: null,
  description: '',
  aiSuggestion: null,
  imageAnalysis: null,
  isAnalyzingImage: false,
  imageAnalysisError: null,
});

watch(imageFile, async (file) => {
  draft.imageFile = file;
  draft.imageAnalysis = null;
  draft.imageAnalysisError = null;
  draft.category = null;

  if (!file) {
    draft.isAnalyzingImage = false;
    return;
  }

  draft.isAnalyzingImage = true;
  try {
    const analysis = await analyzeReportImage(file);
    draft.imageAnalysis = analysis;
    if (analysis.category) {
      draft.category = analysis.category;
    }
    if (analysis.description && !description.value.trim()) {
      description.value = analysis.description;
    }
  } catch (error) {
    draft.imageAnalysisError =
      error instanceof Error ? error.message : 'Could not analyze the photo.';
  } finally {
    draft.isAnalyzingImage = false;
  }
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

const resolvedCategory = computed(
  (): IssueCategory | null => draft.imageAnalysis?.category ?? draft.category,
);

const canSubmit = computed(
  () => hasValidLocation.value && hasValidDescription.value && !draft.isAnalyzingImage,
);

const completedSteps = computed(() => {
  const completed: string[] = [];
  if (draft.imageFile) completed.push('photo');
  if (hasValidLocation.value) completed.push('location');
  if (canSubmit.value) completed.push('review');
  return completed;
});

const canAdvance = computed(() => {
  if (activeStep.value === 'photo') return true;
  if (activeStep.value === 'location') return hasValidLocation.value;
  return false;
});

function goToStep(stepId: string) {
  if (stepId === 'photo' || stepId === 'location' || stepId === 'review') {
    activeStep.value = stepId;
  }
}

function goNext() {
  if (activeStep.value === 'photo') activeStep.value = 'location';
  else if (activeStep.value === 'location') activeStep.value = 'review';
}

function goBack() {
  if (activeStep.value === 'location') activeStep.value = 'photo';
  else if (activeStep.value === 'review') activeStep.value = 'location';
}

async function submitReport() {
  const category = resolvedCategory.value ?? 'other';

  if (!hasValidLocation.value || draft.latitude === null || draft.longitude === null) {
    submitError.value = 'Add a location before submitting.';
    return;
  }

  if (draft.isAnalyzingImage) {
    submitError.value = 'Wait for AI photo analysis to finish.';
    return;
  }

  isSubmitting.value = true;
  submitError.value = null;

  try {
    const report = await createReport(
      {
        category,
        latitude: draft.latitude,
        longitude: draft.longitude,
        source: 'citizen',
        description: description.value.trim() || draft.imageAnalysis?.description || undefined,
        confidence: draft.imageAnalysis?.confidence ?? undefined,
        severity: draft.imageAnalysis?.severity ?? undefined,
        detection_regions: draft.imageAnalysis?.regions ?? [],
      },
      draft.imageFile,
    );

    await router.push({ name: 'report-status', params: { id: report.id } });
  } catch (error) {
    submitError.value =
      error instanceof Error ? error.message : 'Could not submit the report. Try again.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.report-page {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: calc(100dvh - clamp(6rem, 14vw, 9rem));
  padding-block: var(--space-4);
}

.report-page__stack {
  display: grid;
  gap: var(--space-4);
  width: 100%;
  max-width: 32rem;
  margin-inline: auto;
}

.report-page__stack :deep(.page-hero) {
  padding-bottom: 0;
  border-bottom: 0;
}

.report-wizard-shell {
  display: grid;
  gap: var(--space-5);
  width: 100%;
}

.report-wizard {
  min-height: 14rem;
}

.report-wizard__nav {
  padding-top: var(--space-2);
}

.step-enter-active,
.step-leave-active {
  transition:
    opacity var(--motion-base) var(--ease-out-expo),
    transform var(--motion-base) var(--ease-out-expo);
}

.step-enter-from {
  opacity: 0;
  transform: translateX(16px);
}

.step-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}

@media (max-width: 640px) {
  .report-page {
    align-items: flex-start;
    justify-content: flex-start;
    min-height: calc(100dvh - clamp(5.5rem, 20vw, 8.5rem));
    padding:
      max(var(--space-2), env(safe-area-inset-top, 0px))
      max(var(--space-3), env(safe-area-inset-right, 0px))
      max(calc(clamp(5rem, 10vw, 7rem) + env(safe-area-inset-bottom, 0px)), var(--space-4))
      max(var(--space-3), env(safe-area-inset-left, 0px));
  }

  .report-page__stack {
    gap: var(--space-3);
    max-width: none;
  }

  .report-page__stack :deep(.page-hero__title) {
    font-size: clamp(1.55rem, 7.5vw, 2rem);
  }

  .report-page__stack :deep(.page-hero__description) {
    padding-inline: var(--space-1);
    font-size: var(--text-sm);
    line-height: 1.5;
  }

  .report-wizard-shell {
    gap: var(--space-4);
  }

  .report-wizard {
    min-height: 11rem;
  }

  .report-wizard__nav {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-2);
    padding-top: var(--space-1);
  }

  .report-wizard__nav :deep(.app-button) {
    width: 100%;
    min-height: 2.75rem;
  }
}
</style>
