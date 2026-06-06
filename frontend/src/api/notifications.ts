import { apiGet } from './client';
import type { AppNotification, NotificationScope } from '@/types/notification';

export function listNotifications(
  scope: NotificationScope = 'all',
  limit = 40,
): Promise<AppNotification[]> {
  const params = new URLSearchParams({
    scope,
    limit: String(limit),
  });
  return apiGet<AppNotification[]>(`/api/v1/notifications?${params.toString()}`);
}
