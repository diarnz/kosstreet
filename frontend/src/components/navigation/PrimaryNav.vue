<template>
  <header class="site-header">
    <div class="site-header__inner">
      <RouterLink class="site-header__brand" to="/" aria-label="KoStreet home">
        <AppLogo size="sm" />
      </RouterLink>

      <nav class="site-header__nav" aria-label="Primary navigation">
        <RouterLink
          v-for="item in items"
          :key="item.to"
          class="site-header__link"
          :to="item.to"
        >
          <span class="site-header__link-text">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <button
        class="site-header__demo"
        :class="{ 'site-header__demo--active': uiStore.demoMode }"
        :aria-pressed="uiStore.demoMode"
        :aria-label="uiStore.demoMode ? 'Demo mode on' : 'Demo mode off'"
        type="button"
        @click="uiStore.toggleDemoMode"
      >
        Demo
      </button>
    </div>
    <div class="site-header__shine" aria-hidden="true" />
  </header>
</template>

<script setup lang="ts">
import AppLogo from '@/components/common/AppLogo.vue';
import { useUiStore } from '@/stores/ui';

const uiStore = useUiStore();

const items = [
  { to: '/', label: 'Home' },
  { to: '/report', label: 'Report' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/audit', label: 'Street Audit' },
];
</script>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: var(--z-nav);
  border-bottom: 1px solid rgba(255, 253, 247, 0.45);
  background: rgba(255, 253, 247, 0.72);
  backdrop-filter: blur(20px) saturate(1.2);
  box-shadow: 0 12px 40px rgba(23, 33, 26, 0.06);
}

.site-header__shine {
  position: absolute;
  inset: 0 0 auto;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 253, 247, 0.95), transparent);
  pointer-events: none;
}

.site-header__inner {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  justify-content: space-between;
  max-width: 1440px;
  margin-inline: auto;
  padding: 0.65rem clamp(1rem, 4vw, 2.5rem);
}

.site-header__brand {
  flex-shrink: 0;
  transition: transform var(--motion-fast) var(--ease-out-expo);
}

.site-header__brand:hover {
  transform: scale(1.03);
}

.site-header__nav {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  gap: 0.2rem;
  justify-content: center;
}

.site-header__link {
  position: relative;
  display: inline-flex;
  align-items: center;
  min-height: 2.45rem;
  padding: 0 1rem;
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 850;
  letter-spacing: 0.01em;
  transition:
    color var(--motion-fast) ease,
    background var(--motion-fast) ease;
}

.site-header__link::after {
  content: "";
  position: absolute;
  inset: auto 1rem -2px;
  height: 2px;
  border-radius: var(--radius-pill);
  background: var(--color-municipal-green);
  transform: scaleX(0);
  transition: transform var(--motion-fast) var(--ease-out-expo);
}

.site-header__link:hover {
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.08);
}

.site-header__link.router-link-active {
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.12);
}

.site-header__link.router-link-active::after {
  transform: scaleX(1);
}

.site-header__demo {
  display: inline-flex;
  gap: 0.45rem;
  flex-shrink: 0;
  align-items: center;
  min-height: 2.45rem;
  padding: 0 1rem;
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.55);
  font-size: var(--text-sm);
  font-weight: 850;
  cursor: pointer;
  transition:
    color var(--motion-fast) ease,
    background var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

.site-header__demo:hover {
  color: var(--text-primary);
  box-shadow: 0 8px 24px rgba(23, 33, 26, 0.08);
}

.site-header__demo--active {
  color: var(--color-municipal-green);
  background: rgba(47, 93, 80, 0.12);
  border-color: rgba(47, 93, 80, 0.35);
  box-shadow: 0 0 0 3px rgba(47, 93, 80, 0.1);
}

@media (max-width: 760px) {
  .site-header__inner {
    flex-wrap: wrap;
    gap: var(--space-2);
  }

  .site-header__nav {
    order: 3;
    justify-content: flex-start;
    width: 100%;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .site-header__nav::-webkit-scrollbar {
    display: none;
  }

  .site-header__link {
    white-space: nowrap;
  }
}
</style>
