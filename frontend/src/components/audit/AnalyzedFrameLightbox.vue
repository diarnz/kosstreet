<template>
  <Teleport to="body">
    <Transition
      name="frame-lightbox"
      @before-enter="onBeforeEnter"
      @before-leave="onBeforeLeave"
    >
      <div
        v-if="open"
        class="frame-lightbox"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
        @click.self="emit('close')"
      >
        <button class="frame-lightbox__close" type="button" aria-label="Close" @click="emit('close')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
          </svg>
        </button>

        <div ref="panelRef" class="frame-lightbox__panel">
          <div class="frame-lightbox__stage">
            <img
              v-if="resolvedImageUrl"
              :src="resolvedImageUrl"
              :alt="alt"
              class="frame-lightbox__image"
            />
            <div v-else class="frame-lightbox__placeholder muted">Frame unavailable</div>

            <DetectionCircleOverlay
              v-if="resolvedImageUrl && displayRegions.length"
              overlay-id="lightbox"
              :category="category ?? undefined"
              :confidence="confidence ?? undefined"
              :description="description ?? undefined"
              interactive
              :regions="displayRegions"
              :severity="severity ?? undefined"
            />
          </div>

          <div v-if="hasCaption" class="frame-lightbox__caption">
            <div class="frame-lightbox__pill">
              <span v-if="frameLabel" class="frame-lightbox__tag frame-lightbox__tag--muted">{{ frameLabel }}</span>
              <span v-if="category" class="frame-lightbox__tag frame-lightbox__tag--title">{{ categoryLabel }}</span>
              <span
                v-if="severity"
                class="frame-lightbox__tag frame-lightbox__tag--severity"
                :class="`frame-lightbox__tag--severity-${severity}`"
              >
                {{ severityLabel }}
              </span>
              <span v-if="confidence != null" class="frame-lightbox__tag frame-lightbox__tag--confidence">
                {{ confidenceLabel }}
              </span>
            </div>
            <p v-if="description && !displayRegions.length" class="frame-lightbox__description">
              {{ description }}
            </p>
            <p v-if="hasRegions" class="frame-lightbox__hint">Tap highlight for AI details</p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue';
import type { AuditSuggestionSeverity, DetectionRegion } from '@/types/detection';
import type { IssueCategory } from '@/types/report';
import { resolveApiAssetUrl } from '@/utils/apiAssets';
import { SEVERITY_LABELS } from '@/utils/detectionRegions';
import { categoryLabels, formatConfidence } from '@/utils/reportFormatting';
import DetectionCircleOverlay from '@/components/audit/DetectionCircleOverlay.vue';

export type LightboxOriginRect = {
  top: number;
  left: number;
  width: number;
  height: number;
};

const props = withDefaults(
  defineProps<{
    open: boolean;
    imageUrl?: string | null;
    regions?: DetectionRegion[] | null;
    severity?: AuditSuggestionSeverity | null;
    category?: IssueCategory | null;
    description?: string | null;
    confidence?: number | null;
    frameIndex?: number | null;
    framesTotal?: number | null;
    alt?: string;
    originRect?: LightboxOriginRect | null;
  }>(),
  {
    imageUrl: null,
    regions: () => [],
    severity: null,
    category: null,
    description: null,
    confidence: null,
    frameIndex: null,
    framesTotal: null,
    alt: 'AI street audit evidence frame',
    originRect: null,
  },
);

const emit = defineEmits<{
  close: [];
}>();

const panelRef = ref<HTMLElement | null>(null);
const leaveOriginRect = ref<LightboxOriginRect | null>(null);

const resolvedImageUrl = computed(() =>
  props.imageUrl ? resolveApiAssetUrl(props.imageUrl) : null,
);
const displayRegions = computed(() => props.regions ?? []);
const hasRegions = computed(() => displayRegions.value.length > 0);
const severityLabel = computed(() =>
  props.severity ? SEVERITY_LABELS[props.severity] : '',
);
const categoryLabel = computed(() =>
  props.category ? categoryLabels[props.category] : 'Issue',
);
const confidenceLabel = computed(() =>
  props.confidence == null ? '' : formatConfidence(props.confidence),
);
const frameLabel = computed(() => {
  if (props.frameIndex == null) {
    return null;
  }
  if (props.framesTotal != null) {
    return `Frame ${props.frameIndex + 1} / ${props.framesTotal}`;
  }
  return `Frame ${props.frameIndex + 1}`;
});
const title = computed(() =>
  props.category ? `${categoryLabel.value} evidence` : 'Analyzed frame evidence',
);
const hasCaption = computed(
  () =>
    Boolean(frameLabel.value || props.category || props.severity || props.confidence != null) ||
    (Boolean(props.description) && !hasRegions.value) ||
    hasRegions.value,
);

function targetPanelSize() {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const width = Math.min(vw * 0.92, 68 * 16);
  const height = Math.min(vh * 0.72, width);
  return { width, height };
}

function applyFlipTransform(panel: HTMLElement, rect: LightboxOriginRect) {
  const { width: targetW, height: targetH } = targetPanelSize();
  const originCx = rect.left + rect.width / 2;
  const originCy = rect.top + rect.height / 2;
  const viewportCx = window.innerWidth / 2;
  const viewportCy = window.innerHeight / 2;
  const scaleX = rect.width / targetW;
  const scaleY = rect.height / targetH;
  const scale = Math.max(Math.min(scaleX, scaleY), 0.06);

  panel.style.setProperty('--flip-x', `${originCx - viewportCx}px`);
  panel.style.setProperty('--flip-y', `${originCy - viewportCy}px`);
  panel.style.setProperty('--flip-scale', String(scale));
}

