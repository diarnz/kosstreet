import { ref } from 'vue';

export function useAsyncState<TArgs extends unknown[], TResult>(
  callback: (...args: TArgs) => Promise<TResult>,
) {
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  async function run(...args: TArgs): Promise<TResult> {
    isLoading.value = true;
    error.value = null;

    try {
      return await callback(...args);
    } catch (unknownError) {
      const normalizedError =
        unknownError instanceof Error ? unknownError : new Error('Unexpected async error');
      error.value = normalizedError;
      throw normalizedError;
    } finally {
      isLoading.value = false;
    }
  }

  function reset() {
    isLoading.value = false;
    error.value = null;
  }

  return {
    isLoading,
    error,
    run,
    reset,
  };
}

