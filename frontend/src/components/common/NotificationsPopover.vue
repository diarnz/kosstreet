<template>
  <div ref="rootRef" class="notifications-popover">
    <button
      class="notifications-popover__trigger"
      type="button"
      :aria-label="unreadCount ? `${unreadCount} notifications` : 'Notifications'"
      :aria-expanded="open"
      @click="toggleOpen"
    >
      <svg class="notifications-popover__bell" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3a5 5 0 0 0-5 5v2.2c0 .8-.3 1.6-.8 2.2L4.5 14.5A1.5 1.5 0 0 0 6 17h12a1.5 1.5 0 0 0 1.5-2.5l-1.7-2.1c-.5-.6-.8-1.4-.8-2.2V8a5 5 0 0 0-5-5Z"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linejoin="round"
        />
        <path d="M10 18.5a2 2 0 0 0 4 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      </svg>
      <span v-if="unreadCount > 0" class="notifications-popover__badge">{{ unreadCount }}</span>
    </button>

    <Teleport to="body">
      <Transition name="notifications-panel">
        <div
          v-if="open"
          ref="panelRef"
          class="notifications-popover__panel"
          :style="panelStyle"
          role="dialog"
          aria-label="Notifications"
        >
        <div class="notifications-popover__panel-head">
          <span class="notifications-popover__panel-title">Notifications</span>
          <button
            v-if="visibleItems.length"
            class="notifications-popover__clear"
            type="button"
            @click="archiveAll"
          >
            Clear all
          </button>
        </div>

        <div v-if="isLoading" class="notifications-popover__empty">Loading…</div>
        <div v-else-if="error" class="notifications-popover__empty notifications-popover__empty--warn">
          {{ error }}
        </div>
        <div v-else-if="visibleItems.length === 0" class="notifications-popover__empty">
          No notifications
        </div>
        <ul v-else class="notifications-popover__list">
          <li
            v-for="item in visibleItems"
            :key="item.id"
            class="notifications-popover__item"
            :class="{ 'notifications-popover__item--active': activeId === item.id }"
          >
            <button
              class="notifications-popover__body"
              type="button"
              @click="handleOpen(item)"
            >
              <div class="notifications-popover__meta">
                <span class="notifications-popover__title">{{ item.title }}</span>
                <span class="notifications-popover__time">{{ formatRelativeTime(item.created_at) }}</span>
              </div>
              <p class="notifications-popover__description">{{ item.description }}</p>
            </button>

            <div class="notifications-popover__actions">
              <template v-if="activeId === item.id">
                <button
                  class="notifications-popover__action"
                  type="button"
                  aria-label="Archive notification"
                  @click="archive(item.id)"
                >
                  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M4 7h16M6 7V5h12v2M8 11v6M12 11v6M16 11v6M7 7l1 12h8l1-12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                  </svg>
                </button>
                <button
                  class="notifications-popover__action notifications-popover__action--danger"
                  type="button"
                  aria-label="Delete notification"
                  @click="remove(item.id)"
                >
                  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                  </svg>
                </button>
                <button
                  class="notifications-popover__action"
                  type="button"
                  aria-label="Close actions"
                  @click="activeId = null"
                >
                  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M10 8l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </button>
              </template>
              <button
                v-else
                class="notifications-popover__action"
                type="button"
                aria-label="Notification actions"
                @click.stop="activeId = item.id"
              >
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle cx="12" cy="6" r="1.2" fill="currentColor" />
                  <circle cx="12" cy="12" r="1.2" fill="currentColor" />
                  <circle cx="12" cy="18" r="1.2" fill="currentColor" />
                </svg>
              </button>
            </div>
          </li>
        </ul>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useNotificationsStore } from '@/stores/notifications';
import { useAuditRunsStore } from '@/stores/auditRuns';
import { useReportsStore } from '@/stores/reports';
import type { AppNotification, NotificationScope } from '@/types/notification';
import { formatRelativeTime } from '@/utils/reportFormatting';

const props = defineProps<{
  scope: NotificationScope;
}>();

