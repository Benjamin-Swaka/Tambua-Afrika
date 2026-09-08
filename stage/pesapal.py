"""
Thin wrapper around Pesapal's API v3 (JSON).

Docs: https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json

Flow used by stage/views.py:
  1. submit_order(...)              -> get a redirect_url, send the buyer there
  2. Pesapal redirects the buyer back to our callback_url with
     OrderTrackingId + OrderMerchantReference in the query string
  3. Pesapal also calls our IPN URL server-to-server with the same params
  4. Either handler calls get_transaction_status(order_tracking_id) and
     trusts THAT response, not the query params (which aren't proof of
     payment on their own).

None of this touches the ticket's manual "I've paid, here's my M-Pesa
code" flow -- that stays as a fallback in case Pesapal is unreachable.
"""
import requests
from django.conf import settings


class PesapalError(Exception):
    pass


def _headers(token=None):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_access_token():
    """Access tokens are valid for ~5 minutes -- callers should fetch a
    fresh one per request rather than caching it long-term."""
    if not settings.PESAPAL_CONSUMER_KEY or not settings.PESAPAL_CONSUMER_SECRET:
        raise PesapalError(
            "PESAPAL_CONSUMER_KEY / PESAPAL_CONSUMER_SECRET are not set. "
            "Add them to your .env file."
        )

    url = f"{settings.PESAPAL_BASE_URL}/Auth/RequestToken"
    payload = {
        "consumer_key": settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET,
    }
    response = requests.post(url, json=payload, headers=_headers(), timeout=15)
    data = response.json()

    token = data.get("token")
    if not token:
        raise PesapalError(f"Failed to get Pesapal access token: {data}")
    return token


def register_ipn(ipn_url, notification_type="GET"):
    """Registers a URL Pesapal will call on payment status changes.
    Run this once (via the `register_pesapal_ipn` management command)
    and store the returned `ipn_id` in PESAPAL_IPN_ID."""
    token = get_access_token()
    url = f"{settings.PESAPAL_BASE_URL}/URLSetup/RegisterIPN"
    payload = {"url": ipn_url, "ipn_notification_type": notification_type}
    response = requests.post(url, json=payload, headers=_headers(token), timeout=15)
    data = response.json()

    if not data.get("ipn_id"):
        raise PesapalError(f"Failed to register IPN URL: {data}")
    return data


def submit_order(order_id, amount, description, callback_url, billing_address, currency="KES"):
    """
    order_id: our unique reference for this payment -- we use the
              ticket_code, so Pesapal's merchant_reference maps 1:1
              back to a Ticket row with no separate lookup table needed.
    Returns dict with order_tracking_id / redirect_url on success.
    """
    if not settings.PESAPAL_IPN_ID:
        raise PesapalError(
            "PESAPAL_IPN_ID is not set. Run `python manage.py register_pesapal_ipn` "
            "once and add the printed ID to your .env file."
        )

    token = get_access_token()
    url = f"{settings.PESAPAL_BASE_URL}/Transactions/SubmitOrderRequest"
    payload = {
        "id": order_id,
        "currency": currency,
        "amount": float(amount),
        "description": description[:100],
        "callback_url": callback_url,
        "notification_id": settings.PESAPAL_IPN_ID,
        "billing_address": billing_address,
    }
    response = requests.post(url, json=payload, headers=_headers(token), timeout=15)
    data = response.json()

    if not data.get("redirect_url"):
        raise PesapalError(f"Failed to submit Pesapal order: {data}")
    return data


def get_transaction_status(order_tracking_id):
    token = get_access_token()
    url = f"{settings.PESAPAL_BASE_URL}/Transactions/GetTransactionStatus"
    response = requests.get(
        url,
        params={"orderTrackingId": order_tracking_id},
        headers=_headers(token),
        timeout=15,
    )
    return response.json()


def is_payment_successful(status_data):
    """Pesapal's own docs use payment_status_description as the
    human-readable source of truth ("Completed" / "Failed" / "Invalid" /
    "Pending"); status_code 1 means the same thing numerically. Check
    both so a quirk in one doesn't cause a false negative."""
    description = (status_data or {}).get("payment_status_description", "")
    status_code = (status_data or {}).get("status_code")
    return description == "Completed" or status_code == 1
