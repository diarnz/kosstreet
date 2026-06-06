<template>
  <section class="audit-frame-browser">
    <div class="audit-frame-browser__header">
      <span class="audit-frame-browser__label">Detected issues</span>
      <AppBadge tone="source-ai-audit" size="xs">{{ issueFrames.length }}</AppBadge>
    </div>

    <AppCard v-if="error" class="stack" variant="muted">
      <AppBadge tone="danger">Could not load frames</AppBadge>
      <p>{{ error }}</p>
      <AppButton variant="secondary" @click="$emit('refresh')">Retry</AppButton>
    </AppCard>

    <AppLoading v-else-if="isLoading" label="Loading detections" />

    <AppEmptyState
      v-else-if="!issueFrames.length"
      description="No street issues were flagged in this audit run."
      title="All clear"
      tone="audit"
    />

    <div v-else class="audit-frame-browser__grid" role="list">
      <button
        v-for="frame in issueFrames"
        :key="frame.frame_index"
        class="audit-frame-browser__card"
        :class="`audit-frame-browser__card--${frame.severity ?? 'medium'}`"
        type="button"
        role="listitem"
        @click="openFrame(frame.frame_index)"
      >
        <div class="audit-frame-browser__card-media">
          <img
            :src="resolveApiAssetUrl(frame.frame_image_url)"
            :alt="`${frame.category ?? 'Issue'} frame ${frame.frame_index + 1}`"
            loading="lazy"
          />
          <span class="audit-frame-browser__expand" aria-hidden="true">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
              <path d="M9 3H5a2 2 0 00-2 2v4M15 3h4a2 2 0 012 2v4M9 21H5a2 2 0 01-2-2v-4M15 21h4a2 2 0 002-2v-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </span>
        </div>
        <div class="audit-frame-browser__card-body">
          <strong>{{ frame.category ? categoryLabels[frame.category] : 'Issue' }}</strong>
          <span class="audit-frame-browser__meta-line">
            <span
              class="audit-frame-browser__severity"
              :class="`audit-frame-browser__severity--${frame.severity ?? 'medium'}`"
            >{{ frame.severity ?? 'unknown' }}</span>
            <span v-if="frame.confidence != null" class="audit-frame-browser__confidence">{{ formatConfidence(frame.confidence) }}</span>
          </span>
        </div>
      </button>
    </div>

    <AnalyzedFrameLightbox
      :open="selectedFrameIndex != null"
      :category="selectedFrame?.category ?? undefined"
      :confidence="selectedFrame?.confidence ?? undefined"
      :description="selectedFrame?.description ?? undefined"
      :frame-index="selectedFrame?.frame_index ?? undefined"
      :frames-total="issueFrames.length"
      :image-url="selectedFrame?.frame_image_url ?? undefined"
      :regions="selectedFrameDetail?.detection_regions ?? []"
      :severity="selectedFrame?.severity ?? undefined"
      @close="closeFrame"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppCard from '@/components/common/AppCard.vue';
import AppEmptyState from '@/components/common/AppEmptyState.vue';
import AppLoading from '@/components/common/AppLoading.vue';
import AnalyzedFrameLightbox from '@/components/audit/AnalyzedFrameLightbox.vue';
import { getAuditFrame } from '@/api/auditFrames';
import type { AuditFrameDetail, AuditFrameSummary } from '@/types/audit';
import { resolveApiAssetUrl } from '@/utils/apiAssets';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';

const props = withDefaults(
  defineProps<{
    runId: string;
    frames: AuditFrameSummary[];
    isLoading?: boolean;
    error?: string | null;
  }>(),
  {
    isLoading: false,
    error: null,
  },
);

defineEmits<{
  refresh: [];
}>();

const selectedFrameIndex = ref<number | null>(null);
const selectedFrameDetail = ref<AuditFrameDetail | null>(null);

const issueFrames = computed(() =>
  props.frames.filter((frame) => frame.is_civic_issue),
);

const selectedFrame = computed(
  () => issueFrames.value.find((frame) => frame.frame_index === selectedFrameIndex.value) ?? null,
);

watch(
  () => props.frames,
  () => {
    if (
      selectedFrameIndex.value != null &&
      !issueFrames.value.some((frame) => frame.frame_index === selectedFrameIndex.value)
    ) {
      selectedFrameIndex.value = null;
      selectedFrameDetail.value = null;
    }
  },
);

watch(
  () => [props.runId, selectedFrameIndex.value] as const,
  async ([runId, frameIndex]) => {
    if (frameIndex == null) {
      selectedFrameDetail.value = null;
      return;
    }

    try {
      selectedFrameDetail.value = await getAuditFrame(runId, frameIndex);
    } catch {
      selectedFrameDetail.value = null;
    }
  },
);

function openFrame(frameIndex: number) {
  selectedFrameIndex.value = frameIndex;
}

function closeFrame() {
  selectedFrameIndex.value = null;
}
</script>

<style scoped>
.audit-frame-browser {
  display: grid;
  gap: 0.5rem;
}

.audit-frame-browser__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.audit-frame-browser__label {
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.audit-frame-browser__grid {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.2rem;
  scrollbar-width: none;
}

.audit-frame-browser__grid::-webkit-scrollbar {
  display: none;
}

.audit-frame-browser__card {
  display: grid;
  flex-shrink: 0;
  width: 7.5rem;
  overflow: hidden;
  padding: 0;
  border: var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface-inset);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.audit-frame-browser__card:hover {
  border-color: color-mix(in srgb, var(--color-municipal-green) 35%, var(--status-new-border));
  box-shadow: 0 6px 18px color-mix(in srgb, var(--color-municipal-green) 12%, transparent);
  transform: translateY(-1px);
}

.audit-frame-browser__card--low {
  border-top: 3px solid #22c55e;
}

.audit-frame-browser__card--medium {
  border-top: 3px solid #eab308;
}

.audit-frame-browser__card--high,
.audit-frame-browser__card--critical {
  border-top: 3px solid #ef4444;
}

.audit-frame-browser__card-media {
  position: relative;
  aspect-ratio: 1 / 1;
  background: var(--surface-map-placeholder);
}

.audit-frame-browser__card-media img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.audit-frame-browser__expand {
  position: absolute;
  right: 0.35rem;
  bottom: 0.35rem;
  display: grid;
  place-items: center;
  width: 1.5rem;
  height: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  background: rgba(8, 12, 10, 0.72);
  color: #fff;
  backdrop-filter: blur(6px);
  pointer-events: none;
}

.audit-frame-browser__card-body {
  display: grid;
  gap: 0.15rem;
  padding: 0.4rem 0.45rem 0.45rem;
  background: color-mix(in srgb, var(--surface-panel-strong) 88%, transparent);
  border-top: var(--border-soft);
}

.audit-frame-browser__card-body strong {
  color: var(--text-primary);
  font-size: 0.65rem;
  font-weight: 900;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.audit-frame-browser__meta-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.25rem;
  font-size: 0.58rem;
  font-weight: 800;
}

.audit-frame-browser__severity {
  text-transform: capitalize;
}

.audit-frame-browser__severity--low { color: #22c55e; }
.audit-frame-browser__severity--medium { color: #eab308; }
.audit-frame-browser__severity--high,
.audit-frame-browser__severity--critical { color: #f87171; }

.audit-frame-browser__confidence {
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}
</style>
