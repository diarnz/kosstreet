<template>
  <AppBadge :tone="tone" size="sm">{{ label }}</AppBadge>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import type { TicketStatus } from '@/types/report';
import type { BadgeTone } from '@/types/ui';

const props = defineProps<{
  status: TicketStatus;
}>();

const labels: Record<TicketStatus, string> = {
  new: 'New',
  verified: 'Verified',
  assigned: 'Assigned',
  in_progress: 'In Progress',
  resolved: 'Resolved',
  rejected: 'Rejected',
};

const tones: Record<TicketStatus, BadgeTone> = {
  new: 'status-new',
  verified: 'status-verified',
  assigned: 'status-assigned',
  in_progress: 'status-in-progress',
  resolved: 'status-resolved',
  rejected: 'status-rejected',
};

const label = computed(() => labels[props.status]);
const tone = computed(() => tones[props.status]);
</script>