function onBeforeEnter(el: Element) {
  const panel = (panelRef.value ?? el.querySelector('.frame-lightbox__panel')) as HTMLElement | null;
  if (panel && props.originRect) {
    applyFlipTransform(panel, props.originRect);
  }
}

function onBeforeLeave(el: Element) {
  const panel = (panelRef.value ?? el.querySelector('.frame-lightbox__panel')) as HTMLElement | null;
  const rect = leaveOriginRect.value ?? props.originRect;
  if (panel && rect) {
    applyFlipTransform(panel, rect);
  }
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close');
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      leaveOriginRect.value = props.originRect ? { ...props.originRect } : null;
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', onKeydown);
    } else {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', onKeydown);
    }
  },
  { immediate: true },
);

onUnmounted(() => {
  document.body.style.overflow = '';
  window.removeEventListener('keydown', onKeydown);
});
</script>

<style scoped>
.frame-lightbox {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  background: rgba(8, 12, 18, 0.88);
  backdrop-filter: blur(12px);
}

.frame-lightbox-enter-active,
.frame-lightbox-leave-active {
  transition:
    opacity 380ms var(--ease-out-expo, ease),
    backdrop-filter 380ms var(--ease-out-expo, ease);
}

.frame-lightbox-enter-from,
.frame-lightbox-leave-to {
  opacity: 0;
  backdrop-filter: blur(0);
}

.frame-lightbox__close {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  z-index: 2;
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  cursor: pointer;
  transition: background 180ms ease, transform 180ms ease;
}

.frame-lightbox__close:hover {
  background: rgba(255, 255, 255, 0.16);
  transform: scale(1.05);
}

.frame-lightbox__panel {
  --flip-x: 0px;
  --flip-y: 0px;
  --flip-scale: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  width: min(92vw, 68rem);
  max-height: 92vh;
  transform: translate(0, 0) scale(1);
  opacity: 1;
}

.frame-lightbox-enter-active .frame-lightbox__panel,
.frame-lightbox-leave-active .frame-lightbox__panel {
  transition:
    transform 520ms var(--ease-spring, cubic-bezier(0.22, 1.12, 0.32, 1)),
    opacity 360ms var(--ease-out-expo, ease);
}

.frame-lightbox-enter-from .frame-lightbox__panel,
.frame-lightbox-leave-to .frame-lightbox__panel {
  transform: translate(var(--flip-x), var(--flip-y)) scale(var(--flip-scale));
}

.frame-lightbox-enter-from .frame-lightbox__panel {
  opacity: 0.72;
}

.frame-lightbox-leave-to .frame-lightbox__panel {
  opacity: 0.55;
}

.frame-lightbox__stage {
  position: relative;
  overflow: hidden;
  width: 100%;
  border-radius: var(--radius-lg);
  background: #0f141d;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45);
  aspect-ratio: 1 / 1;
  max-height: min(72vh, 68rem);
}

.frame-lightbox__image,
.frame-lightbox__placeholder {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #0f141d;
}

.frame-lightbox__placeholder {
  display: grid;
  place-items: center;
  min-height: 20rem;
}

.frame-lightbox__caption {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  width: fit-content;
  max-width: min(92vw, 34rem);
  text-align: center;
}

.frame-lightbox__pill {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  padding: 0.42rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 999px;
  background: rgba(12, 16, 22, 0.72);
  backdrop-filter: blur(14px);
  box-shadow: 0 10px 36px rgba(0, 0, 0, 0.32);
}

.frame-lightbox__tag {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1;
  white-space: nowrap;
}

.frame-lightbox__tag + .frame-lightbox__tag::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  margin-right: 0.3rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.28);
  vertical-align: middle;
}

.frame-lightbox__tag--title {
  font-size: 0.8rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: #fff;
}

.frame-lightbox__tag--muted {
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.65rem;
  font-weight: 750;
}

.frame-lightbox__tag--confidence {
  color: rgba(255, 255, 255, 0.88);
  font-variant-numeric: tabular-nums;
}

.frame-lightbox__tag--severity {
  padding: 0.18rem 0.5rem;
  border-radius: 999px;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.frame-lightbox__tag--severity::before {
  display: none !important;
}

.frame-lightbox__tag--severity-low {
  background: rgba(34, 197, 94, 0.22);
  color: #86efac;
}

.frame-lightbox__tag--severity-medium {
  background: rgba(234, 179, 8, 0.22);
  color: #fde68a;
}

.frame-lightbox__tag--severity-high,
.frame-lightbox__tag--severity-critical {
  background: rgba(239, 68, 68, 0.24);
  color: #fca5a5;
}

.frame-lightbox__description {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.72rem;
  line-height: 1.45;
}

.frame-lightbox__hint {
  margin: 0;
  color: rgba(255, 255, 255, 0.42);
  font-size: 0.62rem;
  font-weight: 650;
  letter-spacing: 0.02em;
}

@media (prefers-reduced-motion: reduce) {
  .frame-lightbox-enter-active,
  .frame-lightbox-leave-active,
  .frame-lightbox-enter-active .frame-lightbox__panel,
  .frame-lightbox-leave-active .frame-lightbox__panel {
    transition-duration: 1ms !important;
  }

  .frame-lightbox__panel {
    transform: none !important;
    opacity: 1 !important;
  }
}
</style>
