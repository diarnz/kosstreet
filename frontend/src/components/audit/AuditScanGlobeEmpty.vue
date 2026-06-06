<template>
  <section class="audit-scan-globe-empty" aria-label="Waiting for scan points">
    <div class="audit-scan-globe-empty__layout">
      <div class="audit-scan-globe-empty__copy">
        <p class="audit-scan-globe-empty__eyebrow">Route scanner</p>
        <h2 class="audit-scan-globe-empty__title">
          No scan points yet
        </h2>
        <p class="audit-scan-globe-empty__description">
          Scan points appear here once the pipeline starts analyzing the route across Kosovo.
        </p>
        <AppButton variant="secondary" size="sm" class="audit-scan-globe-empty__action" @click="$emit('refresh')">
          Refresh
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M5 12h14M13 6l6 6-6 6"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </AppButton>
      </div>

      <div class="audit-scan-globe-empty__globe-wrap" aria-hidden="true">
        <AuditGlobeCanvas class="audit-scan-globe-empty__globe" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import AppButton from '@/components/common/AppButton.vue';
import AuditGlobeCanvas from '@/components/audit/AuditGlobeCanvas.vue';

defineEmits<{
  refresh: [];
}>();
</script>

<style scoped>
.audit-scan-globe-empty {
  position: relative;
  overflow: hidden;
  border: var(--border-soft);
  border-radius: calc(var(--radius-lg) + 4px);
  background: color-mix(in srgb, var(--surface-panel-strong) 88%, var(--color-ai-surface));
  box-shadow: var(--shadow-card);
  padding: clamp(1.25rem, 4vw, 2rem);
}

.audit-scan-globe-empty__layout {
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  gap: var(--space-4);
}

.audit-scan-globe-empty__copy {
  position: relative;
  z-index: 1;
  display: grid;
  gap: var(--space-2);
  width: 100%;
  max-width: 28rem;
  text-align: left;
}

.audit-scan-globe-empty__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.audit-scan-globe-empty__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.35rem, 4vw, 1.85rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.15;
  color: var(--text-primary);
}

.audit-scan-globe-empty__description {
  margin: 0;
  max-width: 26rem;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.audit-scan-globe-empty__action {
  justify-self: start;
  margin-top: var(--space-2);
  border-radius: var(--radius-pill);
}

.audit-scan-globe-empty__globe-wrap {
  position: relative;
  width: 100%;
  max-width: 22rem;
  height: 9.5rem;
  flex-shrink: 0;
}

.audit-scan-globe-empty__globe {
  position: absolute;
  right: -18%;
  bottom: -72%;
  width: 130%;
  max-width: 24rem;
  transform: scale(1.15);
  opacity: 0.95;
}

@media (min-width: 720px) {
  .audit-scan-globe-empty__layout {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-6);
  }

  .audit-scan-globe-empty__copy {
    flex: 1 1 18rem;
  }

  .audit-scan-globe-empty__globe-wrap {
    flex: 1 1 14rem;
    max-width: 26rem;
    height: 11rem;
  }

  .audit-scan-globe-empty__globe {
    right: -28%;
    bottom: -68%;
    transform: scale(1.35);
  }
}

@media (max-width: 640px) {
  .audit-scan-globe-empty {
    padding: var(--space-4);
  }

  .audit-scan-globe-empty__globe-wrap {
    height: 8rem;
  }
}
</style>
