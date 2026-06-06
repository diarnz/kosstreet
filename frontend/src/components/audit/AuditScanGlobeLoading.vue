<template>
  <section class="audit-scan-globe-loading" aria-label="Loading scan path" aria-live="polite">
    <div class="audit-scan-globe-loading__layout">
      <div class="audit-scan-globe-loading__copy">
        <p class="audit-scan-globe-loading__eyebrow">Route scanner</p>
        <h2 class="audit-scan-globe-loading__title">Loading scan path</h2>
        <p class="audit-scan-globe-loading__description">
          Fetching route analysis points across Kosovo…
        </p>
        <div class="audit-scan-globe-loading__indicator" role="status">
          <span class="audit-scan-globe-loading__spinner" aria-hidden="true" />
          <span>Syncing pipeline data</span>
        </div>
      </div>

      <div class="audit-scan-globe-loading__globe-wrap" aria-hidden="true">
        <AuditGlobeCanvas class="audit-scan-globe-loading__globe" />
        <div class="audit-scan-globe-loading__pulse" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import AuditGlobeCanvas from '@/components/audit/AuditGlobeCanvas.vue';
</script>

<style scoped>
.audit-scan-globe-loading {
  position: relative;
  overflow: hidden;
  border: var(--border-soft);
  border-radius: calc(var(--radius-lg) + 4px);
  background: color-mix(in srgb, var(--surface-panel-strong) 88%, var(--color-ai-surface));
  box-shadow: var(--shadow-card);
  padding: clamp(1.25rem, 4vw, 2rem);
}

.audit-scan-globe-loading__layout {
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  gap: var(--space-4);
}

.audit-scan-globe-loading__copy {
  position: relative;
  z-index: 1;
  display: grid;
  gap: var(--space-2);
  width: 100%;
  max-width: 28rem;
  text-align: left;
}

.audit-scan-globe-loading__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.audit-scan-globe-loading__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.35rem, 4vw, 1.85rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.15;
  color: var(--text-primary);
}

.audit-scan-globe-loading__description {
  margin: 0;
  max-width: 26rem;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.audit-scan-globe-loading__indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 750;
}

.audit-scan-globe-loading__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(47, 93, 80, 0.22);
  border-top-color: var(--color-municipal-green);
  border-radius: 50%;
  animation: audit-globe-spin 800ms linear infinite;
}

.audit-scan-globe-loading__globe-wrap {
  position: relative;
  width: 100%;
  max-width: 22rem;
  height: 9.5rem;
  flex-shrink: 0;
}

.audit-scan-globe-loading__globe {
  position: absolute;
  right: -18%;
  bottom: -72%;
  width: 130%;
  max-width: 24rem;
  transform: scale(1.15);
  opacity: 0.95;
}

.audit-scan-globe-loading__pulse {
  position: absolute;
  inset: 10% 5% 20%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(47, 93, 80, 0.14) 0%, transparent 70%);
  animation: audit-globe-pulse 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes audit-globe-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes audit-globe-pulse {
  0%,
  100% {
    opacity: 0.35;
    transform: scale(0.92);
  }
  50% {
    opacity: 0.85;
    transform: scale(1.05);
  }
}

@media (min-width: 720px) {
  .audit-scan-globe-loading__layout {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-6);
  }

  .audit-scan-globe-loading__copy {
    flex: 1 1 18rem;
  }

  .audit-scan-globe-loading__globe-wrap {
    flex: 1 1 14rem;
    max-width: 26rem;
    height: 11rem;
  }

  .audit-scan-globe-loading__globe {
    right: -28%;
    bottom: -68%;
    transform: scale(1.35);
  }
}

@media (max-width: 640px) {
  .audit-scan-globe-loading {
    padding: var(--space-4);
  }

  .audit-scan-globe-loading__globe-wrap {
    height: 8rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .audit-scan-globe-loading__spinner,
  .audit-scan-globe-loading__pulse {
    animation: none;
  }
}
</style>
