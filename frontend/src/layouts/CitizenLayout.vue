<template>
  <AppShell content-width="narrow">
    <div class="citizen-layout">
      <slot />
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from './AppShell.vue';
</script>

<style scoped>
.citizen-layout {
  display: grid;
  gap: var(--space-5);
}
</style>
