<template>
  <AppBadge :tone="tone" size="sm">{{ auditRunStatusLabels[status] }}</AppBadge>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from '@/components/common/AppBadge.vue';
import type { AuditRunStatus } from '@/types/audit';
import type { BadgeTone } from '@/types/ui';
import { auditRunStatusLabels } from '@/utils/auditFormatting';

const props = defineProps<{
  status: AuditRunStatus;
}>();

const tone = computed<BadgeTone>(() => {
  if (props.status === 'running') return 'warning';
  if (props.status === 'completed') return 'success';
  if (props.status === 'failed') return 'danger';
  return 'ai';
});
</script>
