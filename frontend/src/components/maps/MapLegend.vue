<template>
  <div class="map-legend" aria-label="Map marker legend">
    <div>
      <strong>Categories</strong>
      <span v-for="category in categories" :key="category.value" class="map-legend__item">
        <span class="map-legend__swatch" :class="`map-legend__swatch--${category.value}`" />
        {{ category.label }}
      </span>
    </div>
    <div>
      <strong>Status rings</strong>
      <span v-for="status in statuses" :key="status.value" class="map-legend__item">
        <span class="map-legend__ring" :class="`map-legend__ring--${status.value}`" />
        {{ status.label }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { IssueCategory, TicketStatus } from '@/types/report';
import { categoryLabels, statusLabels } from '@/utils/reportFormatting';

const categories = (Object.keys(categoryLabels) as IssueCategory[]).map((value) => ({
  value,
  label: categoryLabels[value],
}));

const statuses = (Object.keys(statusLabels) as TicketStatus[]).map((value) => ({
  value,
  label: statusLabels[value],
}));
</script>

<style scoped>
.map-legend {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-4);
  border: var(--border-soft);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  background: rgba(255, 253, 247, 0.72);
}

.map-legend > div {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.map-legend strong {
  width: 100%;
  color: var(--text-primary);
  font-size: var(--text-xs);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.map-legend__item {
  display: inline-flex;
  gap: var(--space-2);
  align-items: center;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 750;
}

.map-legend__swatch,
.map-legend__ring {
  width: 0.72rem;
  height: 0.72rem;
  border-radius: var(--radius-pill);
}

.map-legend__swatch--pothole {
  background: var(--category-pothole-text);
}

.map-legend__swatch--garbage {
  background: var(--category-garbage-text);
}

.map-legend__swatch--broken_streetlight {
  background: var(--category-broken-streetlight-text);
}

.map-legend__swatch--blocked_sidewalk {
  background: var(--category-blocked-sidewalk-text);
}

.map-legend__swatch--damaged_sign {
  background: var(--category-damaged-sign-text);
}

.map-legend__swatch--other {
  background: var(--category-other-text);
}

.map-legend__ring {
  border: 3px solid var(--status-new-text);
}

.map-legend__ring--verified {
  border-color: var(--status-verified-text);
}

.map-legend__ring--assigned,
.map-legend__ring--resolved {
  border-color: var(--status-assigned-text);
}

.map-legend__ring--in_progress {
  border-color: var(--status-in-progress-text);
}

.map-legend__ring--rejected {
  border-color: var(--status-rejected-text);
}

@media (max-width: 720px) {
  .map-legend {
    grid-template-columns: 1fr;
  }
}
</style>
