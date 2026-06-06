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

        <div class="home-hero__stats">
          <div v-for="stat in heroStats" :key="stat.label" class="home-hero__stat">
            <span class="home-hero__stat-icon" aria-hidden="true">
              <component :is="stat.icon" />
            </span>
            <span class="home-hero__stat-copy">
              <strong>{{ stat.label }}</strong>
              <span>{{ stat.sub }}</span>
            </span>
          </div>
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
          <span class="home-deck__tile-icon" aria-hidden="true">
            <component :is="tile.icon" />
          </span>
          <div class="home-deck__tile-body">
            <span class="home-deck__tile-index">{{ tile.index }}</span>
            <strong class="home-deck__tile-title">{{ tile.title }}</strong>
            <span class="home-deck__tile-sub">{{ tile.sub }}</span>
          </div>
          <span class="home-deck__tile-arrow" aria-hidden="true">
            <svg viewBox="0 0 16 16" fill="none">
              <path d="M3 8h9M9 5l3 3-3 3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <span class="home-deck__tile-shine" aria-hidden="true" />
        </RouterLink>
      </nav>

      <div class="home-deck__pipeline">
        <span class="home-deck__pipeline-label">Pipeline</span>
        <ol class="home-deck__steps">
          <li v-for="(step, i) in loopSteps" :key="step.id">
            <span class="home-deck__step-chip">
              <span class="home-deck__step-icon" aria-hidden="true">
                <component :is="step.icon" />
              </span>
              <span class="home-deck__step-name">{{ step.label }}</span>
            </span>
            <span v-if="i < loopSteps.length - 1" class="home-deck__step-sep" aria-hidden="true">
              <svg viewBox="0 0 16 16" fill="none">
                <path d="M4 8h8M9 5l3 3-3 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </span>
          </li>
        </ol>
      </div>
    </section>

  </AppShell>
</template>

<script setup lang="ts">
import { defineComponent, h } from 'vue';
import AppLogo from '@/components/common/AppLogo.vue';
import AppShell from '@/layouts/AppShell.vue';

const iconProps = {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
};

function makeIcon(children: ReturnType<typeof h>[]) {
  return defineComponent({
    render: () => h('svg', iconProps, children),
  });
}

const IconCoverage = makeIcon([
  h('circle', { cx: '12', cy: '12', r: '9', stroke: 'currentColor', 'stroke-width': '1.6' }),
  h('path', {
    d: 'M3 12h18M12 3c2.8 2.4 4.5 5.6 4.5 9s-1.7 6.6-4.5 9M12 3c-2.8 2.4-4.5 5.6-4.5 9s1.7 6.6 4.5 9',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linecap': 'round',
  }),
]);

const IconAiReview = makeIcon([
  h('path', {
    d: 'M12 3l1.4 4.3H18l-3.6 2.6 1.4 4.3L12 11.6 8.2 14.2l1.4-4.3L6 7.3h4.6L12 3z',
    stroke: 'currentColor',
    'stroke-width': '1.5',
    'stroke-linejoin': 'round',
  }),
  h('circle', { cx: '18.5', cy: '6.5', r: '1.2', fill: 'currentColor' }),
  h('circle', { cx: '5.5', cy: '17.5', r: '1.2', fill: 'currentColor' }),
]);

const IconRealtime = makeIcon([
  h('circle', { cx: '12', cy: '12', r: '8', stroke: 'currentColor', 'stroke-width': '1.6' }),
  h('path', {
    d: 'M12 7v5l3 2',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
  }),
  h('circle', { cx: '12', cy: '12', r: '1.4', fill: 'currentColor' }),
]);

const IconReport = makeIcon([
  h('path', {
    d: 'M8 4h8a2 2 0 012 2v12l-6-3-6 3V6a2 2 0 012-2z',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linejoin': 'round',
  }),
  h('path', { d: 'M10 9h4M10 12h4', stroke: 'currentColor', 'stroke-width': '1.6', 'stroke-linecap': 'round' }),
]);

