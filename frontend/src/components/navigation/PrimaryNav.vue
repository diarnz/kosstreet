<template>
  <nav class="dock" aria-label="Primary navigation">
    <div class="dock__pill">

      <!-- Home -->
      <RouterLink class="dock__item" to="/" aria-label="Home" exact-active-class="dock__item--active">
        <span class="dock__icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z"/>
            <polyline points="9 21 9 12 15 12 15 21"/>
          </svg>
        </span>
        <span class="dock__label">Home</span>
      </RouterLink>

      <div class="dock__sep" aria-hidden="true" />

      <!-- Report -->
      <RouterLink class="dock__item" to="/report" aria-label="Report an issue" active-class="dock__item--active">
        <span class="dock__icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="12" y1="11" x2="12" y2="17"/>
            <line x1="9" y1="14" x2="15" y2="14"/>
          </svg>
        </span>
        <span class="dock__label">Report</span>
      </RouterLink>

      <!-- Dashboard -->
      <RouterLink class="dock__item" to="/dashboard" aria-label="Command dashboard" active-class="dock__item--active">
        <span class="dock__icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
        </span>
        <span class="dock__label">Dashboard</span>
      </RouterLink>

      <!-- Street Audit -->
      <RouterLink class="dock__item" to="/audit" aria-label="Street audit" active-class="dock__item--active">
        <span class="dock__icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <line x1="11" y1="8" x2="11" y2="14"/>
            <line x1="8" y1="11" x2="14" y2="11"/>
          </svg>
        </span>
        <span class="dock__label">Audit</span>
      </RouterLink>

      <div class="dock__sep" aria-hidden="true" />

      <!-- Dark mode toggle -->
      <button
        class="dock__item dock__item--btn"
        :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        @click="toggleDark"
      >
        <span class="dock__icon">
          <!-- Sun -->
          <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="4"/>
            <line x1="12" y1="2" x2="12" y2="4"/>
            <line x1="12" y1="20" x2="12" y2="22"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="2" y1="12" x2="4" y2="12"/>
            <line x1="20" y1="12" x2="22" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <!-- Moon -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </span>
      </button>

    </div>
  </nav>
</template>

<script setup lang="ts">
import { useDarkMode } from '@/composables/useDarkMode';

const { isDark, toggleDark } = useDarkMode();
</script>

<style scoped>
/* ── Floating dock wrapper ── */
.dock {
  position: fixed;
  bottom: 1.75rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-nav, 200);
  pointer-events: none;
}

/* ── The pill itself ── */
.dock__pill {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.85rem;
  border-radius: 9999px;
  background: rgba(255, 253, 247, 0.72);
  backdrop-filter: blur(24px) saturate(1.6);
  -webkit-backdrop-filter: blur(24px) saturate(1.6);
  border: 1px solid rgba(23, 33, 26, 0.1);
  box-shadow:
    0 8px 32px rgba(23, 33, 26, 0.12),
    0 2px 8px rgba(23, 33, 26, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.65);
  pointer-events: auto;
}

/* ── Each nav item ── */
.dock__item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 9999px;
  border: none;
  background: transparent;
  color: rgba(30, 40, 35, 0.55);
  text-decoration: none;
  cursor: pointer;
  transition:
    color 180ms ease,
    background 180ms ease,
    transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 180ms ease;
}

.dock__item:hover {
  color: rgba(30, 40, 35, 0.9);
  background: rgba(47, 93, 80, 0.09);
  transform: translateY(-3px) scale(1.08);
}

/* Active / current route */
.dock__item--active {
  color: #2f5d50 !important;
  background: rgba(47, 93, 80, 0.13) !important;
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.18);
}

.dock__item--active .dock__icon {
  filter: drop-shadow(0 0 6px rgba(47, 93, 80, 0.45));
}

/* Button variant (dark-mode toggle) */
.dock__item--btn {
  appearance: none;
  font: inherit;
}

/* Icon wrapper */
.dock__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: filter 180ms ease;
}

/* Tooltip label (appears on hover) */
.dock__label {
  position: absolute;
  bottom: calc(100% + 0.55rem);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  background: rgba(23, 33, 26, 0.82);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 140ms ease, transform 140ms ease;
}

/* Arrow tip */
.dock__label::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: rgba(23, 33, 26, 0.82);
}

.dock__item:hover .dock__label {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* Separator */
.dock__sep {
  width: 1px;
  height: 1.5rem;
  margin-inline: 0.25rem;
  background: rgba(23, 33, 26, 0.1);
  border-radius: 1px;
  flex-shrink: 0;
}

/* Entrance animation */
.dock {
  animation: dock-rise 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes dock-rise {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(2rem);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .dock {
    animation: none;
  }
  .dock__item:hover {
    transform: none;
  }
}
</style>
