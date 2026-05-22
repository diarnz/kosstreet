import { resolveApiBaseUrl } from '@/utils/apiBaseUrl';

const API_BASE_URL = resolveApiBaseUrl();

export function resolveApiAssetUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }

  if (path.startsWith('/demo/')) {
    return path;
  }

  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}