const IconDashboard = makeIcon([
  h('rect', { x: '4', y: '4', width: '7', height: '7', rx: '1.6', stroke: 'currentColor', 'stroke-width': '1.6' }),
  h('rect', { x: '13', y: '4', width: '7', height: '4', rx: '1.6', stroke: 'currentColor', 'stroke-width': '1.6' }),
  h('rect', { x: '13', y: '11', width: '7', height: '9', rx: '1.6', stroke: 'currentColor', 'stroke-width': '1.6' }),
  h('rect', { x: '4', y: '14', width: '7', height: '6', rx: '1.6', stroke: 'currentColor', 'stroke-width': '1.6' }),
]);

const IconAudit = makeIcon([
  h('path', {
    d: 'M5 7h14M5 12h14M5 17h9',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linecap': 'round',
  }),
  h('circle', { cx: '18', cy: '17', r: '2.2', stroke: 'currentColor', 'stroke-width': '1.6' }),
  h('path', {
    d: 'M19.6 18.6l1.8 1.8',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linecap': 'round',
  }),
]);

const IconDetect = makeIcon([
  h('circle', { cx: '11', cy: '11', r: '6', stroke: 'currentColor', 'stroke-width': '1.6' }),
  h('path', { d: 'M16 16l4 4', stroke: 'currentColor', 'stroke-width': '1.6', 'stroke-linecap': 'round' }),
]);

const IconVerify = makeIcon([
  h('path', {
    d: 'M6 12l3.2 3.2L18 7',
    stroke: 'currentColor',
    'stroke-width': '1.8',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
  }),
]);

const IconRoute = makeIcon([
  h('path', {
    d: 'M5 6c0-1.7 1.3-3 3-3s3 1.3 3 3-1.3 3-3 3H8v4',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
  }),
  h('path', {
    d: 'M16 14c0 1.7-1.3 3-3 3s-3-1.3-3-3 1.3-3 3-3h1V8',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
  }),
]);

const IconResolve = makeIcon([
  h('path', {
    d: 'M12 3l2.2 4.5 5 .7-3.6 3.5.9 5-4.5-2.4-4.5 2.4.9-5L4.8 8.2l5-.7L12 3z',
    stroke: 'currentColor',
    'stroke-width': '1.5',
    'stroke-linejoin': 'round',
  }),
]);

const IconMeasure = makeIcon([
  h('path', {
    d: 'M5 18V8M9 18V5M13 18v-7M17 18v-4',
    stroke: 'currentColor',
    'stroke-width': '1.6',
    'stroke-linecap': 'round',
  }),
]);

const heroStats = [
  { label: 'Nationwide', sub: 'Kosovo coverage', icon: IconCoverage },
  { label: 'AI + Human', sub: 'Review model', icon: IconAiReview },
  { label: 'Real-time', sub: 'Command center', icon: IconRealtime },
];

const loopSteps = [
  { id: 'detect', label: 'Detect', icon: IconDetect },
  { id: 'verify', label: 'Verify', icon: IconVerify },
  { id: 'route', label: 'Route', icon: IconRoute },
  { id: 'resolve', label: 'Resolve', icon: IconResolve },
  { id: 'measure', label: 'Measure', icon: IconMeasure },
];

const tiles = [
  { to: '/report', index: '01', tone: 'citizen', title: 'Citizen report', sub: 'Submit a street issue', icon: IconReport },
  { to: '/dashboard', index: '02', tone: 'dashboard', title: 'Command dashboard', sub: 'Municipal triage & ops', icon: IconDashboard },
  { to: '/audit', index: '03', tone: 'audit', title: 'Street audit', sub: 'AI-powered scanning', icon: IconAudit },
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

/* Hero stat chips */
.home-hero__stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: stretch;
  justify-content: center;
  width: min(100%, 40rem);
  padding-top: var(--space-3);
}

