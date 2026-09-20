from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import NewsletterForm, CampaignForm, RewardFormSet, PledgeForm
from .models import (
    ContactMessage, Department, HomeDepartment, UserProfile, DepartmentMembership, ConsentLog, FeaturedWork, OpenCall,
    ShopHighlight, Campaign, Reward, Pledge,
)
from django.db.models import Q
from itertools import chain, groupby
from operator import attrgetter
from shop.models import Product
from comics.models import Comic
from journal.models import Article
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import uuid
import requests
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from .forms import NewsletterForm
from .models import NewsletterSubscriber
from urllib.parse import quote
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from .forms import ContactForm
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.urls import reverse
from .forms import ContactForm
from types import SimpleNamespace
from django.urls import reverse
from stage.models import Show 


def _shop_highlights(limit=8):
    """Latest products, reshaped for the home carousel — no separate
    admin entry required. Add a Product in the shop admin and it
    appears here automatically."""
    highlights = []
    for product in Product.objects.order_by('-created_at')[:limit]:
        highlights.append(SimpleNamespace(
            title=product.name,
            description=product.description,
            price_label=f"KES {product.price}",
            image=product.image,
            icon_emoji='🛍️',
            background_color='#e8e0d8',
            link_url=f"{reverse('shop_home')}?category={product.category}",
            link_text='Shop Now',
        ))
    return highlights


def _featured_works(limit=6):
    """Latest comics + shows, reshaped for the home carousel. Add a
    Comic in the comics admin or a Show in the stage admin and it
    appears here automatically. (Ink isn't wired in yet — plug its
    model in here the same way once it's available.)"""
    works = []

    for comic in Comic.objects.order_by('-created_at')[:limit]:
        works.append(SimpleNamespace(
            title=comic.title,
            department_label='Tambua Afrika Comics',
            category_display='Comic',
            author_meta=f"by {comic.artist}",
            image=comic.cover_image,
            icon_emoji='🎨',
            background_color='#e8e0d8',
            link_url=reverse('comic_detail', args=[comic.pk]),
            link_text='Read More',
        ))

    for show in Show.objects.filter(is_active=True).order_by('-date')[:limit]:
        works.append(SimpleNamespace(
            title=show.title,
            department_label='Tambua Afrika Stage',
            category_display='Play',
            author_meta=f"{show.venue} · {show.date:%d %b %Y}",
            image=show.image,
            icon_emoji='🎭',
            background_color='#e8e0d8',
            link_url=reverse('show_detail', kwargs={'slug': show.slug}),
            link_text='Get Tickets',
        ))

    return works[:limit]


def home(request):
    context = {
        'departments':    HomeDepartment.objects.filter(is_active=True).order_by('order', 'name'),
        'featured_works': _featured_works(),
        'open_calls':     OpenCall.objects.filter(is_active=True),
        'shop_highlights': _shop_highlights(),
    }
    return render(request, 'core/home.html', context)

def cookie_settings(request):
    if request.method == 'POST':
        analytics = request.POST.get('analytics') == 'on'
        marketing = request.POST.get('marketing') == 'on'
        consent = {
            'essential': True,
            'analytics': analytics,
            'marketing': marketing,
        }
        next_url = request.GET.get('next', '/')
        response = HttpResponseRedirect(next_url)
        response.set_cookie(
            'cookie_consent',
            quote(json.dumps(consent)),   # <-- percent-encode
            max_age=365 * 24 * 60 * 60,
            samesite='Lax',
        )
        return response
    else:
        return render(request, 'cookies/cookie_settings.html')




def about(request):
    return render(request, 'core/about.html')

def privacy_policy(request):
    return render(request, 'core/privacy.html')

def terms_conditions(request):
    return render(request, 'core/terms.html')

def copyright_policy(request):
    return render(request, 'core/copyright.html')



