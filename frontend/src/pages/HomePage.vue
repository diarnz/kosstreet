<template>
  <AppShell content-width="full">
    <!-- ── Hero ─────────────────────────────────────────── -->
    <section class="home-hero animate-scale-in">
      <div class="home-hero__bg" aria-hidden="true">
        <span class="home-hero__ring home-hero__ring--1" />
        <span class="home-hero__ring home-hero__ring--2" />
        <span class="home-hero__ring home-hero__ring--3" />
        <span class="home-hero__ring home-hero__ring--4" />
        <span class="home-hero__orbit-track" aria-hidden="true">
          <span class="home-hero__orbit-dot" />
        </span>
        <span class="home-hero__dot home-hero__dot--1" />
        <span class="home-hero__dot home-hero__dot--2" />
        <span class="home-hero__dot home-hero__dot--3" />
        <span class="home-hero__dot home-hero__dot--4" />
        <span class="home-hero__dot home-hero__dot--5" />
        <span class="home-hero__dot home-hero__dot--6" />
        <span class="home-hero__dot home-hero__dot--7" />
        <span class="home-hero__dot home-hero__dot--8" />
        <div class="home-hero__glow" />
      </div>

      <div class="home-hero__content">
        <AppLogo class="home-hero__logo" size="hero" animated />

        <p class="home-hero__eyebrow">Civic intelligence · Kosovo</p>

        <h1 class="home-hero__title">
          <span class="gradient-sweep-text">Streets</span>
          <br class="home-hero__br" />
          reimagined.
        </h1>

        <p class="home-hero__lead">
          One platform to report street issues, command municipal workflows,<br class="home-hero__br" />
          and review AI street audits nationwide.
        </p>

        <div class="home-hero__actions">
          <RouterLink class="home-hero__cta home-hero__cta--primary" to="/report">
            Report an issue
          </RouterLink>
          <RouterLink class="home-hero__cta" to="/dashboard">
            Open dashboard
          </RouterLink>
        </div>

        <div class="home-hero__stats">
          <span class="home-hero__stat">
            <strong>Nationwide</strong>
            <span>Kosovo coverage</span>
          </span>
          <span class="home-hero__stat-sep" aria-hidden="true" />
          <span class="home-hero__stat">
            <strong>AI + Human</strong>
            <span>Review model</span>
          </span>
          <span class="home-hero__stat-sep" aria-hidden="true" />
          <span class="home-hero__stat">
            <strong>Real-time</strong>
            <span>Command center</span>
          </span>
        </div>
      </div>
    </section>

    <!-- ── Deck ─────────────────────────────────────────── -->
    <section class="home-deck animate-fade-up" aria-label="Platform overview">
      <nav class="home-deck__nav" aria-label="Product surfaces">
        <RouterLink
          v-for="tile in tiles"
          :key="tile.to"
          :to="tile.to"
          class="home-deck__tile"
          :class="`home-deck__tile--${tile.tone}`"
        >
          <span class="home-deck__tile-index" aria-hidden="true">{{ tile.index }}</span>
          <div class="home-deck__tile-body">
            <strong class="home-deck__tile-title">{{ tile.title }}</strong>
            <span class="home-deck__tile-sub">{{ tile.sub }}</span>
          </div>
          <span class="home-deck__tile-arrow" aria-hidden="true">→</span>
          <span class="home-deck__tile-shine" aria-hidden="true" />
        </RouterLink>
      </nav>

      <div class="home-deck__pipeline">
        <span class="home-deck__pipeline-label">Pipeline</span>
        <ol class="home-deck__steps">
          <li v-for="(step, i) in loopSteps" :key="step">
            <span class="home-deck__step-name">{{ step }}</span>
            <span v-if="i < loopSteps.length - 1" class="home-deck__step-sep" aria-hidden="true" />
          </li>
        </ol>
      </div>
    </section>

  </AppShell>
</template>

