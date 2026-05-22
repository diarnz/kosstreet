<template>
  <article class="metric-card glass-panel" :class="`metric-card--${tone}`">
    <span class="metric-card__glow" aria-hidden="true" />
    <span class="metric-card__label">{{ label }}</span>
    <strong class="metric-card__value">{{ value }}</strong>
    <p v-if="description">{{ description }}</p>
  </article>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string;
    value: string;
    description?: string;
    tone?: 'neutral' | 'success' | 'warning' | 'info' | 'ai';
  }>(),
  {
    tone: 'neutral',
  },
);
</script>

<style scoped>
.metric-card {
  position: relative;
  display: grid;
  gap: var(--space-1);
  padding: var(--space-4);
  overflow: hidden;
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    box-shadow var(--motion-fast) ease;
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow:
    0 20px 48px rgba(23, 33, 26, 0.1),
    inset 0 1px 0 rgba(255, 253, 247, 0.85);
}

.metric-card__glow {
  position: absolute;
  top: -40%;
  right: -20%;
  width: 5rem;
  height: 5rem;
  border-radius: 50%;
  background: var(--metric-glow, rgba(47, 93, 80, 0.12));
  filter: blur(24px);
  pointer-events: none;
}

.metric-card__label {
  position: relative;
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-card__value {
  position: relative;
  color: var(--text-primary);
  font-size: clamp(1.6rem, 4vw, 2.35rem);
  line-height: 1;
  letter-spacing: -0.05em;
}

p {
  position: relative;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.metric-card--success {
  --metric-glow: rgba(47, 93, 80, 0.18);
  border-color: var(--source-citizen-border);
}

.metric-card--warning {
  --metric-glow: rgba(217, 144, 47, 0.2);
  border-color: var(--severity-medium-border);
}

.metric-card--info {
  --metric-glow: rgba(63, 110, 140, 0.18);
  border-color: var(--status-verified-border);
}

.metric-card--ai {
  --metric-glow: rgba(140, 108, 58, 0.22);
  border-color: var(--source-ai-audit-border);
}
</style>
