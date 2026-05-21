<template>
  <AppShell>
    <section class="hero">
      <p class="eyebrow">Smart Municipality AI</p>
      <h1>KoStreet turns street-level issues into municipal action.</h1>
      <p>
        Citizen reports, AI categorization, geolocation, and proactive street audits for Prishtina.
      </p>
      <div class="actions">
        <RouterLink class="button primary" to="/report">Create Report</RouterLink>
        <RouterLink class="button secondary" to="/dashboard">Open Dashboard</RouterLink>
      </div>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue';
</script>