.home-hero__stat {
  display: flex;
  gap: 0.65rem;
  align-items: center;
  min-width: 9.5rem;
  padding: 0.7rem 0.9rem;
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: var(--radius-lg);
  background: rgba(255, 253, 247, 0.55);
  backdrop-filter: blur(12px);
  box-shadow:
    0 8px 24px rgba(23, 33, 26, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
  text-align: left;
  transition:
    transform var(--motion-fast) var(--ease-out-expo),
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

.home-hero__stat:hover {
  transform: translateY(-2px);
  border-color: rgba(47, 93, 80, 0.22);
  box-shadow:
    0 12px 28px rgba(23, 33, 26, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.home-hero__stat-icon {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 2.35rem;
  height: 2.35rem;
  border-radius: var(--radius-md);
  color: var(--color-municipal-green);
  background: color-mix(in srgb, var(--color-municipal-green) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-municipal-green) 22%, transparent);
}

.home-hero__stat-icon svg {
  width: 1.2rem;
  height: 1.2rem;
}

.home-hero__stat:nth-child(2) .home-hero__stat-icon {
  color: var(--color-amber-signal);
  background: color-mix(in srgb, var(--color-amber-signal) 12%, transparent);
  border-color: color-mix(in srgb, var(--color-amber-signal) 22%, transparent);
}

.home-hero__stat:nth-child(3) .home-hero__stat-icon {
  color: var(--color-resolved-blue);
  background: color-mix(in srgb, var(--color-resolved-blue) 12%, transparent);
  border-color: color-mix(in srgb, var(--color-resolved-blue) 22%, transparent);
}

.home-hero__stat-copy {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.home-hero__stat-copy strong {
  color: var(--text-primary);
  font-size: var(--text-xs);
  font-weight: 900;
  letter-spacing: -0.01em;
}

.home-hero__stat-copy span {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 700;
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
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-4);
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

.home-deck__tile-icon {
  display: grid;
  place-items: center;
  width: 3.25rem;
  height: 3.25rem;
  border-radius: var(--radius-md);
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 11%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent) 24%, transparent);
  box-shadow:
    0 0 0 4px color-mix(in srgb, var(--accent) 6%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.35);
  transition:
    transform var(--motion-base) var(--ease-out-expo),
    box-shadow var(--motion-base) ease;
}

.home-deck__tile-icon svg {
  width: 1.45rem;
  height: 1.45rem;
}

.home-deck__tile:hover .home-deck__tile-icon {
  transform: scale(1.05);
  box-shadow:
    0 0 0 5px color-mix(in srgb, var(--accent) 10%, transparent),
    0 8px 20px color-mix(in srgb, var(--accent) 18%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.home-deck__tile-index {
  display: block;
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  color: color-mix(in srgb, var(--accent) 70%, transparent);
  text-transform: uppercase;
}

.home-deck__tile-body {
  display: grid;
  gap: 0.2rem;
  min-width: 0;
  text-align: left;
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
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  opacity: 0.85;
  transition: transform var(--motion-fast) ease, opacity var(--motion-fast) ease, background var(--motion-fast) ease;
}

.home-deck__tile-arrow svg {
  width: 1rem;
  height: 1rem;
}

.home-deck__tile:hover .home-deck__tile-arrow {
  transform: translateX(3px);
  opacity: 1;
  background: color-mix(in srgb, var(--accent) 16%, transparent);
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
  gap: 0.35rem;
}

.home-deck__step-chip {
  display: inline-flex;
  gap: 0.35rem;
  align-items: center;
  padding: 0.35rem 0.55rem 0.35rem 0.4rem;
  border: 1px solid rgba(23, 33, 26, 0.07);
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.45);
}

.home-deck__step-icon {
  display: grid;
  place-items: center;
  width: 1.35rem;
  height: 1.35rem;
  color: var(--color-municipal-green);
}

.home-deck__step-icon svg {
  width: 0.9rem;
  height: 0.9rem;
}

.home-deck__step-name {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 800;
}

.home-deck__step-sep {
  display: inline-grid;
  place-items: center;
  width: 1rem;
  height: 1rem;
  color: color-mix(in srgb, var(--color-municipal-green) 55%, transparent);
  opacity: 0.7;
}

.home-deck__step-sep svg {
  width: 0.75rem;
  height: 0.75rem;
}


/* ─── Responsive ─── */
@media (max-width: 720px) {
  .home-deck__nav {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .home-hero__stat {
    flex: 1 1 100%;
    min-width: 0;
  }

  .home-deck__tile {
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto;
  }

  .home-deck__tile-arrow {
    grid-column: 2;
    justify-self: end;
  }
}

@media (max-width: 480px) {
  .home-deck__steps {
    justify-content: center;
  }

  .home-deck__step-sep {
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
