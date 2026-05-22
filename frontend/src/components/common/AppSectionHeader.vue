<template>
  <header class="section-header" :class="[`section-header--${size}`, `section-header--${align}`]">
    <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
    <h1 class="page-title" :class="{ 'page-title--hero': size === 'hero' }">{{ title }}</h1>
    <p v-if="description" class="page-description">{{ description }}</p>
  </header>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    eyebrow?: string;
    title: string;
    description?: string;
    size?: 'default' | 'hero';
    align?: 'start' | 'center';
  }>(),
  {
    size: 'default',
    align: 'start',
  },
);
</script>

<style scoped>
.section-header {
  display: grid;
  gap: var(--space-4);
}

.section-header--center {
  justify-items: center;
  text-align: center;
}

.section-header--center .page-description {
  margin-inline: auto;
}

.section-header--hero {
  gap: var(--space-5);
}
</style>
