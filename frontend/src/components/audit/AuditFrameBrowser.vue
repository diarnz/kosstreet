<template>
  <section class="audit-frame-browser">
    <div class="audit-frame-browser__header">
      <div>
        <h3 class="audit-frame-browser__title">Detected issues</h3>
        <p class="audit-frame-browser__subtitle muted">Tap a card to inspect full-frame evidence.</p>
      </div>
      <AppBadge tone="source-ai-audit">{{ issueFrames.length }}</AppBadge>
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
          <span class="audit-frame-browser__expand" aria-hidden="true">⤢</span>
        </div>
        <div class="audit-frame-browser__card-body">
          <strong>{{ frame.category ? categoryLabels[frame.category] : 'Issue' }}</strong>
          <span class="audit-frame-browser__meta-line">
            <span class="audit-frame-browser__severity">{{ frame.severity ?? 'unknown' }}</span>
            <span v-if="frame.confidence != null">{{ formatConfidence(frame.confidence) }}</span>
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
  gap: var(--space-4);
}

.audit-frame-browser__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
}

.audit-frame-browser__title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 900;
  letter-spacing: -0.02em;
}

.audit-frame-browser__subtitle {
  margin: var(--space-1) 0 0;
  font-size: var(--text-sm);
}

.audit-frame-browser__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 10.5rem), 1fr));
  gap: var(--space-3);
}

.audit-frame-browser__card {
  display: grid;
  overflow: hidden;
  padding: 0;
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: calc(var(--radius-md) + 2px);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 253, 247, 0.62)),
    var(--surface-panel);
  box-shadow: 0 10px 24px rgba(23, 33, 26, 0.06);
  cursor: pointer;
  text-align: left;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease;
}

.audit-frame-browser__card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(23, 33, 26, 0.12);
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
  right: var(--space-2);
  bottom: var(--space-2);
  display: grid;
  place-items: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 999px;
  background: rgba(8, 12, 18, 0.72);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 900;
}

.audit-frame-browser__card-body {
  display: grid;
  gap: var(--space-1);
  padding: var(--space-3);
}

.audit-frame-browser__card-body strong {
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 900;
}

.audit-frame-browser__meta-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 800;
}

.audit-frame-browser__severity {
  text-transform: capitalize;
}
</style>
