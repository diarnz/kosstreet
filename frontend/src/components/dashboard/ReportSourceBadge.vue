<template>
  <AppBadge :tone="source === 'citizen' ? 'source-citizen' : 'source-ai-audit'" :size="compact ? 'xs' : 'sm'">
    {{ compact ? shortLabels[source] : sourceLabels[source] }}
  </AppBadge>
</template>

<script setup lang="ts">
import AppBadge from '@/components/common/AppBadge.vue';
import type { ReportSource } from '@/types/report';
import { sourceLabels } from '@/utils/reportFormatting';

defineProps<{
  source: ReportSource;
  compact?: boolean;
}>();

const shortLabels: Record<ReportSource, string> = {
  citizen: 'Citizen',
  street_audit: 'AI',
};
</script>

