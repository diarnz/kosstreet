<template>
  <AppBadge :tone="tone" size="sm">{{ label }}</AppBadge>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import type { IssueCategory } from '@/types/report';
import type { BadgeTone } from '@/types/ui';

const props = defineProps<{
  category: IssueCategory;
}>();

const labels: Record<IssueCategory, string> = {
  pothole: 'Pothole',
  garbage: 'Garbage',
  broken_streetlight: 'Broken Light',
  blocked_sidewalk: 'Blocked Sidewalk',
  damaged_sign: 'Damaged Sign',
  other: 'Other',
};

const tones: Record<IssueCategory, BadgeTone> = {
  pothole: 'category-pothole',
  garbage: 'category-garbage',
  broken_streetlight: 'category-broken-streetlight',
  blocked_sidewalk: 'category-blocked-sidewalk',
  damaged_sign: 'category-damaged-sign',
  other: 'category-other',
};

const label = computed(() => labels[props.category]);
const tone = computed(() => tones[props.category]);
</script>
