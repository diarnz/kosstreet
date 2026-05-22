<template>
  <AppShell content-width="wide">
    <div class="dashboard-layout">
      <slot />
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from './AppShell.vue';
</script>

<style scoped>
.dashboard-layout {
  display: grid;
  gap: var(--space-5);
}
</style>