const router = useRouter();
const notificationsStore = useNotificationsStore();
const reportsStore = useReportsStore();
const auditRunsStore = useAuditRunsStore();

const PANEL_WIDTH = 320;
const PANEL_GAP = 8;

const rootRef = ref<HTMLElement | null>(null);
const panelRef = ref<HTMLElement | null>(null);
const open = ref(false);
const activeId = ref<string | null>(null);
const panelStyle = ref<{ top: string; left: string; width: string } | null>(null);

const visibleItems = computed(() => notificationsStore.visibleItems);
const unreadCount = computed(() => notificationsStore.unreadCount);
const isLoading = computed(() => notificationsStore.isLoading);
const error = computed(() => notificationsStore.error);

function toggleOpen() {
  open.value = !open.value;
  if (open.value) {
    void notificationsStore.fetch(props.scope);
  }
}

function archive(id: string) {
  notificationsStore.dismiss(id);
  activeId.value = null;
}

function remove(id: string) {
  notificationsStore.remove(id);
  activeId.value = null;
}

function archiveAll() {
  notificationsStore.dismissAll(props.scope);
  activeId.value = null;
}

async function handleOpen(item: AppNotification) {
  if (item.scope === 'dashboard' && item.target_id) {
    reportsStore.selectReport(item.target_id);
    await router.push('/dashboard');
    open.value = false;
    return;
  }

  if (item.scope === 'audit' && item.target_id) {
    if (item.kind.startsWith('audit_run')) {
      auditRunsStore.selectRun(item.target_id);
    }
    await router.push('/audit');
    open.value = false;
  }
}

function updatePanelPosition() {
  const trigger = rootRef.value?.querySelector('.notifications-popover__trigger');
  if (!trigger) {
    panelStyle.value = null;
    return;
  }

  const rect = trigger.getBoundingClientRect();
  const width = Math.min(PANEL_WIDTH, window.innerWidth - 16);
  let left = rect.right - width;
  left = Math.max(8, Math.min(left, window.innerWidth - width - 8));

  panelStyle.value = {
    top: `${rect.bottom + PANEL_GAP}px`,
    left: `${left}px`,
    width: `${width}px`,
  };
}

function onDocumentClick(event: MouseEvent) {
  if (!open.value) return;

  const target = event.target as Node;
  if (rootRef.value?.contains(target) || panelRef.value?.contains(target)) {
    return;
  }

  open.value = false;
  activeId.value = null;
}

function onEscape(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    open.value = false;
    activeId.value = null;
  }
}

watch(open, (isOpen) => {
  if (!isOpen) {
    activeId.value = null;
    panelStyle.value = null;
    window.removeEventListener('resize', updatePanelPosition);
    window.removeEventListener('scroll', updatePanelPosition, true);
    return;
  }

  void notificationsStore.fetch(props.scope);
  requestAnimationFrame(updatePanelPosition);
  window.addEventListener('resize', updatePanelPosition);
  window.addEventListener('scroll', updatePanelPosition, true);
});

onMounted(() => {
  notificationsStore.hydrateDismissed();
  void notificationsStore.fetch(props.scope);
  document.addEventListener('click', onDocumentClick);
  document.addEventListener('keydown', onEscape);
});

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick);
  document.removeEventListener('keydown', onEscape);
  window.removeEventListener('resize', updatePanelPosition);
  window.removeEventListener('scroll', updatePanelPosition, true);
});
</script>

<style scoped>
.notifications-popover {
  position: relative;
}

.notifications-popover__trigger {
  position: relative;
  display: grid;
  place-items: center;
  width: 2.35rem;
  height: 2.35rem;
  border: 1px solid rgba(23, 33, 26, 0.09);
  border-radius: 999px;
  background: rgba(255, 253, 247, 0.62);
  backdrop-filter: blur(14px);
  color: var(--text-secondary);
  cursor: pointer;
  transition:
    background var(--motion-fast) ease,
    border-color var(--motion-fast) ease,
    color var(--motion-fast) ease,
    transform var(--motion-fast) ease;
}

