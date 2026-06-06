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
  overflow: visible;
  min-width: 0;
}

@media (max-width: 640px) {
  .dashboard-layout {
    gap: var(--space-3);
  }
}
</style>
