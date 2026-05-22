<template>
  <AppCard class="feature-panel" :class="`feature-panel--${tone}`" interactive>
    <div class="feature-panel__marker" aria-hidden="true" />
    <div class="stack">
      <AppBadge :tone="badgeTone">{{ eyebrow }}</AppBadge>
      <div class="stack">
        <h2>{{ title }}</h2>
        <p>{{ description }}</p>
      </div>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from './AppBadge.vue';
import AppCard from './AppCard.vue';
import type { BadgeTone } from '@/types/ui';

const props = withDefaults(
  defineProps<{
    eyebrow: string;
    title: string;
    description: string;
    tone?: 'citizen' | 'dashboard' | 'audit';
  }>(),
  {
    tone: 'dashboard',
  },
);

const badgeTone = computed<BadgeTone>(() => {
  if (props.tone === 'citizen') return 'source-citizen';
  if (props.tone === 'audit') return 'source-ai-audit';
  return 'info';
});
</script>

<style scoped>
.feature-panel {
  position: relative;
  overflow: hidden;
  min-height: 17rem;
}

.feature-panel__marker {
  width: 2.7rem;
  height: 2.7rem;
  border-radius: 1rem;
  background: var(--color-municipal-green);
  box-shadow: 0 14px 28px rgba(47, 93, 80, 0.18);
}

.feature-panel--citizen .feature-panel__marker {
  background: linear-gradient(135deg, var(--color-municipal-green), var(--color-garbage-green));
}

.feature-panel--dashboard .feature-panel__marker {
  background: linear-gradient(135deg, var(--color-resolved-blue), var(--color-municipal-green));
}

.feature-panel--audit .feature-panel__marker {
  background: linear-gradient(135deg, var(--color-amber-signal), #7a6335);
}

h2 {
  margin: 0;
  font-size: var(--text-xl);
  letter-spacing: -0.03em;
}

p {
  color: var(--text-secondary);
}
</style>

