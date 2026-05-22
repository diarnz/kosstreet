export interface ApiErrorBody {
  detail?: string;
  message?: string;
}

export class ApiError extends Error {
  status: number;
  body: ApiErrorBody | unknown;

  constructor(message: string, status: number, body: ApiErrorBody | unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

export interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
}

