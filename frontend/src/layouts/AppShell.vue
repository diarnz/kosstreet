<template>
  <div class="app-shell">
    <div class="app-shell__bg" aria-hidden="true">
      <span class="app-shell__orb app-shell__orb--1" />
      <span class="app-shell__orb app-shell__orb--2" />
      <span class="app-shell__orb app-shell__orb--3" />
      <span class="app-shell__orb app-shell__orb--4" />
      <span class="app-shell__orb app-shell__orb--5" />
      <div class="app-shell__aurora" />
      <div class="app-shell__grid" />
      <div class="app-shell__streaks">
        <span class="app-shell__streak" />
        <span class="app-shell__streak app-shell__streak--b" />
        <span class="app-shell__streak app-shell__streak--c" />
      </div>
      <div class="app-shell__noise" />
    </div>

    <PrimaryNav />
    <main class="app-shell__main">
      <div class="app-shell__container animate-fade-up" :class="`app-shell__container--${contentWidth}`">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import PrimaryNav from '@/components/navigation/PrimaryNav.vue';

withDefaults(
  defineProps<{
    contentWidth?: 'narrow' | 'default' | 'wide' | 'full';
  }>(),
  {
    contentWidth: 'default',
  },
);
</script>

<style scoped>
.app-shell {
  --shell-pad-x: clamp(1rem, 4vw, 2.5rem);
  --shell-pad-y: clamp(1rem, 3vw, 1.75rem);

  position: relative;
  isolation: isolate;
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
  overflow-x: hidden;
  background: #e8e2d6;
}

/* ─── Background layer ─── */
.app-shell__bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

/* Aurora orbs */
.app-shell__orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
}

.app-shell__orb--1 {
  top: -10rem;
  left: -8rem;
  width: 36rem;
  height: 36rem;
  background: radial-gradient(circle, rgba(47, 93, 80, 0.38) 0%, transparent 68%);
  animation: aurora-drift 22s ease-in-out infinite;
}

.app-shell__orb--2 {
  top: 10%;
  right: -12rem;
  width: 42rem;
  height: 42rem;
  background: radial-gradient(circle, rgba(217, 144, 47, 0.26) 0%, transparent 68%);
  animation: aurora-slow 28s ease-in-out infinite;
  animation-delay: -8s;
}

.app-shell__orb--3 {
  bottom: -16rem;
  left: 22%;
  width: 48rem;
  height: 48rem;
  background: radial-gradient(circle, rgba(63, 110, 140, 0.22) 0%, transparent 68%);
  animation: aurora-drift 34s ease-in-out infinite;
  animation-delay: -14s;
}

.app-shell__orb--4 {
  top: 35%;
  left: 55%;
  width: 30rem;
  height: 30rem;
  background: radial-gradient(circle, rgba(82, 120, 102, 0.18) 0%, transparent 68%);
  animation: aurora-slow 26s ease-in-out infinite;
  animation-delay: -5s;
}

.app-shell__orb--5 {
  bottom: 5%;
  right: 8%;
  width: 26rem;
  height: 26rem;
  background: radial-gradient(circle, rgba(200, 76, 58, 0.1) 0%, transparent 68%);
  animation: aurora-drift 18s ease-in-out infinite;
  animation-delay: -20s;
}

/* Rotating conic aurora sweep */
.app-shell__aurora {
  position: absolute;
  inset: -30%;
  opacity: 0.055;
  background: conic-gradient(
    from 220deg at 45% 38%,
    rgba(47, 93, 80, 1),
    rgba(217, 144, 47, 0.6),
    rgba(63, 110, 140, 0.8),
    rgba(47, 93, 80, 0.4),
    rgba(47, 93, 80, 1)
  );
  filter: blur(80px);
  animation: spin-slow 80s linear infinite;
}

/* Dot-grid */
.app-shell__grid {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle, rgba(23, 33, 26, 0.2) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(ellipse 80% 70% at 50% 40%, black 20%, transparent 80%);
  opacity: 0.22;
  animation: mesh-float 18s ease-in-out infinite;
}

/* Light-speed streaks */
.app-shell__streaks {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.app-shell__streak {
  position: absolute;
  left: 0;
  width: 35%;
  height: 1px;
  top: 22%;
  background: linear-gradient(90deg, transparent 0%, rgba(47, 93, 80, 0.5) 40%, rgba(47, 93, 80, 0.5) 60%, transparent 100%);
  animation: streak 14s linear 0s infinite;
  opacity: 0;
}

.app-shell__streak--b {
  top: 54%;
  width: 22%;
  animation-delay: -5s;
  animation-duration: 11s;
  background: linear-gradient(90deg, transparent 0%, rgba(217, 144, 47, 0.4) 40%, rgba(217, 144, 47, 0.4) 60%, transparent 100%);
}

.app-shell__streak--c {
  top: 78%;
  width: 45%;
  animation-delay: -10s;
  animation-duration: 18s;
  background: linear-gradient(90deg, transparent 0%, rgba(63, 110, 140, 0.35) 40%, rgba(63, 110, 140, 0.35) 60%, transparent 100%);
}

/* Film grain noise */
.app-shell__noise {
  position: absolute;
  inset: 0;
  opacity: 0.028;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='256' height='256'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='256' height='256' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 180px 180px;
  mix-blend-mode: multiply;
}

/* ─── Shell layout ─── */
.app-shell__main {
  position: relative;
  z-index: 1;
  display: grid;
  align-content: start;
  gap: var(--space-4);
  padding: var(--shell-pad-y) var(--shell-pad-x) clamp(2rem, 5vw, 3rem);
}

.app-shell__container {
  width: 100%;
  margin-inline: auto;
}

.app-shell__container--narrow  { max-width: 720px; }
.app-shell__container--default { max-width: 1080px; }
.app-shell__container--wide    { max-width: 1440px; }
.app-shell__container--full    { max-width: none; }

@media (prefers-reduced-motion: reduce) {
  .app-shell__orb,
  .app-shell__aurora,
  .app-shell__grid,
  .app-shell__streak {
    animation: none;
  }
}
</style>