def subscribe_newsletter(request):
    """
    Handles newsletter subscription via AJAX or regular POST.
    Returns JSON for AJAX requests; otherwise uses Django messages.
    """
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if form.is_valid():
            email = form.cleaned_data['email']
            consent = form.cleaned_data.get('consent', False)

            try:
                subscriber = NewsletterSubscriber.objects.get(email=email)
                if subscriber.is_active:
                    msg = 'You are already subscribed to our newsletter.'
                    if is_ajax:
                        return JsonResponse({'status': 'info', 'message': msg})
                    messages.info(request, msg)
                else:
                    # Reactivate inactive subscriber
                    subscriber.is_active = True
                    subscriber.consent = consent
                    subscriber.save()
                    msg = 'Welcome back! You have been resubscribed.'
                    if is_ajax:
                        return JsonResponse({'status': 'success', 'message': msg})
                    messages.success(request, msg)
            except NewsletterSubscriber.DoesNotExist:
                # New subscriber
                NewsletterSubscriber.objects.create(
                    email=email,
                    consent=consent,
                    is_active=True
                )
                msg = 'Thank you for subscribing to our creative community!'
                if is_ajax:
                    return JsonResponse({'status': 'success', 'message': msg})
                messages.success(request, msg)

            # Non‑AJAX redirect after handling
            if not is_ajax:
                return redirect('home')

        else:
            # Form invalid (e.g., malformed email, missing consent)
            if is_ajax:
                errors = {}
                for field, err_list in form.errors.items():
                    errors[field] = [str(err) for err in err_list]
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            else:
                for field, err_list in form.errors.items():
                    for err in err_list:
                        messages.error(request, f'{field}: {err}')
                return redirect('home')

    # GET request – shouldn't happen, but redirect safely
    return redirect('home')


def team(request):
    return render(request, 'core/team.html')




def global_search(request):
    query = request.GET.get('q')
    results = []

    if query:
        # Search Products
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        # Search Comics
        comics = Comic.objects.filter(
            Q(title__icontains=query) | Q(artist__icontains=query)
        )
        # Search Journal
        articles = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

        # Combine results (You can also use a list of dictionaries to keep track of type)
        results = list(chain(products, comics, articles))

    return render(request, 'core/search_results.html', {'results': results, 'query': query})


