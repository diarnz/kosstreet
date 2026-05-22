<template>
  <div class="app-shell">
    <div class="app-shell__bg" aria-hidden="true">
      <span class="app-shell__orb app-shell__orb--green" />
      <span class="app-shell__orb app-shell__orb--amber" />
      <span class="app-shell__orb app-shell__orb--blue" />
      <div class="app-shell__grid" />
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
  background: #ebe6dc;
}

.app-shell__bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.app-shell__orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: float-orb 18s ease-in-out infinite;
}

.app-shell__orb--green {
  top: -8rem;
  left: -6rem;
  width: 28rem;
  height: 28rem;
  background: radial-gradient(circle, rgba(47, 93, 80, 0.35) 0%, transparent 70%);
}

.app-shell__orb--amber {
  top: 20%;
  right: -10rem;
  width: 32rem;
  height: 32rem;
  background: radial-gradient(circle, rgba(217, 144, 47, 0.28) 0%, transparent 70%);
  animation-delay: -6s;
}

.app-shell__orb--blue {
  bottom: -12rem;
  left: 30%;
  width: 36rem;
  height: 36rem;
  background: radial-gradient(circle, rgba(63, 110, 140, 0.2) 0%, transparent 70%);
  animation-delay: -12s;
}

.app-shell__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(23, 33, 26, 0.028) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23, 33, 26, 0.028) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 85%);
}

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

.app-shell__container--narrow {
  max-width: 720px;
}

.app-shell__container--default {
  max-width: 1080px;
}

.app-shell__container--wide {
  max-width: 1440px;
}

.app-shell__container--full {
  max-width: none;
}
</style>
