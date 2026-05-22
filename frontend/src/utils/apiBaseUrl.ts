const LOCAL_API_HOST_PATTERN = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/;

type ResolveApiBaseUrlOptions = {
  dev?: boolean;
  configured?: string;
};

export function resolveApiBaseUrl(options: ResolveApiBaseUrlOptions = {}): string {
  const dev = options.dev ?? import.meta.env.DEV;
  const configured = (options.configured ?? import.meta.env.VITE_API_BASE_URL)?.replace(/\/$/, '');

  if (!dev) {
    return configured || 'http://localhost:8000';
  }

  // In dev, same-origin requests go through the Vite proxy and avoid CORS.
  if (!configured || LOCAL_API_HOST_PATTERN.test(configured)) {
    return '';
  }

  return configured;
}
