<template>
  <div class="map-fallback" role="status">
    <AppBadge tone="warning">Map unavailable</AppBadge>
    <h3>Use the report queue while the map is unavailable.</h3>
    <p>
      The dashboard still has {{ reportCount }} real report{{ reportCount === 1 ? '' : 's' }}
      available in the queue and detail panel.
    </p>
    <p v-if="reason" class="map-fallback__reason">{{ reason }}</p>
  </div>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';

defineProps<{
  reportCount: number;
  reason?: string;
}>();
</script>

<style scoped>
.map-fallback {
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

.map-fallback h3,
.map-fallback p {
  margin: 0;
}

.map-fallback p {
  max-width: 42rem;
  color: var(--text-secondary);
}

.map-fallback__reason {
  font-size: var(--text-sm);
}
</style>