<script setup lang="ts">
import AppLogo from '@/components/common/AppLogo.vue';
import AppShell from '@/layouts/AppShell.vue';

const loopSteps = ['Detect', 'Verify', 'Route', 'Resolve', 'Measure'];

const tiles = [
  { to: '/report',    index: '01', tone: 'citizen',   title: 'Citizen report',      sub: 'Submit a street issue' },
  { to: '/dashboard', index: '02', tone: 'dashboard', title: 'Command dashboard',   sub: 'Municipal triage & ops' },
  { to: '/audit',     index: '03', tone: 'audit',     title: 'Street audit',        sub: 'AI-powered scanning' },
];
</script>

<style scoped>
/* ─── Hero ─────────────────────────────────────────── */
.home-hero {
  position: relative;
  display: grid;
  place-items: center;
  min-height: clamp(26rem, 66vh, 44rem);
  padding: clamp(2.5rem, 6vw, 4.5rem) 0 clamp(2rem, 4vw, 3rem);
  text-align: center;
  overflow: hidden;
}

/* Decorative background layer */
.home-hero__bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* Rings */
.home-hero__ring {
  position: absolute;
  top: 50%;
  left: 50%;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.home-hero__ring--1 {
  width: clamp(9rem, 20vw, 14rem);
  aspect-ratio: 1;
  border: 1.5px solid rgba(47, 93, 80, 0.32);
  animation: spin-slow 36s linear infinite;
  box-shadow: 0 0 18px rgba(47, 93, 80, 0.1), inset 0 0 18px rgba(47, 93, 80, 0.06);
}

.home-hero__ring--2 {
  width: clamp(16rem, 35vw, 24rem);
  aspect-ratio: 1;
  border: 1px dashed rgba(47, 93, 80, 0.2);
  animation: spin-reverse 52s linear infinite;
}

.home-hero__ring--3 {
  width: clamp(24rem, 52vw, 38rem);
  aspect-ratio: 1;
  border: 1px solid rgba(47, 93, 80, 0.1);
  animation: spin-slow 80s linear infinite;
  border-style: dashed;
}

.home-hero__ring--4 {
  width: clamp(34rem, 72vw, 54rem);
  aspect-ratio: 1;
  border: 1px solid rgba(47, 93, 80, 0.06);
  animation: spin-reverse 120s linear infinite;
}

/* Orbit dot */
.home-hero__orbit-track {
  position: absolute;
  top: 50%;
  left: 50%;
  width: clamp(24rem, 52vw, 38rem);
  aspect-ratio: 1;
  transform: translate(-50%, -50%);
  animation: spin-slow 20s linear infinite;
  pointer-events: none;
}

.home-hero__orbit-dot {
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  display: block;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--color-municipal-green);
  box-shadow:
    0 0 0 3px rgba(47, 93, 80, 0.2),
    0 0 12px rgba(47, 93, 80, 0.7),
    0 0 28px rgba(47, 93, 80, 0.35);
}

/* Floating dots */
.home-hero__dot {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.home-hero__dot--1  { top: 12%; left: 8%;   width: 5px;  height: 5px;  background: rgba(47, 93, 80, 0.5);   animation: dot-float 6s   ease-in-out 0s    infinite; }
.home-hero__dot--2  { top: 20%; left: 88%;  width: 4px;  height: 4px;  background: rgba(217, 144, 47, 0.5); animation: dot-float 7.5s ease-in-out 1.2s  infinite; }
.home-hero__dot--3  { top: 72%; left: 6%;   width: 6px;  height: 6px;  background: rgba(63, 110, 140, 0.4); animation: dot-float 5.5s ease-in-out 2.8s  infinite; }
.home-hero__dot--4  { top: 78%; left: 90%;  width: 4px;  height: 4px;  background: rgba(47, 93, 80, 0.4);   animation: dot-float 8s   ease-in-out 0.5s  infinite; }
.home-hero__dot--5  { top: 8%;  left: 48%;  width: 3px;  height: 3px;  background: rgba(217, 144, 47, 0.6); animation: dot-float 9s   ease-in-out 3.5s  infinite; }
.home-hero__dot--6  { top: 88%; left: 44%;  width: 5px;  height: 5px;  background: rgba(47, 93, 80, 0.35);  animation: dot-float 6.5s ease-in-out 1.8s  infinite; }
.home-hero__dot--7  { top: 35%; left: 3%;   width: 3px;  height: 3px;  background: rgba(200, 76, 58, 0.35); animation: dot-float 7s   ease-in-out 4.2s  infinite; }
.home-hero__dot--8  { top: 55%; left: 95%;  width: 4px;  height: 4px;  background: rgba(47, 93, 80, 0.45);  animation: dot-float 8.5s ease-in-out 0.9s  infinite; }

/* Central radial glow */
.home-hero__glow {
  position: absolute;
  inset: 18% 20%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(47, 93, 80, 0.14) 0%, transparent 65%);
  animation: glow-pulse 5s ease-in-out infinite;
}

