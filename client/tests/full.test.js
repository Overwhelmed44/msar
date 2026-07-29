// client.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock the DIST files (not the source files)
vi.mock('../dist/sniff.js', () => ({
  default: vi.fn(() => 'desktop')
}));

vi.mock('../dist/retry.js', () => ({
  default: vi.fn((fn) => fn())
}));

// Now import from dist
import Client from '../dist/index.js';
import getPlatform from '../dist/sniff.js';
import withRetries from '../dist/retry.js';

describe('Client', () => {
  const mockFetch = vi.fn();
  
  beforeEach(() => {
    global.fetch = mockFetch;
    vi.clearAllMocks();
    vi.mocked(getPlatform).mockReturnValue('desktop');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ========== CORE REQUEST LOGIC ==========
  describe('makeRequest', () => {
    it('should make HTTP requests with correct method and URL', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL);
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      await client.get('/users');

      expect(mockFetch).toHaveBeenCalledWith(
        new URL('https://api.example.com/users'),
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('should include Authorization header', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL);
      client.accessToken = 'test-token';
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      await client.get('/users');

      const headers = mockFetch.mock.calls[0][1]?.headers;
      expect(headers.get('Authorization')).toBe('test-token');
    });

    it('should include platform header when sniffPlatform is true', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL, undefined, true);
      vi.mocked(getPlatform).mockReturnValue('mobile');
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      await client.get('/users');

      const headers = mockFetch.mock.calls[0][1]?.headers;
      expect(headers.get('X-User-Platform')).toBe('mobile');
    });

    it('should NOT include platform header when sniffPlatform is false', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL, undefined, false);
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      await client.get('/users');

      const headers = mockFetch.mock.calls[0][1]?.headers;
      expect(headers.has('X-User-Platform')).toBe(false);
    });

    it('should include custom headers', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL);
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      await client.get('/users', { 'X-Custom': 'value' });

      const headers = mockFetch.mock.calls[0][1]?.headers;
      expect(headers.get('X-Custom')).toBe('value');
    });

    it('should send body with requests', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL);
      mockFetch.mockResolvedValue(new Response(null, { status: 201 }));

      const body = JSON.stringify({ name: 'Test' });
      await client.post('/users', body);

      expect(mockFetch.mock.calls[0][1]?.body).toBe(body);
    });

    it('should use retries when enabled', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL, undefined, false, true);
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      await client.get('/users');

      expect(withRetries).toHaveBeenCalled();
    });

    it('should NOT use retries when disabled', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL, undefined, false, false);
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      await client.get('/users');

      expect(withRetries).not.toHaveBeenCalled();
    });

    it('should call unauthed callback on 401', async () => {
      const baseURL = new URL('https://api.example.com');
      const unauthedMock = vi.fn();
      const client = new Client(baseURL, unauthedMock);
      mockFetch.mockResolvedValue(new Response(null, { status: 401 }));

      await client.get('/users');

      expect(unauthedMock).toHaveBeenCalled();
    });

    it('should update token from response headers', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL);
      client.accessToken = 'old-token';
      
      const headers = new Headers();
      headers.set('X-Refreshed-Access-Token', 'new-token');
      
      mockFetch.mockResolvedValue(new Response(null, { 
        status: 200,
        headers: headers
      }));

      await client.get('/users');

      expect(client.accessToken).toBe('new-token');
    });

    it('should propagate network errors', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL);
      mockFetch.mockRejectedValue(new Error('Network error'));

      await expect(client.get('/users')).rejects.toThrow('Network error');
    });
  });

  // ========== VERIFY ALL HTTP METHODS WORK ==========
  describe('all HTTP methods', () => {
    it('should support GET, POST, PUT, DELETE, PATCH', async () => {
      const baseURL = new URL('https://api.example.com');
      const client = new Client(baseURL);
      mockFetch.mockResolvedValue(new Response(null, { status: 200 }));

      const methods = ['get', 'post', 'put', 'delete', 'patch'];
      
      for (const method of methods) {
        await client[method]('/test');
      }

      const calls = mockFetch.mock.calls;
      expect(calls[0][1]?.method).toBe('GET');
      expect(calls[1][1]?.method).toBe('POST');
      expect(calls[2][1]?.method).toBe('PUT');
      expect(calls[3][1]?.method).toBe('DELETE');
      expect(calls[4][1]?.method).toBe('PATCH');
    });
  });
});
