import { describe, expect, it } from 'vitest';

import { resolveApiBaseUrl } from './apiBaseUrl';

describe('resolveApiBaseUrl', () => {
  it('uses same-origin proxy for local backend URLs in dev', () => {
    expect(
      resolveApiBaseUrl({
        dev: true,
        configured: 'http://localhost:8001',
      }),
    ).toBe('');
  });

  it('keeps remote API URLs in dev', () => {
    expect(
      resolveApiBaseUrl({
        dev: true,
        configured: 'https://api.example.com',
      }),
    ).toBe('https://api.example.com');
  });

  it('uses configured URL in production builds', () => {
    expect(
      resolveApiBaseUrl({
        dev: false,
        configured: 'https://api.example.com',
      }),
    ).toBe('https://api.example.com');
  });
});
