export default class Client {
    private baseURL?;
    private unauthed?;
    private sniffPlatform;
    private withRetries;
    private accessToken;
    host: string;
    constructor(baseURL?: string | URL | undefined, unauthed?: (() => void) | undefined, sniffPlatform?: boolean, withRetries?: boolean);
    private makeRequest;
    get: (endpoint: string, headers?: HeadersInit) => Promise<Response>;
    post: (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit) => Promise<Response>;
    put: (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit) => Promise<Response>;
    delete: (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit) => Promise<Response>;
    patch: (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit) => Promise<Response>;
}
//# sourceMappingURL=index.d.ts.map