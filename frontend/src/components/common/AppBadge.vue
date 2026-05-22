<template>
  <span class="app-badge" :class="classes">
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { BadgeTone } from '@/types/ui';

const props = withDefaults(
  defineProps<{
    tone?: BadgeTone;
    size?: 'xs' | 'sm' | 'md';
  }>(),
  {
    tone: 'neutral',
    size: 'md',
  },
);

const classes = computed(() => [`app-badge--${props.tone}`, `app-badge--${props.size}`]);
</script>

<style scoped>
.app-badge {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  border: 1px solid transparent;
  border-radius: var(--radius-pill);
  font-weight: 800;
  letter-spacing: 0.01em;
  line-height: 1;
  white-space: nowrap;
}

.app-badge--xs {
  padding: 0.18rem 0.42rem;
  font-size: 0.62rem;
}

.app-badge--sm {
  padding: 0.32rem 0.55rem;
  font-size: 0.72rem;
}

.app-badge--md {
  padding: 0.45rem 0.7rem;
  font-size: var(--text-xs);
}

.app-badge--neutral {
  color: var(--status-new-text);
  background: var(--status-new-surface);
  border-color: var(--status-new-border);
}

.app-badge--success {
  color: var(--status-assigned-text);
  background: var(--status-assigned-surface);
  border-color: var(--status-assigned-border);
}

.app-badge--warning {
  color: var(--status-in-progress-text);
  background: var(--status-in-progress-surface);
  border-color: var(--status-in-progress-border);
}

.app-badge--danger {
  color: var(--status-rejected-text);
  background: var(--status-rejected-surface);
  border-color: var(--status-rejected-border);
}

.app-badge--info {
  color: var(--status-verified-text);
  background: var(--status-verified-surface);
  border-color: var(--status-verified-border);
}

.app-badge--ai {
  color: var(--source-ai-audit-text);
  background: var(--source-ai-audit-surface);
  border-color: var(--source-ai-audit-border);
}

.app-badge--status-new {
  color: var(--status-new-text);
  background: var(--status-new-surface);
  border-color: var(--status-new-border);
}

.app-badge--status-verified {
  color: var(--status-verified-text);
  background: var(--status-verified-surface);
  border-color: var(--status-verified-border);
}

.app-badge--status-assigned {
  color: var(--status-assigned-text);
  background: var(--status-assigned-surface);
  border-color: var(--status-assigned-border);
}

.app-badge--status-in-progress {
  color: var(--status-in-progress-text);
  background: var(--status-in-progress-surface);
  border-color: var(--status-in-progress-border);
}

.app-badge--status-resolved {
  color: var(--status-resolved-text);
  background: var(--status-resolved-surface);
  border-color: var(--status-resolved-border);
}

.app-badge--status-rejected {
  color: var(--status-rejected-text);
  background: var(--status-rejected-surface);
  border-color: var(--status-rejected-border);
}

.app-badge--severity-low {
  color: var(--severity-low-text);
  background: var(--severity-low-surface);
  border-color: var(--severity-low-border);
}

.app-badge--severity-medium {
  color: var(--severity-medium-text);
  background: var(--severity-medium-surface);
  border-color: var(--severity-medium-border);
}

.app-badge--severity-high {
  color: var(--severity-high-text);
  background: var(--severity-high-surface);
  border-color: var(--severity-high-border);
}

.app-badge--severity-critical {
  color: var(--severity-critical-text);
  background: var(--severity-critical-surface);
  border-color: var(--severity-critical-border);
}

.app-badge--source-citizen {
  color: var(--source-citizen-text);
  background: var(--source-citizen-surface);
  border-color: var(--source-citizen-border);
}

.app-badge--source-ai-audit {
  color: var(--source-ai-audit-text);
  background: var(--source-ai-audit-surface);
  border-color: var(--source-ai-audit-border);
}

.app-badge--category-pothole {
  color: var(--category-pothole-text);
  background: var(--category-pothole-surface);
  border-color: var(--category-pothole-border);
}

.app-badge--category-garbage {
  color: var(--category-garbage-text);
  background: var(--category-garbage-surface);
  border-color: var(--category-garbage-border);
}

.app-badge--category-broken-streetlight {
  color: var(--category-broken-streetlight-text);
  background: var(--category-broken-streetlight-surface);
  border-color: var(--category-broken-streetlight-border);
}

.app-badge--category-blocked-sidewalk {
  color: var(--category-blocked-sidewalk-text);
  background: var(--category-blocked-sidewalk-surface);
  border-color: var(--category-blocked-sidewalk-border);
}

.app-badge--category-damaged-sign {
  color: var(--category-damaged-sign-text);
  background: var(--category-damaged-sign-surface);
  border-color: var(--category-damaged-sign-border);
}

.app-badge--category-other {
  color: var(--category-other-text);
  background: var(--category-other-surface);
  border-color: var(--category-other-border);
}
</style>
