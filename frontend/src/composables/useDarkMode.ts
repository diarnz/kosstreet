import { ref, watch } from 'vue';

const STORAGE_KEY = 'kostreet-dark';

// Singleton state — shared across every component that calls useDarkMode()
const isDark = ref<boolean>(
  localStorage.getItem(STORAGE_KEY) === 'true' ||
  (!localStorage.getItem(STORAGE_KEY) &&
    window.matchMedia('(prefers-color-scheme: dark)').matches),
);

// Apply the class immediately on load (before Vue mounts)
if (isDark.value) document.documentElement.classList.add('dark');

watch(isDark, (val) => {
  document.documentElement.classList.toggle('dark', val);
  localStorage.setItem(STORAGE_KEY, String(val));
});

export function useDarkMode() {
  function toggleDark() {
    isDark.value = !isDark.value;
  }
  return { isDark, toggleDark };
}
