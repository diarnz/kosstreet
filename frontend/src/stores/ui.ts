import { defineStore } from 'pinia';

const demoModeStorageKey = 'kostreet-demo-mode';

interface UiState {
  sidebarOpen: boolean;
  demoMode: boolean;
}

export const useUiStore = defineStore('ui', {
  state: (): UiState => ({
    sidebarOpen: false,
    demoMode: false,
  }),
  actions: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },
    setDemoMode(enabled: boolean) {
      this.demoMode = enabled;
      window.localStorage.setItem(demoModeStorageKey, enabled ? '1' : '0');
    },
    toggleDemoMode() {
      this.setDemoMode(!this.demoMode);
    },
    hydrateDemoMode() {
      this.demoMode = window.localStorage.getItem(demoModeStorageKey) === '1';
    },
  },
});

