import { resolveApiBaseUrl } from '@/utils/apiBaseUrl';

const API_BASE_URL = resolveApiBaseUrl();
const ADMIN_KEY_STORAGE = 'kostreet_admin_key';

export function getStoredAdminKey(): string {
  return sessionStorage.getItem(ADMIN_KEY_STORAGE) ?? '';
}

export function setStoredAdminKey(key: string): void {
  sessionStorage.setItem(ADMIN_KEY_STORAGE, key);
}

export function clearStoredAdminKey(): void {
  sessionStorage.removeItem(ADMIN_KEY_STORAGE);
}

export async function adminRequest<T>(
  path: string,
  adminKey: string,
  options: { method?: string; body?: unknown } = {},
): Promise<T> {
  const headers: Record<string, string> = {
    'X-Admin-Key': adminKey,
  };

  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail =
      body && typeof body === 'object' && 'detail' in body && typeof body.detail === 'string'
        ? body.detail
        : `Admin request failed (${response.status})`;
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
