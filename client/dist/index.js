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
        if (body !== undefined) {
            rInit.body = body;
        }
        headers = new Headers(headers);
        headers.append('Authorization', this.accessToken);
        if (this.sniffPlatform)
            headers.append('X-User-Platform', getPlatform());
        rInit.headers = headers;
        let url;
        if (this.baseURL) {
            url = new URL(endpoint, this.baseURL);
        }
        else {
            url = endpoint;
        }
        let resp = await (this.withRetries ? withRetries(() => fetch(url, rInit)) : fetch(url, rInit));
        if (resp.status == 401 && this.unauthed)
            this.unauthed();
        const newToken = resp.headers.get('X-Refreshed-Access-Token') ||
            resp.headers.get('X-Issued-Access-Token') ||
            resp.headers.get('X-Access-Token');
        if (newToken) {
            this.accessToken = newToken;
        }
        return resp;
    }
    get = async (endpoint, headers) => await this.makeRequest(endpoint, 'GET', undefined, headers || {});
    post = async (endpoint, body, headers) => await this.makeRequest(endpoint, 'POST', body, headers || {});
    put = async (endpoint, body, headers) => await this.makeRequest(endpoint, 'PUT', body, headers || {});
    delete = async (endpoint, body, headers) => await this.makeRequest(endpoint, 'DELETE', body, headers || {});
    patch = async (endpoint, body, headers) => await this.makeRequest(endpoint, 'PATCH', body, headers || {});
}
//# sourceMappingURL=index.js.map