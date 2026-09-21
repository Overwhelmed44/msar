import getPlatform from "./sniff.js";
import withRetries from "./retry.js";
export default class Client {
    baseURL;
    unauthed;
    sniffPlatform;
    withRetries;
    accessToken;
    host;
    constructor(baseURL, unauthed, sniffPlatform = true, withRetries = true) {
        this.baseURL = baseURL;
        this.unauthed = unauthed;
        this.sniffPlatform = sniffPlatform;
        this.withRetries = withRetries;
        this.accessToken = '';
        const hostname = window.location.hostname;
        const spl = hostname.split('.');
        if (spl.length == 2) {
            this.host = hostname;
        }
        else {
            this.host = spl.slice(1).join('.');
        }
    }
    async makeRequest(endpoint, method, body, headers) {
        const rInit = {};
        rInit.method = method;
        rInit.credentials = 'include';
        headers = new Headers(headers);
        headers.set('Authorization', (this.accessToken ? `Bearer ${this.accessToken}` : ''));
        if (this.sniffPlatform)
            headers.set('X-User-Platform', getPlatform());
        if (body !== undefined) {
            if (!(body instanceof FormData) && typeof body === 'object') {
                body = JSON.stringify(body);
                headers.set('Content-Type', 'application/json');
            }
            rInit.body = body;
        }
        rInit.headers = headers;
        let url;
        if (this.baseURL) {
            url = new URL(endpoint, this.baseURL);
        }
        else {
            url = endpoint;
        }
        let resp = await (this.withRetries ? withRetries(() => fetch(url, rInit)) : fetch(url, rInit));
        if (resp.status == 401 &&
            this.unauthed)
            this.unauthed();
        const newToken = resp.headers.get('X-Refreshed-Access-Token') ||
            resp.headers.get('X-Issued-Access-Token') ||
            resp.headers.get('X-Access-Token');
        if (newToken) {
            this.accessToken = newToken;
        }
        return resp;
    }
    get = (endpoint, headers) => this.makeRequest(endpoint, 'GET', undefined, headers || {});
    post = (endpoint, body, headers) => this.makeRequest(endpoint, 'POST', body, headers || {});
    put = (endpoint, body, headers) => this.makeRequest(endpoint, 'PUT', body, headers || {});
    delete = (endpoint, body, headers) => this.makeRequest(endpoint, 'DELETE', body, headers || {});
    patch = (endpoint, body, headers) => this.makeRequest(endpoint, 'PATCH', body, headers || {});
}
//# sourceMappingURL=index.js.map