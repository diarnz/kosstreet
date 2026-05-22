import { ApiError, type ApiRequestOptions } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function parseResponseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type');

  if (response.status === 204) {
    return undefined;
  }

  if (contentType?.includes('application/json')) {
    return response.json();
  }

  return response.text();
}

function buildApiErrorMessage(status: number, body: unknown): string {
  if (body && typeof body === 'object') {
    const detail = 'detail' in body ? body.detail : undefined;
    const message = 'message' in body ? body.message : undefined;

    if (typeof detail === 'string') {
      return detail;
    }

    if (typeof message === 'string') {
      return message;
    }
  }

  return `API request failed with status ${status}`;
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);

  if (options.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  const body = await parseResponseBody(response);

  if (!response.ok) {
    throw new ApiError(buildApiErrorMessage(response.status, body), response.status, body);
  }

  return body as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>(path);
}

export function apiPost<TResponse, TPayload>(path: string, payload: TPayload): Promise<TResponse> {
  return apiRequest<TResponse>(path, { method: 'POST', body: payload });
}

export function apiPatch<TResponse, TPayload>(path: string, payload: TPayload): Promise<TResponse> {
  return apiRequest<TResponse>(path, { method: 'PATCH', body: payload });
}
