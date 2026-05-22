<template>
  <span
    v-if="animated"
    :class="['app-logo-wrap', `app-logo-wrap--${size}`]"
    role="img"
    aria-label="KoStreet Civic Community"
  >
    <img :src="logoUrl" alt="" aria-hidden="true" class="app-logo__sizer" />
    <span
      class="app-logo__gradient gradient-sweep-fill"
      aria-hidden="true"
      :style="maskStyle"
    />
  </span>
  <img
    v-else
    :class="['app-logo', `app-logo--${size}`]"
    :src="logoUrl"
    alt="KoStreet Civic Community"
  />
</template>

<script setup lang="ts">
import logoUrl from '@/assets/kostreet-logo.png';

withDefaults(
  defineProps<{
    size?: 'sm' | 'md' | 'lg' | 'hero';
    animated?: boolean;
  }>(),
  {
    size: 'md',
    animated: false,
  },
);

const maskStyle = {
  WebkitMaskImage: `url(${logoUrl})`,
  maskImage: `url(${logoUrl})`,
};
</script>

<style scoped>
.app-logo {
  display: block;
  width: auto;
  object-fit: contain;
}

.app-logo-wrap {
  position: relative;
  display: inline-block;
  line-height: 0;
}

.app-logo__sizer {
  display: block;
  width: auto;
  object-fit: contain;
  visibility: hidden;
}

.app-logo__gradient {
  position: absolute;
  inset: 0;
  -webkit-mask-size: 100% 100%;
  mask-size: 100% 100%;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-position: center;
}

.app-logo--sm,
.app-logo-wrap--sm .app-logo__sizer {
  height: 2.75rem;
}

.app-logo--md,
.app-logo-wrap--md .app-logo__sizer {
  height: 3.5rem;
}

.app-logo--lg,
.app-logo-wrap--lg .app-logo__sizer {
  height: 5rem;
}

.app-logo--hero,
.app-logo-wrap--hero .app-logo__sizer {
  height: clamp(5rem, 18vw, 8.5rem);
}
</style>
