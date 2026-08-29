document.addEventListener('DOMContentLoaded', function () {
    const COOKIE_NAME = 'cookie_consent';
    const banner = document.getElementById('cookie-banner');
    const acceptAllBtn = document.getElementById('cookie-accept-all');
    const rejectAllBtn = document.getElementById('cookie-reject-all');
    const settingsForm = document.getElementById('cookie-settings-form');
    const analyticsCheckbox = document.getElementById('cookie-analytics');
    const marketingCheckbox = document.getElementById('cookie-marketing');

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value}; expires=${date.toUTCString()}; path=/; SameSite=Lax`;
    }

    function getConsent() {
        const raw = getCookie(COOKIE_NAME);
        if (raw) {
            try {
                return JSON.parse(raw);
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    function applyConsent(consent) {
        // Placeholder for analytics / marketing scripts
        if (consent.analytics) console.log('Analytics enabled');
        if (consent.marketing) console.log('Marketing enabled');
    }

    function hideBanner() {
        if (banner) banner.style.display = 'none';
    }

    function showBannerIfNeeded() {
        const consent = getConsent();
        if (!consent) {
            if (banner) banner.style.display = 'flex';
        } else {
            hideBanner();
            applyConsent(consent);
        }
    }

    if (acceptAllBtn) {
        acceptAllBtn.addEventListener('click', function () {
            const consent = { essential: true, analytics: true, marketing: true };
            setCookie(COOKIE_NAME, JSON.stringify(consent), 365);
            hideBanner();
            applyConsent(consent);
        });
    }

    if (rejectAllBtn) {
        rejectAllBtn.addEventListener('click', function () {
            const consent = { essential: true, analytics: false, marketing: false };
            setCookie(COOKIE_NAME, JSON.stringify(consent), 365);
            hideBanner();
            applyConsent(consent);
        });
    }

    if (settingsForm && analyticsCheckbox && marketingCheckbox) {
        const consent = getConsent();
        if (consent) {
            analyticsCheckbox.checked = consent.analytics;
            marketingCheckbox.checked = consent.marketing;
        }

        settingsForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const newConsent = {
                essential: true,
                analytics: analyticsCheckbox.checked,
                marketing: marketingCheckbox.checked,
            };
            setCookie(COOKIE_NAME, JSON.stringify(newConsent), 365);
            applyConsent(newConsent);
            window.location.href = settingsForm.getAttribute('data-redirect') || '/';
        });
    }

    showBannerIfNeeded();
});