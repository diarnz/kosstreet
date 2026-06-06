import { defineStore } from 'pinia';
import { listNotifications } from '@/api/notifications';
import type { AppNotification, NotificationScope } from '@/types/notification';

const dismissedStorageKey = 'kostreet-dismissed-notifications';

interface NotificationsState {
  items: AppNotification[];
  dismissedIds: string[];
  isLoading: boolean;
  error: string | null;
  lastFetchedAt: string | null;
}

function readDismissedIds(): string[] {
  try {
    const raw = window.localStorage.getItem(dismissedStorageKey);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    return Array.isArray(parsed) ? parsed.filter((id) => typeof id === 'string') : [];
  } catch {
    return [];
  }
}

function writeDismissedIds(ids: string[]) {
  window.localStorage.setItem(dismissedStorageKey, JSON.stringify(ids));
}

export const useNotificationsStore = defineStore('notifications', {
  state: (): NotificationsState => ({
    items: [],
    dismissedIds: readDismissedIds(),
    isLoading: false,
    error: null,
    lastFetchedAt: null,
  }),
  getters: {
    visibleItems(state): AppNotification[] {
      const dismissed = new Set(state.dismissedIds);
      return state.items.filter((item) => !dismissed.has(item.id));
    },
    unreadCount(): number {
      return this.visibleItems.length;
    },
  },
  actions: {
    hydrateDismissed() {
      this.dismissedIds = readDismissedIds();
    },
    async fetch(scope: NotificationScope) {
      this.isLoading = true;
      this.error = null;

      try {
        this.items = await listNotifications(scope);
        this.lastFetchedAt = new Date().toISOString();
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to load notifications';
        this.items = [];
      } finally {
        this.isLoading = false;
      }
    },
    dismiss(id: string) {
      if (this.dismissedIds.includes(id)) return;
      this.dismissedIds = [...this.dismissedIds, id];
      writeDismissedIds(this.dismissedIds);
    },
    dismissAll(scope?: NotificationScope) {
      const ids = this.visibleItems
        .filter((item) => !scope || item.scope === scope || scope === 'all')
        .map((item) => item.id);
      const merged = new Set([...this.dismissedIds, ...ids]);
      this.dismissedIds = [...merged];
      writeDismissedIds(this.dismissedIds);
    },
    remove(id: string) {
      this.dismiss(id);
      this.items = this.items.filter((item) => item.id !== id);
    },
  },
});
