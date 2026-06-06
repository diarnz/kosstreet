export type NotificationScope = 'dashboard' | 'audit' | 'all';

export interface AppNotification {
  id: string;
  title: string;
  description: string;
  created_at: string;
  scope: 'dashboard' | 'audit';
  kind: string;
  target_id: string | null;
}
