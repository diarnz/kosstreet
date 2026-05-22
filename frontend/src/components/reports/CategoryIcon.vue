<template>
  <svg :class="['category-icon', `category-icon--${category}`]" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <template v-if="category === 'pothole'">
      <path d="M4 16c2-4 4-4 6-2s4 2 6-2 4-2 4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      <circle cx="8" cy="17" r="1.5" fill="currentColor" />
      <circle cx="16" cy="15" r="1.5" fill="currentColor" />
    </template>
    <template v-else-if="category === 'garbage'">
      <path d="M9 6h6M10 6V4h4v2M8 9h8l-1 11H9L8 9z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
    </template>
    <template v-else-if="category === 'broken_streetlight'">
      <path d="M12 3v3M9 21h6M10 6h4v8a2 2 0 01-4 0V6z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M8 12h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>
    <template v-else-if="category === 'blocked_sidewalk'">
      <path d="M4 18h16M6 18V8l4-3 4 3v10M14 18V11l4 3v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>
    <template v-else-if="category === 'damaged_sign'">
      <path d="M12 4l7 4-7 4-7-4 7-4z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
      <path d="M12 12v8M9 20h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>
    <template v-else>
      <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.8" />
      <path d="M12 8v5M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </template>
  </svg>
</template>

<script setup lang="ts">
import type { IssueCategory } from '@/types/report';

defineProps<{
  category: IssueCategory;
}>();
</script>

<style scoped>
.category-icon {
  width: 1.65rem;
  height: 1.65rem;
}
</style>
