<template>
  <CitizenLayout>
    <PageHero
      align="center"
      eyebrow="Citizen report"
      title="Report a street issue"
      description="Photo, location, category — submit in under a minute."
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

        <IssueCategorySelector v-else-if="activeStep === 'category'" key="category" v-model="draft.category" />

        <div v-else key="review" class="report-wizard__review stack-lg">
          <AppCard variant="inset" class="description-card stack">
            <div class="cluster-between">
              <div>
                <h2>Add a note</h2>
                <p class="muted">Optional context for municipal staff.</p>
              </div>
              <AppBadge :tone="description.length > maxDescriptionLength ? 'danger' : 'neutral'">
                {{ description.length }}/{{ maxDescriptionLength }}
              </AppBadge>
            </div>
            <AppTextarea
              v-model="description"
              :maxlength="maxDescriptionLength"
              aria-label="Issue description"
              placeholder="Lane, landmark, urgency…"
            />
          </AppCard>

          <ReportReviewCard
            :can-submit="canSubmit"
            :draft="draft"
            :error="submitError"
            :is-submitting="isSubmitting"
            @submit="submitReport"
          />
        </div>
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
  </CitizenLayout>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import GlassPanel from '@/components/common/GlassPanel.vue';
import PageHero from '@/components/common/PageHero.vue';
import AppTextarea from '@/components/common/AppTextarea.vue';
import IssueCategorySelector from '@/components/reports/IssueCategorySelector.vue';
import LocationCaptureField from '@/components/reports/LocationCaptureField.vue';
import PhotoCaptureField from '@/components/reports/PhotoCaptureField.vue';
import ReportProgress, { type ReportStep } from '@/components/reports/ReportProgress.vue';
import ReportReviewCard from '@/components/reports/ReportReviewCard.vue';
import { analyzeReportImage, createReport } from '@/api/reports';
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
const activeStep = ref<'photo' | 'location' | 'category' | 'review'>('photo');

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

  if (!file) {
    draft.isAnalyzingImage = false;
    return;
  }

  draft.isAnalyzingImage = true;
  try {
    const analysis = await analyzeReportImage(file);
    draft.imageAnalysis = analysis;
    if (analysis.category && !draft.category) {
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
const canSubmit = computed(
  () => Boolean(draft.category) && hasValidLocation.value && hasValidDescription.value,
);

const completedSteps = computed(() => {
  const completed: string[] = [];
  if (draft.imageFile) completed.push('photo');
  if (hasValidLocation.value) completed.push('location');
  if (draft.category) completed.push('category');
  if (canSubmit.value) completed.push('review');
  return completed;
});

const canAdvance = computed(() => {
  if (activeStep.value === 'photo') return true;
  if (activeStep.value === 'location') return hasValidLocation.value;
  if (activeStep.value === 'category') return Boolean(draft.category);
  return false;
});

function goToStep(stepId: string) {
  if (stepId === 'photo' || stepId === 'location' || stepId === 'category' || stepId === 'review') {
    activeStep.value = stepId;
  }
}

function goNext() {
  if (activeStep.value === 'photo') activeStep.value = 'location';
  else if (activeStep.value === 'location') activeStep.value = 'category';
  else if (activeStep.value === 'category') activeStep.value = 'review';
}

function goBack() {
  if (activeStep.value === 'location') activeStep.value = 'photo';
  else if (activeStep.value === 'category') activeStep.value = 'location';
  else if (activeStep.value === 'review') activeStep.value = 'category';
}

async function submitReport() {
  if (!canSubmit.value || !draft.category || draft.latitude === null || draft.longitude === null) {
    submitError.value = 'Complete category and location before submitting.';
    return;
  }

  isSubmitting.value = true;
  submitError.value = null;

  try {
    const report = await createReport(
      {
        category: draft.category,
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
.report-wizard-shell {
  display: grid;
  gap: var(--space-5);
  max-width: 48rem;
  margin: 0 auto;
}

.report-wizard {
  min-height: 18rem;
}

.report-wizard__nav {
  padding-top: var(--space-2);
}

.description-card h2 {
  margin: 0;
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
</style>
