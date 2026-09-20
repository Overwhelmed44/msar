import getPlatform from "./sniff.js";
import withRetries from "./retry.js";
export default class Client {
    baseURL;
    unauthed;
    sniffPlatform;
    withRetries;
    accessToken;
    constructor(baseURL, unauthed, sniffPlatform = true, withRetries = true) {
        this.baseURL = baseURL;
        this.unauthed = unauthed;
        this.sniffPlatform = sniffPlatform;
        this.withRetries = withRetries;
        this.accessToken = '';
    }
    async makeRequest(endpoint, method, body, headers) {
        const rInit = {};
        rInit.method = method;
        headers = new Headers(headers);
        headers.set('Authorization', `Bearer ${this.accessToken}`);
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