/* Content */
.home-hero__content {
  position: relative;
  z-index: 1;
  display: grid;
  gap: var(--space-3);
  justify-items: center;
  width: min(100%, 46rem);
  margin-inline: auto;
  padding: 0 var(--space-4);
}

.home-hero__logo {
  margin-bottom: var(--space-2);
}

.home-hero__logo :deep(.app-logo__sizer) {
  height: clamp(7rem, 26vw, 12rem);
}

.home-hero__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.home-hero__title {
  margin: var(--space-2) 0 0;
  font-family: var(--font-display);
  font-size: clamp(3rem, 7.5vw, 5.8rem);
  line-height: 1.0;
  letter-spacing: -0.06em;
}

.home-hero__br {
  display: none;
}

@media (min-width: 520px) {
  .home-hero__br { display: block; }
}

.home-hero__lead {
  margin: 0;
  max-width: 36rem;
  color: var(--text-secondary);
  font-size: clamp(0.9rem, 1.7vw, 1.02rem);
  line-height: 1.6;
}

/* CTA actions */
.home-hero__actions {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  justify-content: center;
  align-items: center;
  padding: 0.32rem;
  border: 1px solid rgba(23, 33, 26, 0.09);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.48);
  backdrop-filter: blur(12px);
  box-shadow:
    0 4px 24px rgba(23, 33, 26, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.home-hero__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.5rem;
  padding: 0 1.35rem;
  border-radius: var(--radius-pill);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 900;
  letter-spacing: 0.005em;
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    box-shadow var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.home-hero__cta--primary {
  color: #fff;
  background: linear-gradient(140deg, #3a7062 0%, #2f5d50 50%, #224840 100%);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
    0 8px 24px rgba(47, 93, 80, 0.32),
    0 2px 6px rgba(47, 93, 80, 0.5);
}

.home-hero__cta--primary:hover {
  transform: translateY(-2px);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.12) inset,
    0 12px 32px rgba(47, 93, 80, 0.42),
    0 3px 8px rgba(47, 93, 80, 0.55);
}

.home-hero__cta:not(.home-hero__cta--primary):hover {
  background: rgba(47, 93, 80, 0.09);
  transform: translateY(-1px);
}

/* Inline stats */
.home-hero__stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  align-items: center;
  justify-content: center;
  padding-top: var(--space-2);
}

.home-hero__stat {
  display: inline-flex;
  gap: 0.35rem;
  align-items: baseline;
}

.home-hero__stat strong {
  color: var(--text-primary);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: -0.01em;
}

.home-hero__stat span {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 700;
}

.home-hero__stat-sep {
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: rgba(23, 33, 26, 0.2);
}

/* ─── Deck ─────────────────────────────────────────── */
.home-deck {
  display: grid;
  gap: var(--space-4);
  max-width: 62rem;
  margin-inline: auto;
  width: 100%;
}

.home-deck__nav {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
}

