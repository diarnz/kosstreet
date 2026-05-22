<template>
  <AppShell>
    <div class="home-page stack-xl">
      <AppSectionHeader
        eyebrow="Smart Municipality AI"
        title="KoStreet turns street-level issues into municipal action."
        description="A Prishtina-focused civic operations platform for structured reports, municipal triage, and AI-assisted street audit review."
        size="hero"
      />

      <div class="home-page__actions cluster">
        <RouterLink class="home-page__link home-page__link--primary" to="/dashboard">
          Open municipal dashboard
        </RouterLink>
        <RouterLink class="home-page__link" to="/report">Start citizen report</RouterLink>
      </div>

      <section class="grid-auto" aria-label="KoStreet product surfaces">
        <RouterLink to="/report">
          <FeaturePanel
            eyebrow="Citizen"
            title="Citizen reporting"
            description="The mobile-first entry point for photo capture, location tagging, AI assistance, and transparent report tracking."
            tone="citizen"
          />
        </RouterLink>

        <RouterLink to="/dashboard">
          <FeaturePanel
            eyebrow="Municipality"
            title="Command dashboard"
            description="The operating surface for Prishtina teams to triage, route, verify, and follow civic issues through resolution."
            tone="dashboard"
          />
        </RouterLink>

        <RouterLink to="/audit">
          <FeaturePanel
            eyebrow="AI Street Audit"
            title="Audit workspace"
            description="The review area for AI-suggested street defects, designed around confidence, transparency, and human verification."
            tone="audit"
          />
        </RouterLink>
      </section>

      <AppCard variant="command" class="operating-loop stack">
        <div class="cluster-between">
          <div>
            <p class="eyebrow">Municipal Operating Loop</p>
            <h2>Detect, verify, route, resolve, and measure.</h2>
          </div>
          <AppBadge tone="info">Prishtina-first workflow</AppBadge>
        </div>
        <div class="loop-steps">
          <span v-for="step in loopSteps" :key="step">{{ step }}</span>
        </div>
      </AppCard>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import AppCard from '@/components/common/AppCard.vue';
import FeaturePanel from '@/components/common/FeaturePanel.vue';
import AppSectionHeader from '@/components/common/AppSectionHeader.vue';
import AppShell from '@/layouts/AppShell.vue';

const loopSteps = ['Detect', 'Verify', 'Route', 'Resolve', 'Measure'];
</script>

<style scoped>
.home-page__link {
  display: inline-flex;
  align-items: center;
  min-height: 3rem;
  padding: 0 var(--space-5);
  border: var(--border-strong);
  border-radius: var(--radius-pill);
  font-weight: 850;
}

.home-page__link--primary {
  color: var(--text-inverse);
  background: var(--action-primary);
  border-color: transparent;
  box-shadow: 0 14px 30px rgba(47, 93, 80, 0.2);
}

.operating-loop h2 {
  margin: 0;
  font-size: clamp(1.7rem, 4vw, 2.5rem);
  letter-spacing: -0.05em;
}

.loop-steps {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-2);
}

.loop-steps span {
  padding: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  background: rgba(255, 253, 247, 0.54);
  font-weight: 850;
  text-align: center;
}

@media (max-width: 760px) {
  .loop-steps {
    grid-template-columns: 1fr;
  }
}
</style>
