<template>
  <AppCard class="metric-card" :class="`metric-card--${tone}`" variant="inset">
    <span class="metric-card__label">{{ label }}</span>
    <strong class="metric-card__value">{{ value }}</strong>
    <p>{{ description }}</p>
  </AppCard>
</template>

<script setup lang="ts">
import AppCard from './AppCard.vue';

withDefaults(
  defineProps<{
    label: string;
    value: string;
    description: string;
    tone?: 'neutral' | 'success' | 'warning' | 'info' | 'ai';
  }>(),
  {
    tone: 'neutral',
  },
);
</script>

<style scoped>
.metric-card {
  display: grid;
  gap: var(--space-2);
}

.metric-card__label {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-card__value {
  color: var(--text-primary);
  font-size: clamp(1.6rem, 4vw, 2.45rem);
  line-height: 1;
  letter-spacing: -0.05em;
}

p {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.metric-card--success {
  border-color: var(--source-citizen-border);
}

.metric-card--warning {
  border-color: var(--severity-medium-border);
}

.metric-card--info {
  border-color: var(--status-verified-border);
}

.metric-card--ai {
  border-color: var(--source-ai-audit-border);
}
</style>

