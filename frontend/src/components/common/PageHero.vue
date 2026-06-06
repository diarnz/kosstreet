<template>
  <header class="page-hero animate-fade-up" :class="[`page-hero--${align}`]">
    <div class="page-hero__content">
      <AppLogo v-if="showLogo" class="page-hero__logo" size="sm" />
      <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
      <h1 class="page-hero__title" :class="{ 'gradient-text': gradient }">{{ title }}</h1>
      <p v-if="description" class="page-hero__description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="page-hero__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup lang="ts">
import AppLogo from '@/components/common/AppLogo.vue';

withDefaults(
  defineProps<{
    title: string;
    description?: string;
    eyebrow?: string;
    align?: 'start' | 'center';
    showLogo?: boolean;
    gradient?: boolean;
  }>(),
  {
    align: 'start',
    showLogo: false,
    gradient: false,
  },
);
</script>

<style scoped>
.page-hero {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: flex-end;
  justify-content: space-between;
  padding-bottom: var(--space-5);
  border-bottom: 1px solid rgba(23, 33, 26, 0.08);
}

.page-hero--center {
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.page-hero__content {
  display: grid;
  gap: var(--space-2);
  min-width: 0;
}

.page-hero--center .page-hero__content {
  justify-items: center;
}

.page-hero__logo {
  margin-bottom: var(--space-1);
}

.page-hero__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.65rem, 3.5vw, 2.35rem);
  line-height: 1.08;
  letter-spacing: -0.04em;
  text-wrap: balance;
}

.page-hero__description {
  max-width: 38rem;
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.page-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
}

.page-hero--center .page-hero__actions {
  justify-content: center;
}

@media (max-width: 640px) {
  .page-hero {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    padding-bottom: var(--space-4);
  }

  .page-hero__title {
    font-size: clamp(1.4rem, 7vw, 1.85rem);
  }

  .page-hero__description {
    font-size: var(--text-xs);
  }

  .page-hero__actions {
    width: 100%;
    justify-content: flex-start;
  }

  .page-hero--center .page-hero__actions {
    justify-content: center;
  }
}
</style>
