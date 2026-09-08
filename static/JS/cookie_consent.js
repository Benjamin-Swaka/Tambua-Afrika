document.addEventListener('DOMContentLoaded', function () {
    const COOKIE_NAME = 'cookie_consent';
    const banner = document.getElementById('cookie-banner');
    const acceptForm = document.getElementById('cookie-accept-all-form');
    const rejectForm = document.getElementById('cookie-reject-all-form');
    const settingsForm = document.getElementById('cookie-settings-form');
    const analyticsCheckbox = document.getElementById('cookie-analytics');
    const marketingCheckbox = document.getElementById('cookie-marketing');

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function getConsent() {
        const raw = getCookie(COOKIE_NAME);
        if (raw) {
            try {
                return JSON.parse(decodeURIComponent(raw));
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    function applyConsent(consent) {
        // Placeholder hook for gating analytics/marketing scripts.
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

    // Submit a consent form via fetch so the choice is recorded on the
    // server (audit trail) and the response Set-Cookie header is honoured
    // by the browser, without a full page reload. Falls back to a normal
    // form POST automatically if fetch/JS is unavailable.
    function submitConsentForm(form) {
        if (!form) return;
        form.addEventListener('submit', function onSubmit(e) {
            e.preventDefault();
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                credentials: 'same-origin',
                redirect: 'follow',
            }).then(function () {
                hideBanner();
                const consent = getConsent();
                if (consent) applyConsent(consent);
            }).catch(function () {
                // Network hiccup — let the browser do a real submit instead.
                form.removeEventListener('submit', onSubmit);
                form.submit();
            });
        });
    }

    submitConsentForm(acceptForm);
    submitConsentForm(rejectForm);

    if (settingsForm && analyticsCheckbox && marketingCheckbox) {
        const consent = getConsent();
        if (consent) {
            analyticsCheckbox.checked = !!consent.analytics;
            marketingCheckbox.checked = !!consent.marketing;
        }
        // No preventDefault here: let the settings page do a real POST to
        // the Django view, so it's recorded server-side and works with JS
        // disabled too. The view redirects back afterwards.
    }

    showBannerIfNeeded();
});
