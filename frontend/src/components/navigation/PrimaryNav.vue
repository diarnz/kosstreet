<template>
  <nav class="primary-nav" aria-label="Primary navigation">
    <RouterLink class="primary-nav__brand" to="/">
      <span class="primary-nav__mark" aria-hidden="true" />
      <span>
        KoStreet
        <small>Prishtina civic intelligence</small>
      </span>
    </RouterLink>
    <div class="primary-nav__links">
      <RouterLink v-for="item in items" :key="item.to" class="primary-nav__link" :to="item.to">
        {{ item.label }}
      </RouterLink>
      <button
        class="primary-nav__demo-toggle"
        :class="{ 'primary-nav__demo-toggle--active': uiStore.demoMode }"
        :aria-pressed="uiStore.demoMode"
        :aria-label="uiStore.demoMode ? 'Disable Pitch Mode' : 'Enable Pitch Mode'"
        type="button"
        @click="uiStore.toggleDemoMode"
      >
        {{ uiStore.demoMode ? 'Pitch Mode On' : 'Pitch Mode' }}
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui';

const uiStore = useUiStore();

const items = [
  { to: '/report', label: 'Report' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/audit', label: 'Street Audit' },
];
</script>

<style scoped>
.primary-nav {
  position: relative;
  z-index: var(--z-nav);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: center;
  justify-content: space-between;
  max-width: 1180px;
  margin: 0 auto;
  padding: 0.35rem;
  border: 1px solid rgba(23, 33, 26, 0.08);
  border-radius: calc(var(--radius-pill) + 0.35rem);
  background: rgba(255, 253, 247, 0.52);
  backdrop-filter: blur(12px);
}

.primary-nav__brand,
.primary-nav__link,
.primary-nav__demo-toggle {
  display: inline-flex;
  align-items: center;
  min-height: 2.5rem;
  border-radius: var(--radius-pill);
  font-weight: 850;
}

.primary-nav__brand {
  gap: var(--space-2);
  padding: 0 var(--space-3) 0 var(--space-1);
  font-size: var(--text-lg);
}

.primary-nav__brand small {
  display: block;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 750;
  letter-spacing: 0.02em;
}

.primary-nav__mark {
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 0.65rem;
  background: linear-gradient(135deg, var(--color-municipal-green), var(--color-ink));
  box-shadow: 0 10px 24px rgba(47, 93, 80, 0.22);
}

.primary-nav__links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.primary-nav__link,
.primary-nav__demo-toggle {
  padding: 0 var(--space-4);
  color: var(--text-secondary);
  transition:
    background 160ms ease,
    color 160ms ease,
    box-shadow 160ms ease;
}

.primary-nav__demo-toggle {
  border: 0;
  border-radius: var(--radius-pill);
  background: rgba(255, 253, 247, 0.42);
  font-weight: 850;
}

.primary-nav__link:hover,
.primary-nav__demo-toggle:hover {
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.5);
}

.primary-nav__link.router-link-active {
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.86);
  box-shadow: inset 0 0 0 1px rgba(23, 33, 26, 0.12);
}

.primary-nav__demo-toggle--active {
  color: var(--text-primary);
  background: rgba(255, 247, 225, 0.94);
  box-shadow: inset 0 0 0 1px rgba(217, 144, 47, 0.38);
}

@media (max-width: 620px) {
  .primary-nav {
    align-items: flex-start;
    border-radius: var(--radius-lg);
  }

  .primary-nav__links {
    width: 100%;
  }

  .primary-nav__link,
  .primary-nav__demo-toggle {
    flex: 1 1 auto;
    justify-content: center;
  }
}
</style>
