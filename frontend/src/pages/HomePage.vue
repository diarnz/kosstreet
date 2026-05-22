<template>
  <AppShell content-width="full">
    <section class="home-hero animate-scale-in">
      <div class="home-hero__glow" aria-hidden="true" />
      <div class="home-hero__ring" aria-hidden="true" />

      <div class="home-hero__content">
        <AppLogo class="home-hero__logo" size="hero" animated />
        <h1 class="home-hero__title gradient-sweep-text">Civic intelligence for Kosovo</h1>
        <p class="home-hero__lead">
          One platform to report street issues, command municipal workflows, and review AI street audits nationwide.
        </p>

        <div class="home-hero__actions">
          <RouterLink class="home-hero__cta home-hero__cta--primary" to="/report">
            Report an issue
          </RouterLink>
          <RouterLink class="home-hero__cta" to="/dashboard">Open dashboard</RouterLink>
        </div>
      </div>
    </section>

    <section class="home-deck glass-panel glass-panel--elevated animate-fade-up" aria-label="Platform overview">
      <div class="home-deck__stats">
        <span v-for="stat in stats" :key="stat.label" class="home-deck__stat">
          <strong>{{ stat.value }}</strong>
          <span>{{ stat.label }}</span>
        </span>
      </div>

      <div class="home-deck__divider" aria-hidden="true" />

      <nav class="home-deck__nav" aria-label="Product surfaces">
        <RouterLink
          v-for="tile in tiles"
          :key="tile.to"
          :to="tile.to"
          class="home-deck__link"
          :class="`home-deck__link--${tile.tone}`"
        >
          <span class="home-deck__index">{{ tile.index }}</span>
          <span class="home-deck__link-title">{{ tile.title }}</span>
          <span class="home-deck__arrow" aria-hidden="true">→</span>
        </RouterLink>
      </nav>

      <div class="home-deck__divider" aria-hidden="true" />

      <div class="home-deck__pipeline">
        <span class="home-deck__pipeline-label">Pipeline</span>
        <ol class="home-deck__steps">
          <li v-for="(step, i) in loopSteps" :key="step">
            <span>{{ step }}</span>
            <span v-if="i < loopSteps.length - 1" class="home-deck__step-sep" aria-hidden="true">·</span>
          </li>
        </ol>
      </div>
    </section>

    <section v-if="uiStore.demoMode" class="home-pitch animate-fade-in">
      <RouterLink to="/report">Report</RouterLink>
      <RouterLink to="/dashboard">Dashboard</RouterLink>
      <RouterLink to="/audit">Audit</RouterLink>
      <RouterLink to="/report/status/demo-report-pothole-001">Tracking</RouterLink>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import AppLogo from '@/components/common/AppLogo.vue';
import AppShell from '@/layouts/AppShell.vue';
import { useUiStore } from '@/stores/ui';

const uiStore = useUiStore();
const loopSteps = ['Detect', 'Verify', 'Route', 'Resolve', 'Measure'];

const stats = [
  { value: 'Nationwide', label: 'Kosovo coverage' },
  { value: 'AI + Human', label: 'Review model' },
  { value: 'Real-time', label: 'Command center' },
];

const tiles = [
  { to: '/report', index: '01', tone: 'citizen', title: 'Citizen report' },
  { to: '/dashboard', index: '02', tone: 'dashboard', title: 'Command dashboard' },
  { to: '/audit', index: '03', tone: 'audit', title: 'Street audit' },
];
</script>

<style scoped>
.home-hero {
  position: relative;
  display: grid;
  place-items: center;
  min-height: clamp(22rem, 52vh, 34rem);
  padding: clamp(2rem, 5vw, 3.5rem) 0 clamp(1.5rem, 3vw, 2rem);
  text-align: center;
}

.home-hero__glow {
  position: absolute;
  inset: 15% 22%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(47, 93, 80, 0.16) 0%, transparent 65%);
  animation: glow-pulse 4s ease-in-out infinite;
  pointer-events: none;
}

.home-hero__ring {
  position: absolute;
  top: 4%;
  width: clamp(14rem, 32vw, 20rem);
  aspect-ratio: 1;
  border: 1px dashed rgba(47, 93, 80, 0.18);
  border-radius: 50%;
  animation: spin-slow 48s linear infinite;
  pointer-events: none;
}

