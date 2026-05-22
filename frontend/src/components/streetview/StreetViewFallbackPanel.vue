<template>
  <div class="street-view-fallback" role="status">
    <AppBadge tone="warning">Street View unavailable</AppBadge>
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <dl v-if="targetLabel || coordinates" class="street-view-fallback__target">
      <div v-if="targetLabel">
        <dt>Selected record</dt>
        <dd>{{ targetLabel }}</dd>
      </div>
      <div v-if="coordinates">
        <dt>Coordinate checked</dt>
        <dd>{{ coordinates }}</dd>
      </div>
    </dl>
    <p v-if="reason" class="street-view-fallback__reason">{{ reason }}</p>
  </div>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';

withDefaults(
  defineProps<{
    title?: string;
    description?: string;
    reason?: string | null;
    targetLabel?: string | null;
    coordinates?: string | null;
  }>(),
  {
    title: 'Use the queue and detail panel while Street View is unavailable.',
    description: 'The backend data remains available even when Google Street View cannot load.',
    reason: null,
    targetLabel: null,
    coordinates: null,
  },
);
</script>

<style scoped>
.street-view-fallback {
  display: grid;
  align-content: center;
  gap: var(--space-3);
  min-height: 24rem;
  border: var(--border-soft);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  background:
    linear-gradient(135deg, rgba(248, 234, 212, 0.8), rgba(255, 253, 247, 0.86)),
    var(--surface-panel-strong);
}

.street-view-fallback h3,
.street-view-fallback p {
  margin: 0;
}

.street-view-fallback p {
  max-width: 42rem;
  color: var(--text-secondary);
}

.street-view-fallback__reason {
  font-size: var(--text-sm);
}

.street-view-fallback__target {
  display: grid;
  gap: var(--space-2);
  margin: 0;
}

.street-view-fallback__target > div {
  display: grid;
  gap: var(--space-1);
}

dt {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

dd {
  margin: 0;
  color: var(--text-primary);
  font-weight: 800;
}
</style>