.notifications-popover__trigger:hover,
.notifications-popover__trigger[aria-expanded='true'] {
  color: var(--text-primary);
  border-color: rgba(47, 93, 80, 0.22);
  background: rgba(47, 93, 80, 0.08);
  transform: translateY(-1px);
}

.notifications-popover__bell {
  width: 1.05rem;
  height: 1.05rem;
}

.notifications-popover__badge {
  position: absolute;
  top: -0.2rem;
  right: -0.15rem;
  min-width: 1.1rem;
  height: 1.1rem;
  padding: 0 0.25rem;
  border-radius: 999px;
  background: var(--color-municipal-green);
  color: #fff;
  font-size: 0.58rem;
  font-weight: 900;
  line-height: 1.1rem;
  text-align: center;
}

.notifications-popover__panel {
  position: fixed;
  z-index: var(--z-dropdown);
  overflow: hidden;
  border: 1px solid rgba(23, 33, 26, 0.1);
  border-radius: var(--radius-lg);
  background: rgba(255, 253, 247, 0.96);
  backdrop-filter: blur(16px);
  box-shadow: 0 18px 40px rgba(16, 20, 18, 0.14);
}

.notifications-popover__panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.7rem 0.85rem;
  border-bottom: 1px solid rgba(23, 33, 26, 0.08);
}

.notifications-popover__panel-title {
  font-size: var(--text-sm);
  font-weight: 850;
  color: var(--text-primary);
}

.notifications-popover__clear {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: 750;
  cursor: pointer;
}

.notifications-popover__clear:hover {
  color: var(--color-municipal-green);
}

.notifications-popover__list {
  max-height: 20rem;
  margin: 0;
  padding: 0;
  list-style: none;
  overflow: auto;
}

.notifications-popover__item {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid rgba(23, 33, 26, 0.06);
  transition: background var(--motion-fast) ease;
}

.notifications-popover__item:hover {
  background: rgba(47, 93, 80, 0.05);
}

.notifications-popover__item--active .notifications-popover__body {
  transform: translateX(-2.2rem);
}

.notifications-popover__body {
  flex: 1;
  min-width: 0;
  padding: 0.85rem 0.45rem 0.85rem 0.85rem;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: transform 220ms cubic-bezier(0.22, 1, 0.36, 1);
}

.notifications-popover__meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}

.notifications-popover__title {
  font-size: var(--text-sm);
  font-weight: 800;
  color: var(--text-primary);
}

.notifications-popover__time {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 750;
}

.notifications-popover__description {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  line-height: 1.45;
}

.notifications-popover__actions {
  display: flex;
  align-items: center;
  gap: 0.15rem;
  padding-right: 0.45rem;
}

.notifications-popover__action {
  display: grid;
  place-items: center;
  width: 1.75rem;
  height: 1.75rem;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: background var(--motion-fast) ease, color var(--motion-fast) ease;
}

.notifications-popover__action svg {
  width: 0.95rem;
  height: 0.95rem;
}

.notifications-popover__action:hover {
  background: rgba(23, 33, 26, 0.06);
  color: var(--text-primary);
}

.notifications-popover__action--danger:hover {
  background: rgba(200, 76, 58, 0.12);
  color: var(--color-repair-red);
}

.notifications-popover__empty {
  padding: 1rem 0.85rem;
  color: var(--text-muted);
  font-size: var(--text-sm);
  text-align: center;
}

.notifications-popover__empty--warn {
  color: var(--color-repair-red);
}

.notifications-panel-enter-active,
.notifications-panel-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.notifications-panel-enter-from,
.notifications-panel-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 640px) {
  .notifications-popover__list {
    max-height: min(50vh, 18rem);
  }
}

@media (prefers-reduced-motion: reduce) {
  .notifications-popover__body,
  .notifications-panel-enter-active,
  .notifications-panel-leave-active {
    transition: none;
  }

  .notifications-popover__item--active .notifications-popover__body {
    transform: none;
  }
}
</style>