.home-hero__content {
  position: relative;
  z-index: 1;
  display: grid;
  gap: var(--space-3);
  justify-items: center;
  width: min(100%, 40rem);
  margin-inline: auto;
  padding-top: var(--space-4);
}

.home-hero__logo :deep(.app-logo__sizer) {
  height: clamp(6.5rem, 24vw, 10.5rem);
}

.home-hero__logo {
  margin-bottom: var(--space-3);
}

.home-hero__title {
  margin: var(--space-3) 0 0;
  max-width: 14ch;
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 5.5vw, 3.5rem);
  line-height: 1.04;
  letter-spacing: -0.05em;
}

.home-hero__lead {
  margin: 0;
  max-width: 32rem;
  color: var(--text-secondary);
  font-size: clamp(0.92rem, 1.8vw, 1.05rem);
  line-height: 1.55;
}

.home-hero__actions {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
  padding: 0.35rem;
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.5);
  backdrop-filter: blur(10px);
}

.home-hero__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.35rem;
  padding: 0 1.1rem;
  border-radius: var(--radius-pill);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 850;
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    box-shadow var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.home-hero__cta:hover {
  transform: translateY(-1px);
}

.home-hero__cta--primary {
  color: var(--text-inverse);
  background: linear-gradient(135deg, #2f5d50 0%, #244c42 100%);
  box-shadow: 0 8px 20px rgba(47, 93, 80, 0.22);
}

.home-hero__cta:not(.home-hero__cta--primary):hover {
  background: rgba(47, 93, 80, 0.08);
}

/* Compact footer deck */
.home-deck {
  display: grid;
  gap: var(--space-3);
  padding: var(--space-4);
  max-width: 56rem;
  margin-inline: auto;
}

.home-deck__stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
  justify-content: center;
}

.home-deck__stat {
  display: inline-flex;
  gap: 0.4rem;
  align-items: baseline;
  font-size: var(--text-xs);
}

.home-deck__stat strong {
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 850;
  letter-spacing: -0.02em;
}

.home-deck__stat span {
  color: var(--text-muted);
  font-weight: 700;
}

.home-deck__divider {
  height: 1px;
  background: rgba(23, 33, 26, 0.07);
}

.home-deck__nav {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-2);
}

.home-deck__link {
  display: flex;
  gap: 0.45rem;
  align-items: center;
  min-height: 2.5rem;
  padding: 0.55rem 0.75rem;
  border: 1px solid rgba(23, 33, 26, 0.07);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.45);
  font-size: var(--text-xs);
  font-weight: 800;
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    border-color var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.home-deck__link--citizen { --accent: var(--color-municipal-green); }
.home-deck__link--dashboard { --accent: var(--color-resolved-blue); }
.home-deck__link--audit { --accent: var(--color-amber-signal); }

.home-deck__link:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--accent) 35%, transparent);
  background: rgba(255, 253, 247, 0.72);
}

.home-deck__index {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.1em;
}

.home-deck__link-title {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.home-deck__arrow {
  color: var(--accent);
  font-size: 0.85rem;
  opacity: 0.7;
  transition: transform var(--motion-fast) ease;
}

.home-deck__link:hover .home-deck__arrow {
  transform: translateX(2px);
  opacity: 1;
}

.home-deck__pipeline {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  align-items: center;
  justify-content: center;
}

.home-deck__pipeline-label {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.home-deck__steps {
  display: flex;
  flex-wrap: wrap;
  gap: 0.15rem;
  align-items: center;
  margin: 0;
  padding: 0;
  list-style: none;
}

.home-deck__steps li {
  display: inline-flex;
  align-items: center;
}

.home-deck__steps span:first-child {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 750;
}

.home-deck__step-sep {
  margin: 0 0.35rem;
  color: rgba(23, 33, 26, 0.25);
  font-weight: 900;
}

.home-pitch {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
  padding-top: var(--space-2);
}

.home-pitch a {
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-pill);
  color: var(--text-muted);
  background: rgba(255, 247, 225, 0.6);
  font-size: 0.72rem;
  font-weight: 800;
}

@media (max-width: 640px) {
  .home-deck__nav {
    grid-template-columns: 1fr;
  }

  .home-deck__stat {
    flex: 1 1 100%;
    justify-content: center;
  }
}
</style>