@login_required
def select_department(request):
    """
    Lets a signed-in user pick which studio/department they primarily
    belong to. This is entirely optional -- a user can skip it and use
    the site without belonging to any department, and can come back to
    change their selection at any time (e.g. from Profile & Settings).
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    departments = Department.objects.all()

    if request.method == 'POST':
        if request.POST.get('skip'):
            profile.onboarding_completed = True
            profile.save()
            messages.info(
                request,
                "No problem -- you can join a department any time from your profile settings."
            )
            return redirect('dashboard_routing')

        dept_id = request.POST.get('department')
        try:
            dept = Department.objects.get(id=dept_id)
        except (Department.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Please choose a valid department, or skip this step.")
            return redirect('select_department')

        profile.primary_department = dept
        profile.onboarding_completed = True
        profile.save()

        DepartmentMembership.objects.get_or_create(
            user=request.user,
            department=dept,
            defaults={'role': 'viewer'}
        )

        messages.success(request, f"Welcome to {dept.name}!")
        return redirect('dashboard_routing')

    return render(request, 'account/select_department.html', {
        'departments': departments,
        'profile': profile,
    })

# ============================================================
# CROWDFUNDING: PAYMENT GATEWAY ADAPTER (Pesapal)
# ============================================================
# Everything gateway-specific lives in this section. Pesapal
# settings (PESAPAL_CONSUMER_KEY, PESAPAL_CONSUMER_SECRET,
# PESAPAL_IPN_ID, PESAPAL_BASE_URL, SITE_BASE_URL) are read from
# config/settings.py, which already loads them from .env.
#
# NOTE: PESAPAL_IPN_ID must already be a registered IPN URL ID
# (via Pesapal's /URLSetup/RegisterIPN) before payments can be
# submitted -- that's a separate one-time setup step, not done here.

PESAPAL_TOKEN_CACHE_KEY = "pesapal_auth_token"


def _get_pesapal_token():
    """
    Fetch (and briefly cache) a Pesapal bearer token.
    Tokens are short-lived (~5 min per Pesapal's docs), so we cache
    for a bit less than that to avoid hammering /Auth/RequestToken
    on every pledge while still refreshing well before expiry.
    """
    cached = cache.get(PESAPAL_TOKEN_CACHE_KEY)
    if cached:
        return cached

    response = requests.post(
        f"{settings.PESAPAL_BASE_URL}/Auth/RequestToken",
        json={
            "consumer_key": settings.PESAPAL_CONSUMER_KEY,
            "consumer_secret": settings.PESAPAL_CONSUMER_SECRET,
        },
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=15,
    )
    data = response.json()

    token = data.get("token")
    if not token:
        raise RuntimeError(f"Pesapal auth failed: {data.get('error') or data}")

    cache.set(PESAPAL_TOKEN_CACHE_KEY, token, timeout=240)  # refresh before 5 min expiry
    return token


def initiate_payment(pledge, request):
    base_url = os.environ.get("SITE_BASE_URL", settings.SITE_BASE_URL)

    tx_ref = f"tambua-{pledge.pk}-{uuid.uuid4().hex[:8]}"
    pledge.transaction_id = tx_ref
    pledge.save(update_fields=["transaction_id"])

    token = _get_pesapal_token()

    full_name = getattr(pledge.user, "get_full_name", lambda: pledge.user.username)() or pledge.user.username
    name_parts = full_name.split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    payload = {
        "id": tx_ref,
        "currency": "KES",
        "amount": float(pledge.amount),
        "description": f"Pledge for {pledge.campaign.title}"[:100],  # Pesapal caps description length
        "callback_url": f"{base_url}{reverse('campaign_pledge_confirm')}",
        "notification_id": settings.PESAPAL_IPN_ID,
        "billing_address": {
            "email_address": pledge.user.email,
            "first_name": first_name,
            "last_name": last_name,
        },
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(
        f"{settings.PESAPAL_BASE_URL}/Transactions/SubmitOrderRequest",
        json=payload,
        headers=headers,
        timeout=15,
    )
    data = response.json()

    redirect_url = data.get("redirect_url")
    if redirect_url:
        return redirect_url

    pledge.status = Pledge.STATUS_FAILED
    pledge.save(update_fields=["status"])
    return None


def verify_payment(order_tracking_id):
    """
    Looks up a Pesapal transaction by its OrderTrackingId and returns
    (is_successful, merchant_reference) so the caller can match it back
    to the right Pledge without trusting the redirect params alone.
    """
    token = _get_pesapal_token()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    response = requests.get(
        f"{settings.PESAPAL_BASE_URL}/Transactions/GetTransactionStatus",
        params={"orderTrackingId": order_tracking_id},
        headers=headers,
        timeout=15,
    )
    data = response.json()

    is_successful = data.get("payment_status_description") == "Completed"
    merchant_reference = data.get("merchant_reference")
    return is_successful, merchant_reference


# ============================================================
# CROWDFUNDING: CAMPAIGN VIEWS
# ============================================================

def campaign_list(request):
    campaigns = (
        Campaign.objects.filter(status=Campaign.STATUS_LIVE)
        .select_related("department", "creator")
        .order_by("department__name", "-created_at")
    )

    grouped = []
    for department, items in groupby(campaigns, key=attrgetter("department")):
        grouped.append({"department": department, "campaigns": list(items)})

    return render(request, "campaigns/campaign_list.html", {"grouped_campaigns": grouped})


def campaign_detail(request, slug):
    campaign = get_object_or_404(
        Campaign.objects.select_related("department", "creator").prefetch_related("rewards"),
        slug=slug,
    )
    backers = (
        Pledge.objects.filter(campaign=campaign, status=Pledge.STATUS_COMPLETED)
        .select_related("user")
        .order_by("-created_at")
    )
    pledge_form = PledgeForm(campaign=campaign)

    return render(
        request,
        "campaigns/campaign_detail.html",
        {
            "campaign": campaign,
            "rewards": campaign.rewards.all(),
            "backers": backers,
            "pledge_form": pledge_form,
        },
    )


@login_required
def campaign_create(request):
    if not getattr(request.user, "is_creator", True):
        messages.error(request, "Only creator accounts can start a campaign.")
        return redirect("campaign_list")

    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.creator = request.user
            campaign.status = Campaign.STATUS_DRAFT
            campaign.save()

            formset = RewardFormSet(request.POST, instance=campaign)
            if formset.is_valid():
                formset.save()
                messages.success(request, "Campaign created as a draft.")
                return redirect("campaign_edit", slug=campaign.slug)
        else:
            formset = RewardFormSet(request.POST)
    else:
        form = CampaignForm()
        formset = RewardFormSet()

    return render(
        request,
        "campaigns/campaign_form.html",
        {"form": form, "formset": formset, "is_edit": False},
    )


@login_required
def campaign_edit(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug, creator=request.user)

    if campaign.status not in (Campaign.STATUS_DRAFT, Campaign.STATUS_LIVE):
        messages.error(request, "This campaign can no longer be edited.")
        return redirect("campaign_detail", slug=campaign.slug)

    if request.method == "POST":
        form = CampaignForm(request.POST, instance=campaign)
        formset = RewardFormSet(request.POST, instance=campaign)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Campaign updated.")
            return redirect("campaign_detail", slug=campaign.slug)
    else:
        form = CampaignForm(instance=campaign)
        formset = RewardFormSet(instance=campaign)

    return render(
        request,
        "campaigns/campaign_form.html",
        {"form": form, "formset": formset, "is_edit": True, "campaign": campaign},
    )


@login_required
def campaign_pledge(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug)

    if not campaign.is_active:
        messages.error(request, "This campaign is not currently accepting pledges.")
        return redirect("campaign_detail", slug=campaign.slug)

    if request.method == "POST":
        form = PledgeForm(request.POST, campaign=campaign)
        if form.is_valid():
            pledge = form.save(commit=False)
            pledge.user = request.user
            pledge.campaign = campaign
            pledge.status = Pledge.STATUS_PENDING
            pledge.save()

            payment_url = initiate_payment(pledge, request)
            if payment_url:
                return redirect(payment_url)

            messages.error(request, "We couldn't start the payment. Please try again.")
    else:
        form = PledgeForm(campaign=campaign)

    return render(
        request,
        "campaigns/pledge_form.html",
        {"campaign": campaign, "form": form},
    )


@csrf_exempt
def campaign_pledge_confirm(request):
    order_tracking_id = request.GET.get("OrderTrackingId") or request.POST.get("OrderTrackingId")
    merchant_reference = request.GET.get("OrderMerchantReference") or request.POST.get("OrderMerchantReference")

    if not order_tracking_id or not merchant_reference:
        return HttpResponseBadRequest("Missing transaction reference.")

    try:
        pledge = Pledge.objects.select_related("campaign").get(transaction_id=merchant_reference)
    except Pledge.DoesNotExist:
        return HttpResponseBadRequest("Unknown transaction.")

    is_successful, verified_reference = verify_payment(order_tracking_id)

    if is_successful and verified_reference == pledge.transaction_id:
        if pledge.status != Pledge.STATUS_COMPLETED:
            pledge.status = Pledge.STATUS_COMPLETED
            pledge.save(update_fields=["status"])

            campaign = pledge.campaign
            campaign.raised_amount = campaign.raised_amount + pledge.amount
            if campaign.raised_amount >= campaign.goal_amount:
                campaign.status = Campaign.STATUS_FUNDED
            campaign.save(update_fields=["raised_amount", "status"])

        messages.success(request, "Thank you — your pledge is confirmed!")
    else:
        pledge.status = Pledge.STATUS_FAILED
        pledge.save(update_fields=["status"])
        messages.error(request, "Your payment could not be confirmed.")

    return redirect("campaign_detail", slug=pledge.campaign.slug)


@login_required
def campaign_dashboard(request):
    my_campaigns = Campaign.objects.filter(creator=request.user).order_by("-created_at")
    my_pledges = (
        Pledge.objects.filter(user=request.user)
        .select_related("campaign", "reward")
        .order_by("-created_at")
    )

    return render(
        request,
        "campaigns/campaign_dashboard.html",
        {"my_campaigns": my_campaigns, "my_pledges": my_pledges},
    )



def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def contact(request):
    if request.method == 'POST':
        ip = _client_ip(request)
        cooldown_key = f'contact_form_cooldown_{ip}'

        form = ContactForm(request.POST)

        # Simple per-IP cooldown to blunt automated/repeat spam submissions.
        # Requires Django's cache framework (works out of the box with the
        # default LocMemCache — no extra setup needed, though a shared cache
        # like Redis is recommended in production with multiple app servers).
        if cache.get(cooldown_key):
            form.add_error(None, "You're sending messages too quickly. Please wait a moment and try again.")
        elif form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.ip_address = ip
            contact_message.save()
            cache.set(cooldown_key, True, timeout=60)  # 60 second cooldown per IP

            # Redirect-after-POST so refreshing the confirmation page never
            # resubmits the form.
            return redirect(f"{reverse('contact')}?sent=1")
    else:
        form = ContactForm()

    sent = request.method == 'GET' and request.GET.get('sent') == '1'
    return render(request, 'core/contact.html', {'form': form, 'sent': sent})

def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def contact(request):
    if request.method == 'POST':
        ip = _client_ip(request)
        cooldown_key = f'contact_form_cooldown_{ip}'

        form = ContactForm(request.POST)

        # Simple per-IP cooldown to blunt automated/repeat spam submissions.
        # Requires Django's cache framework (works out of the box with the
        # default LocMemCache — no extra setup needed, though a shared cache
        # like Redis is recommended in production with multiple app servers).
        if cache.get(cooldown_key):
            form.add_error(None, "You're sending messages too quickly. Please wait a moment and try again.")
        elif form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.ip_address = ip
            contact_message.save()
            cache.set(cooldown_key, True, timeout=60)  # 60 second cooldown per IP

            # Redirect-after-POST so refreshing the confirmation page never
            # resubmits the form.
            return redirect(f"{reverse('contact')}?sent=1")
    else:
        form = ContactForm()

    sent = request.method == 'GET' and request.GET.get('sent') == '1'
    return render(request, 'core/contact.html', {'form': form, 'sent': sent})




def staff_required(view_func):
    """Like @login_required, but also requires request.user.is_staff."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


@staff_required
def admin_messages(request):
    queryset = ContactMessage.objects.all()
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'messages_list': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_count': queryset.count(),
        'unread_count': queryset.filter(is_read=False).count(),
        'segment': 'admin_messages',
    }
    return render(request, 'users/admin_messages.html', context)


@staff_required
@require_POST
def admin_message_mark_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save(update_fields=['is_read'])
    return redirect('admin_messages')

def submission_guidelines(request):
    """Render the submission guidelines page."""
    context = {
        'segment': 'guidelines',
    }
    return render(request, 'core/submission_guidelines.html', context)


def publishing_packages(request):
    """Render the publishing packages page."""
    return render(request, 'core/publishing_packages.html', {'segment': 'packages'})

def partnerships(request):
    """Render the partnerships page."""
    return render(request, 'core/partnerships.html', {'segment': 'partnerships'})