.home-deck__tile {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-4) var(--space-3);
  border: 1px solid rgba(23, 33, 26, 0.09);
  border-radius: var(--radius-lg);
  background: rgba(255, 253, 247, 0.5);
  backdrop-filter: blur(14px);
  overflow: hidden;
  transition:
    transform var(--motion-base) var(--ease-out-expo),
    border-color var(--motion-base) ease,
    box-shadow var(--motion-base) ease,
    background var(--motion-base) ease;
  animation: tile-enter var(--motion-slow) var(--ease-spring) both;
}

.home-deck__tile:nth-child(1) { animation-delay: 0ms; }
.home-deck__tile:nth-child(2) { animation-delay: 80ms; }
.home-deck__tile:nth-child(3) { animation-delay: 160ms; }

.home-deck__tile--citizen   { --accent: var(--color-municipal-green); }
.home-deck__tile--dashboard { --accent: var(--color-resolved-blue); }
.home-deck__tile--audit     { --accent: var(--color-amber-signal); }

.home-deck__tile:hover {
  transform: translateY(-4px);
  border-color: color-mix(in srgb, var(--accent) 38%, transparent);
  background: rgba(255, 253, 247, 0.8);
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--accent) 15%, transparent),
    0 20px 48px rgba(23, 33, 26, 0.12),
    0 4px 12px color-mix(in srgb, var(--accent) 14%, transparent);
}

/* Hover shine sweep */
.home-deck__tile-shine {
  position: absolute;
  inset: 0;
  opacity: 0;
  background: linear-gradient(
    135deg,
    transparent 30%,
    color-mix(in srgb, var(--accent) 8%, transparent) 50%,
    transparent 70%
  );
  transition: opacity var(--motion-base) ease;
  pointer-events: none;
}

.home-deck__tile:hover .home-deck__tile-shine {
  opacity: 1;
}

/* Large watermark index */
.home-deck__tile-index {
  display: block;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  color: color-mix(in srgb, var(--accent) 75%, transparent);
  text-transform: uppercase;
}

.home-deck__tile-body {
  display: grid;
  gap: 0.2rem;
  flex: 1;
}

.home-deck__tile-title {
  font-size: var(--text-base);
  font-weight: 900;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.home-deck__tile-sub {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-weight: 700;
}

.home-deck__tile-arrow {
  align-self: flex-end;
  color: var(--accent);
  font-size: 1rem;
  font-weight: 900;
  opacity: 0.65;
  transition: transform var(--motion-fast) ease, opacity var(--motion-fast) ease;
}

.home-deck__tile:hover .home-deck__tile-arrow {
  transform: translateX(4px);
  opacity: 1;
}

/* Pipeline strip */
.home-deck__pipeline {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-4);
  border: 1px solid rgba(23, 33, 26, 0.07);
  border-radius: var(--radius-lg);
  background: rgba(255, 253, 247, 0.38);
  backdrop-filter: blur(10px);
}

.home-deck__pipeline-label {
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.home-deck__steps {
  display: flex;
  flex-wrap: wrap;
  gap: 0.1rem;
  align-items: center;
  margin: 0;
  padding: 0;
  list-style: none;
}

.home-deck__steps li {
  display: inline-flex;
  align-items: center;
  gap: 0.1rem;
}

.home-deck__step-name {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 750;
}

.home-deck__step-sep {
  display: inline-block;
  width: 14px;
  height: 1px;
  background: linear-gradient(90deg, rgba(47, 93, 80, 0.3), rgba(217, 144, 47, 0.3));
  margin: 0 0.25rem;
  vertical-align: middle;
}


/* ─── Responsive ─── */
@media (max-width: 720px) {
  .home-deck__nav {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .home-hero__stats {
    flex-direction: column;
    gap: var(--space-1);
  }

  .home-hero__stat-sep {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .home-hero__ring,
  .home-hero__orbit-track,
  .home-hero__dot,
  .home-hero__glow {
    animation: none;
  }
}
</style>
