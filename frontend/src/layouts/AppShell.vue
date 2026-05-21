<template>
  <main class="app-shell">
    <nav class="top-nav" aria-label="Main navigation">
      <RouterLink to="/">KoStreet</RouterLink>
      <RouterLink to="/report">Report</RouterLink>
      <RouterLink to="/dashboard">Dashboard</RouterLink>
      <RouterLink to="/audit">Street Audit</RouterLink>
    </nav>
    <section class="page-panel">
      <slot />
    </section>
  </main>
</template>

