import getPlatform from "./sniff.js";
import withRetries from "./retry.js";


export default class Client {
    private accessToken: string

    constructor (
        private baseURL?: string | URL,
        private unauthed?: () => void,
        private sniffPlatform: boolean = true,
        private withRetries: boolean = true
    ) {
        this.accessToken = ''
    }

    private async makeRequest(endpoint: string | URL, method: string, body: BodyInit | Record<string, unknown> | undefined, headers: HeadersInit): Promise<Response> {
        const rInit: RequestInit = {};
        rInit.method = method

        headers = new Headers(headers);
        headers.set('Authorization', `Bearer ${this.accessToken}`);
        if (this.sniffPlatform) headers.set('X-User-Platform', getPlatform());

        if (body !== undefined) {
            if (!(body instanceof FormData) && typeof body === 'object') {
                body = JSON.stringify(body);
                headers.set('Content-Type', 'application/json')
            }

            rInit.body = body
        }
        
        rInit.headers = headers;

        let url: URL | string;
        if (this.baseURL) {
            url = new URL(endpoint, this.baseURL)
        } else {
            url = endpoint;
        }

        let resp = await (this.withRetries ? withRetries(() => fetch(url, rInit)) : fetch(url, rInit));

        if (
            resp.status == 401 &&
            this.unauthed
        ) this.unauthed();
        
        const newToken = resp.headers.get('X-Refreshed-Access-Token') ||
                         resp.headers.get('X-Issued-Access-Token') ||
                         resp.headers.get('X-Access-Token');

        if (newToken) {
            this.accessToken = newToken;
        }

        return resp;
    }

    public get = (endpoint: string, headers?: HeadersInit): Promise<Response> => this.makeRequest(endpoint, 'GET', undefined, headers || {})
    public post = (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit): Promise<Response> => this.makeRequest(endpoint, 'POST', body, headers || {})
    public put = (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit): Promise<Response> => this.makeRequest(endpoint, 'PUT', body, headers || {})
    public delete = (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit): Promise<Response> => this.makeRequest(endpoint, 'DELETE', body, headers || {})
    public patch = (endpoint: string, body?: BodyInit | Record<string, unknown>, headers?: HeadersInit): Promise<Response> => this.makeRequest(endpoint, 'PATCH', body, headers || {})
}
