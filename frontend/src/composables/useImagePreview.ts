import { onBeforeUnmount, ref, watch, type Ref } from 'vue';

export function useImagePreview(file: Ref<File | null>) {
  const previewUrl = ref<string | null>(null);

  function revokePreview() {
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value);
      previewUrl.value = null;
    }
  }

  watch(
    file,
    (nextFile) => {
      revokePreview();

      if (nextFile) {
        previewUrl.value = URL.createObjectURL(nextFile);
      }
    },
    { immediate: true },
  );

  onBeforeUnmount(revokePreview);

  return {
    previewUrl,
    revokePreview,
  };
}

