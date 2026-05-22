<template>
  <div class="audit-scan-timeline" role="list" aria-label="Scan path timeline">
    <button
      v-for="point in scanPath"
      :key="point.frame_index"
      class="audit-scan-timeline__point"
      :class="timelinePointClasses(point)"
      type="button"
      role="listitem"
      :aria-label="timelineLabel(point)"
      :aria-current="point.frame_index === selectedFrameIndex ? 'step' : undefined"
      @click="emit('select', point.frame_index)"
      @mouseenter="emit('hover', point.frame_index)"
      @focus="emit('hover', point.frame_index)"
    >
      <span class="audit-scan-timeline__dot" aria-hidden="true">
        <span
          v-if="point.suggestion_status === 'converted_to_report'"
          class="audit-scan-timeline__status-mark"
          aria-hidden="true"
        >
          ✓
        </span>
      </span>
      <span class="audit-scan-timeline__index">{{ point.frame_index + 1 }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { AuditScanPoint } from '@/types/audit';
import { SEVERITY_LABELS } from '@/utils/detectionRegions';

const props = defineProps<{
  scanPath: AuditScanPoint[];
  selectedFrameIndex: number | null;
}>();

const emit = defineEmits<{
  select: [frameIndex: number];
  hover: [frameIndex: number];
}>();

function timelinePointClasses(point: AuditScanPoint): Record<string, boolean> {
  return {
    'audit-scan-timeline__point--selected': point.frame_index === props.selectedFrameIndex,
    'audit-scan-timeline__point--issue': point.is_civic_issue,
    [`audit-scan-timeline__point--${point.severity ?? 'detected'}`]: point.is_civic_issue,
    'audit-scan-timeline__point--accepted': point.suggestion_status === 'accepted',
    'audit-scan-timeline__point--rejected': point.suggestion_status === 'rejected',
    'audit-scan-timeline__point--converted': point.suggestion_status === 'converted_to_report',
    'audit-scan-timeline__point--manual-review':
      point.suggestion_status === 'needs_manual_review',
  };
}

function timelineLabel(point: AuditScanPoint): string {
  const position = `Scan point ${point.frame_index + 1}`;
  if (!point.is_civic_issue) {
    return `${position}, no issue detected`;
  }

  const severity = point.severity ? SEVERITY_LABELS[point.severity] : 'Issue';
  const statusSuffix = point.suggestion_status
    ? `, ${formatSuggestionStatus(point.suggestion_status)}`
    : '';

  return `${position}, ${severity} severity detection${statusSuffix}`;
}

function formatSuggestionStatus(status: NonNullable<AuditScanPoint['suggestion_status']>): string {
  switch (status) {
    case 'accepted':
      return 'accepted for review';
    case 'rejected':
      return 'rejected';
    case 'needs_manual_review':
      return 'needs manual review';
    case 'converted_to_report':
      return 'converted to report';
    default:
      return 'pending review';
  }
}
</script>

<style scoped>
.audit-scan-timeline {
  display: flex;
  gap: var(--space-2);
  overflow-x: auto;
  padding: var(--space-2) var(--space-1);
  scrollbar-width: thin;
}

.audit-scan-timeline__point {
  display: grid;
  justify-items: center;
  gap: var(--space-1);
  min-width: 2.25rem;
  padding: var(--space-1);
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  background: transparent;
  cursor: pointer;
  transition:
    background var(--motion-fast),
    transform var(--motion-fast);
}

.audit-scan-timeline__point:hover {
  background: rgba(47, 93, 80, 0.08);
}

.audit-scan-timeline__point--selected {
  background: rgba(47, 93, 80, 0.12);
}

.audit-scan-timeline__dot {
  position: relative;
  display: grid;
  place-items: center;
  width: 0.75rem;
  height: 0.75rem;
  border: 2px solid rgba(23, 33, 26, 0.2);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.9);
}

.audit-scan-timeline__point--issue .audit-scan-timeline__dot {
  border-color: transparent;
}

.audit-scan-timeline__point--low .audit-scan-timeline__dot {
  background: #22c55e;
}

.audit-scan-timeline__point--medium .audit-scan-timeline__dot,
.audit-scan-timeline__point--detected .audit-scan-timeline__dot {
  background: #eab308;
}

.audit-scan-timeline__point--high .audit-scan-timeline__dot {
  background: #ef4444;
}

.audit-scan-timeline__point--critical .audit-scan-timeline__dot {
  background: #b91c1c;
}

.audit-scan-timeline__point--accepted .audit-scan-timeline__dot {
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.55);
}

.audit-scan-timeline__point--rejected {
  opacity: 0.55;
}

.audit-scan-timeline__point--rejected .audit-scan-timeline__dot {
  background: rgba(107, 114, 128, 0.85);
}

.audit-scan-timeline__point--converted .audit-scan-timeline__dot {
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.55);
}

.audit-scan-timeline__point--manual-review .audit-scan-timeline__dot {
  box-shadow: 0 0 0 2px rgba(234, 179, 8, 0.55);
}

.audit-scan-timeline__point--selected .audit-scan-timeline__dot {
  transform: scale(1.15);
}

.audit-scan-timeline__status-mark {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 0.55rem;
  font-weight: 900;
  line-height: 1;
}

.audit-scan-timeline__index {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.audit-scan-timeline__point--selected .audit-scan-timeline__index {
  color: var(--text-primary);
}
</style>
