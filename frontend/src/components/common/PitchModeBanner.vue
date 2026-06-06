<template>
  <aside v-if="uiStore.demoMode" class="pitch-banner" :class="{ 'pitch-banner--compact': compact }" aria-live="polite">
    <div>
      <AppBadge :tone="dataMode === 'live' ? 'success' : 'warning'">{{ demoScenario.enabledLabel }}</AppBadge>
      <strong>{{ label }}</strong>
      <p>{{ resolvedMessage }}</p>
    </div>
    <AppButton size="sm" variant="secondary" @click="uiStore.setDemoMode(false)">
      Disable
    </AppButton>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from './AppBadge.vue';
import AppButton from './AppButton.vue';
import { demoScenario } from '@/demo/demoScenario';
import { useUiStore } from '@/stores/ui';
import type { DataMode } from '@/types/demo';

const props = withDefaults(
  defineProps<{
    dataMode?: DataMode;
    message?: string;
    compact?: boolean;
  }>(),
  {
    dataMode: 'demo',
    message: undefined,
    compact: false,
  },
);

const uiStore = useUiStore();

const label = computed(() => {
  if (props.dataMode === 'live') {
    return 'Pitch mode is on, but this page is using live backend data.';
  }

  if (props.dataMode === 'mixed') {
    return 'Pitch mode is mixing live data with demo context.';
  }

  return 'Pitch mode is showing prepared demo records.';
});

const resolvedMessage = computed(() => props.message ?? demoScenario.disclaimer);
</script>

<style scoped>
.pitch-banner {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: center;
  justify-content: space-between;
  border: 1px solid rgba(217, 144, 47, 0.36);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  background: rgba(255, 247, 225, 0.82);
}

.pitch-banner div {
  display: grid;
  gap: var(--space-2);
}

.pitch-banner strong,
.pitch-banner p {
  margin: 0;
}

.pitch-banner p {
  color: var(--text-secondary);
}

.pitch-banner--compact {
  padding: var(--space-3);
}

.pitch-banner--compact p {
  font-size: var(--text-sm);
}

@media (max-width: 640px) {
  .pitch-banner {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    padding: var(--space-3);
  }
}
</style>
