export default async function withRetries(fn: () => Promise<Response>, max: number = 3): Promise<Response> {
    let r: Response

    let delay: number;
    let iter = 1;

    do {
        r = await fn();

        if (r.status == 401) {
            // Could fail due to a race condition when rotating JWT
            console.warn(`Failed with ${r.status}. Retrying in 2s...`);

            await new Promise(resolve => setTimeout(resolve, 2000))

            return await fn()
        }

        if (!(r.status == 429 || Math.floor(r.status / 100) == 5) || --max <= 0) {
            break
        }

        delay = 1000 * 2 ** (iter++ - 1);
        console.warn(`Failed with ${r.status}. Retrying in ${delay / 1000}s...`);

        await new Promise(resolve => setTimeout(resolve, delay))
    } while (max > 0);

    return r;
}
