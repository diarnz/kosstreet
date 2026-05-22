<template>
  <div class="app-shell surface-grid">
    <PrimaryNav />
    <main class="app-shell__main" :class="`app-shell__main--${contentWidth}`">
      <PitchModeBanner v-if="uiStore.demoMode" compact class="app-shell__pitch-banner" data-mode="demo" />
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import PitchModeBanner from '@/components/common/PitchModeBanner.vue';
import PrimaryNav from '@/components/navigation/PrimaryNav.vue';
import { useUiStore } from '@/stores/ui';

const uiStore = useUiStore();

withDefaults(
  defineProps<{
    contentWidth?: 'narrow' | 'default' | 'wide';
  }>(),
  {
    contentWidth: 'default',
  },
);
</script>

<style scoped>
.app-shell {
  position: relative;
  overflow-x: hidden;
  min-height: 100vh;
  padding: clamp(1rem, 3vw, 2rem);
  background:
    radial-gradient(circle at 8% 4%, rgba(217, 144, 47, 0.18), transparent 30rem),
    radial-gradient(circle at 92% 16%, rgba(47, 93, 80, 0.13), transparent 28rem),
    linear-gradient(135deg, var(--surface-app) 0%, var(--color-sage-surface) 100%);
}

.app-shell::before {
  content: "";
  position: fixed;
  inset: auto -8rem -12rem auto;
  width: 28rem;
  height: 28rem;
  pointer-events: none;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 46% 54% 58% 42%;
  transform: rotate(-18deg);
}

.app-shell__main {
  position: relative;
  width: min(100%, 1120px);
  margin: var(--space-10) auto 0;
  padding: clamp(1.4rem, 4vw, 4rem);
  border: var(--border-soft);
  border-radius: var(--radius-xl);
  background: var(--surface-panel);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(14px);
}

.app-shell__main--narrow {
  width: min(100%, 860px);
}

.app-shell__main--wide {
  width: min(100%, 1240px);
}

.app-shell__pitch-banner {
  margin-bottom: var(--space-6);
}

@media (max-width: 620px) {
  .app-shell {
    padding: var(--space-4);
  }

  .app-shell__main {
    margin-top: var(--space-6);
    border-radius: var(--radius-lg);
  }
}
</style>
