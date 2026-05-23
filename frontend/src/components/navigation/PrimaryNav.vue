<template>
  <header class="site-header">
    <div class="site-header__glow" aria-hidden="true" />
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

    </div>
    <div class="site-header__border" aria-hidden="true" />
  </header>
</template>

<script setup lang="ts">
import AppLogo from '@/components/common/AppLogo.vue';

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
  background: rgba(232, 226, 214, 0.78);
  backdrop-filter: blur(28px) saturate(1.8);
  -webkit-backdrop-filter: blur(28px) saturate(1.8);
}

/* Subtle top glow */
.site-header__glow {
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(47, 93, 80, 0.55) 30%,
    rgba(217, 144, 47, 0.35) 55%,
    rgba(47, 93, 80, 0.55) 70%,
    transparent
  );
  animation: gradient-shift 8s ease infinite;
  background-size: 200% 100%;
}

/* Animated gradient border bottom */
.site-header__border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(47, 93, 80, 0.18) 20%,
    rgba(217, 144, 47, 0.12) 50%,
    rgba(63, 110, 140, 0.18) 80%,
    transparent 100%
  );
}

.site-header__inner {
  position: relative;
  display: flex;
  gap: var(--space-4);
  align-items: center;
  justify-content: space-between;
  max-width: 1440px;
  margin-inline: auto;
  padding: 0.6rem clamp(1rem, 4vw, 2.5rem);
}

.site-header__brand {
  flex-shrink: 0;
  transition: transform var(--motion-fast) var(--ease-out-expo), opacity var(--motion-fast) ease;
}

.site-header__brand:hover {
  transform: scale(1.04);
  opacity: 0.85;
}

.site-header__nav {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  gap: 0.15rem;
  justify-content: center;
}

.site-header__link {
  position: relative;
  display: inline-flex;
  align-items: center;
  min-height: 2.25rem;
  padding: 0 0.95rem;
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 850;
  letter-spacing: 0.005em;
  transition:
    color var(--motion-fast) ease,
    background var(--motion-fast) ease,
    box-shadow var(--motion-fast) ease;
}

.site-header__link:hover {
  color: var(--text-primary);
  background: rgba(47, 93, 80, 0.09);
}

/* Active = filled green pill */
.site-header__link.router-link-active {
  color: #fff;
  background: var(--color-municipal-green);
  box-shadow:
    0 0 0 3px rgba(47, 93, 80, 0.18),
    0 4px 18px rgba(47, 93, 80, 0.38),
    inset 0 1px 0 rgba(255, 255, 255, 0.14);
}

.site-header__link.router-link-active:hover {
  background: #244c42;
  box-shadow:
    0 0 0 3px rgba(47, 93, 80, 0.22),
    0 6px 22px rgba(47, 93, 80, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.14);
}

/* Demo toggle */
.site-header__demo {
  display: inline-flex;
  gap: 0.4rem;
  flex-shrink: 0;
  align-items: center;
  min-height: 2.25rem;
  padding: 0 0.9rem;
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  background: rgba(255, 253, 247, 0.45);
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
  background: rgba(255, 253, 247, 0.72);
  box-shadow: 0 4px 16px rgba(23, 33, 26, 0.08);
}

.site-header__demo--active {
  color: var(--color-municipal-green);
  background: rgba(47, 93, 80, 0.1);
  border-color: rgba(47, 93, 80, 0.3);
  box-shadow: 0 0 0 3px rgba(47, 93, 80, 0.1);
}

.site-header__demo-dot {
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(58, 63, 59, 0.3);
  transition: background var(--motion-fast) ease, box-shadow var(--motion-fast) ease;
}

.site-header__demo--active .site-header__demo-dot {
  background: var(--color-municipal-green);
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.25);
  animation: glow-pulse 2.4s ease-in-out infinite;
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
