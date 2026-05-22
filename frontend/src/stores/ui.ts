import { defineStore } from 'pinia';

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
    },
  },
});

