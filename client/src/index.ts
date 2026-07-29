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

    private async makeRequest(endpoint: string | URL, method: string, body: BodyInit | undefined, headers: HeadersInit): Promise<Response> {
        const rInit: RequestInit = {};
        rInit.method = method

        if (body !== undefined) {
            rInit.body = body
        }

        headers = new Headers(headers);
        headers.append('Authorization', this.accessToken);
        if (this.sniffPlatform) headers.append('X-User-Platform', getPlatform());
        rInit.headers = headers;

        let url: URL | string;
        if (this.baseURL) {
            url = new URL(endpoint, this.baseURL)
        } else {
            url = endpoint;
        }

        let resp = await (this.withRetries ? withRetries(() => fetch(url, rInit)) : fetch(url, rInit));

        if (resp.status == 401 && this.unauthed) this.unauthed();
        
        const newToken = resp.headers.get('X-Refreshed-Access-Token') ||
                         resp.headers.get('X-Issued-Access-Token') ||
                         resp.headers.get('X-Access-Token');

        if (newToken) {
            this.accessToken = newToken;
        }

        return resp;
    }

    public get = async (endpoint: string, headers?: HeadersInit): Promise<Response> => await this.makeRequest(endpoint, 'GET', undefined, headers || {})
    public post = async (endpoint: string, body?: BodyInit, headers?: HeadersInit): Promise<Response> => await this.makeRequest(endpoint, 'POST', body, headers || {})
    public put = async (endpoint: string, body?: BodyInit, headers?: HeadersInit): Promise<Response> => await this.makeRequest(endpoint, 'PUT', body, headers || {})
    public delete = async (endpoint: string, body?: BodyInit, headers?: HeadersInit): Promise<Response> => await this.makeRequest(endpoint, 'DELETE', body, headers || {})
    public patch = async (endpoint: string, body?: BodyInit, headers?: HeadersInit): Promise<Response> => await this.makeRequest(endpoint, 'PATCH', body, headers || {})
}
