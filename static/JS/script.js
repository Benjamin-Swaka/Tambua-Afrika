document.addEventListener('DOMContentLoaded', function() {
    /* ─────────────────────────────────────────────
       1. COOKIE CONSENT
    ───────────────────────────────────────────── */
    const COOKIE_NAME = 'cookie_consent';
    const banner = document.getElementById('cookie-banner');
    const acceptForm = document.getElementById('cookie-accept-all-form');
    const rejectForm = document.getElementById('cookie-reject-all-form');
    const acceptButton = document.getElementById('cookie-accept-all');
    const rejectButton = document.getElementById('cookie-reject-all');
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
                return JSON.parse(decodeURIComponent(raw));
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    function applyConsent(consent) {
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

    // For form-based accept/reject (server audit), intercept submission
    function submitConsentForm(form, consentValue) {
        if (!form) return;
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // Set cookie client-side first
            setCookie(COOKIE_NAME, JSON.stringify(consentValue), 365);
            hideBanner();
            applyConsent(consentValue);

            // Then send to server via fetch for audit trail (optional)
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                credentials: 'same-origin',
                redirect: 'follow',
            }).catch(() => { /* ignore network errors */ });
        });
    }

    // If forms exist, wire them up
    if (acceptForm) {
        submitConsentForm(acceptForm, { essential: true, analytics: true, marketing: true });
    }
    if (rejectForm) {
        submitConsentForm(rejectForm, { essential: true, analytics: false, marketing: false });
    }

    // Button fallback (if no forms, use buttons)
    if (acceptButton && !acceptForm) {
        acceptButton.addEventListener('click', function() {
            const consent = { essential: true, analytics: true, marketing: true };
            setCookie(COOKIE_NAME, JSON.stringify(consent), 365);
            hideBanner();
            applyConsent(consent);
        });
    }
    if (rejectButton && !rejectForm) {
        rejectButton.addEventListener('click', function() {
            const consent = { essential: true, analytics: false, marketing: false };
            setCookie(COOKIE_NAME, JSON.stringify(consent), 365);
            hideBanner();
            applyConsent(consent);
        });
    }

    // Settings page: prefill checkboxes and allow normal form POST
    if (settingsForm && analyticsCheckbox && marketingCheckbox) {
        const consent = getConsent();
        if (consent) {
            analyticsCheckbox.checked = !!consent.analytics;
            marketingCheckbox.checked = !!consent.marketing;
        }
        // No preventDefault – let the form submit normally to Django view
    }

    // Initial banner check
    showBannerIfNeeded();

    /* ─────────────────────────────────────────────
       2. NEWSLETTER SUBSCRIPTION (AJAX)
    ───────────────────────────────────────────── */
    const newsletterForm = document.getElementById('newsletter-form');
    const responseContainer = document.getElementById('newsletter-response');
    const consentCheckbox = document.getElementById('footer-consent');
    const consentError = document.getElementById('consent-error');

    // Helper: format field names
    function formatFieldName(key) {
        const map = { 'email': 'Email', 'consent': 'Consent' };
        return map[key] || key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ');
    }

    // Helper: build friendly error message
    function buildErrorMessage(errors) {
        const parts = Object.entries(errors).map(([field, messages]) => {
            const label = formatFieldName(field);
            const msg = messages.join(' ');
            return `${label}: ${msg}`;
        });
        return parts.join(' • ');
    }

    if (newsletterForm && responseContainer) {
        const submitBtn = newsletterForm.querySelector('button[type="submit"]');

        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Reset messages
            responseContainer.style.display = 'none';
            responseContainer.className = 'ta-footer-response';
            responseContainer.textContent = '';
            if (consentError) consentError.style.display = 'none';

            // Frontend validation
            if (consentCheckbox && !consentCheckbox.checked) {
                if (consentError) {
                    consentError.style.display = 'block';
                    consentError.textContent = 'You must agree to receive emails.';
                }
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Sending…';
            }

            const formData = new FormData(newsletterForm);
            const url = newsletterForm.action;

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                return response.json().then(data => {
                    if (!response.ok) {
                        return Promise.reject({ status: response.status, data });
                    }
                    return data;
                });
            })
            .then(data => {
                responseContainer.style.display = 'block';

                if (data.status === 'success') {
                    responseContainer.className = 'ta-footer-response success';
                    responseContainer.innerHTML = `<span style="margin-right:6px;">✅</span> ${data.message}`;
                    newsletterForm.reset();
                    setTimeout(() => {
                        responseContainer.style.display = 'none';
                    }, 5000);

                } else if (data.status === 'info') {
                    responseContainer.className = 'ta-footer-response info';
                    responseContainer.innerHTML = `<span style="margin-right:6px;">ℹ️</span> ${data.message}`;

                } else if (data.status === 'error') {
                    responseContainer.className = 'ta-footer-response error';
                    let msg = data.message || 'Please check your input.';
                    if (data.errors) {
                        msg = buildErrorMessage(data.errors);
                    }
                    responseContainer.innerHTML = `<span style="margin-right:6px;">⚠️</span> ${msg}`;
                }

            })
            .catch(error => {
                responseContainer.style.display = 'block';
                responseContainer.className = 'ta-footer-response error';

                let msg = 'Something went wrong. Please try again.';
                if (error.data) {
                    if (error.data.errors) {
                        msg = buildErrorMessage(error.data.errors);
                    } else if (error.data.message) {
                        msg = error.data.message;
                    }
                }
                responseContainer.innerHTML = `<span style="margin-right:6px;">⚠️</span> ${msg}`;

            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    // Restore arrow SVG
                    submitBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                        <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>`;
                }
            });
        });

        // Hide consent error when checkbox is checked
        if (consentCheckbox) {
            consentCheckbox.addEventListener('change', function() {
                if (this.checked && consentError) {
                    consentError.style.display = 'none';
                }
            });
        }

        // Clear error when user types in email
        const emailInput = document.getElementById('footer-email');
        if (emailInput) {
            emailInput.addEventListener('input', function() {
                if (responseContainer.style.display === 'block' && 
                    responseContainer.classList.contains('error')) {
                    responseContainer.style.display = 'none';
                }
            });
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {

    const userPill = document.querySelector('.nav-user-pill');
    if (!userPill) return;

    // Get the dashboard URL from the data attribute (fallback to home)
    const dashboardUrl = userPill.dataset.dashboardUrl || '/';

    function isMobile() {
        return window.innerWidth <= 991;
    }

    function setupMobileBehavior() {
        if (isMobile()) {
            // 1. Remove all dropdown-related attributes
            userPill.removeAttribute('data-bs-toggle');
            userPill.removeAttribute('aria-expanded');
            userPill.setAttribute('role', 'link');

            // 2. Hide the dropdown menu
            const dropdownMenu = userPill.nextElementSibling;
            if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                dropdownMenu.style.display = 'none';
            }

            // 3. Replace click handler – redirect immediately
            userPill.onclick = function (e) {
                e.preventDefault();
                e.stopPropagation();   // prevent any other handlers
                window.location.href = dashboardUrl;
            };

            // 4. Remove the chevron (optional)
            const chevron = userPill.querySelector('.nav-chevron');
            if (chevron) chevron.style.display = 'none';

        } else {
            // Restore desktop behaviour
            userPill.setAttribute('data-bs-toggle', 'dropdown');
            userPill.setAttribute('aria-expanded', 'false');
            userPill.removeAttribute('role');
            const dropdownMenu = userPill.nextElementSibling;
            if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                dropdownMenu.style.display = '';
            }
            userPill.onclick = null;
            const chevron = userPill.querySelector('.nav-chevron');
            if (chevron) chevron.style.display = '';
        }
    }

    // Run on load and on resize
    setupMobileBehavior();
    window.addEventListener('resize', setupMobileBehavior);
});
