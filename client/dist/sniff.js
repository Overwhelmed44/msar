export default function getPlatform() {
    const ua = navigator.userAgent || navigator.vendor;
    if (/iPhone|iPad|iPod/i.test(ua)) {
        return "iPhone";
    }
    if (/Macintosh/i.test(ua) && "ontouchend" in document) {
        return "iPhone";
    }
    if (/Android/i.test(ua)) {
        return "Android";
    }
    if (/Win/i.test(ua)) {
        return "Windows";
    }
    if (/Mac/i.test(ua)) {
        return "Mac";
    }
    if (/Linux/i.test(ua)) {
        return "Linux";
    }
    return screen.width > screen.height ? 'Windows' : 'Android';
}
//# sourceMappingURL=sniff.js.map