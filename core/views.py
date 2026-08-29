from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CampaignForm, NewsletterForm, PledgeForm, RewardFormSet
from .models import Campaign, Department, Pledge, UserProfile, DepartmentMembership
from django.db.models import Q
from itertools import chain
from shop.models import Product
from comics.models import Comic
from journal.models import Article
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseRedirect
import json
from django.views.decorators.csrf import csrf_exempt
from itertools import groupby
from operator import attrgetter


def cookie_settings(request):
    if request.method == 'POST':
        analytics = request.POST.get('analytics') == 'on'
        marketing = request.POST.get('marketing') == 'on'
        consent = {
            'essential': True,
            'analytics': analytics,
            'marketing': marketing,
        }
        # Use GET 'next' or default to home
        next_url = request.GET.get('next', '/')
        response = HttpResponseRedirect(next_url)
        # Set cookie for 1 year
        response.set_cookie(
            'cookie_consent',
            json.dumps(consent),
            max_age=365 * 24 * 60 * 60,
            samesite='Lax',
        )
        return response
    else:
        return render(request, 'cookies/cookie_settings.html')

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def privacy_policy(request):
    return render(request, 'core/privacy.html')

def terms_conditions(request):
    return render(request, 'core/terms.html')

def copyright_policy(request):
    return render(request, 'core/copyright.html')

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for subscribing to our creative community!')
        else:
            messages.error(request, 'This email is already subscribed or invalid.')
    return redirect('home') # Redirects back to home (or wherever the user was)


def cookie_settings(request):
    return render(request, 'cookies/cookie_settings.html')


def team(request):
    return render(request, 'core/team.html')

def contact(request):
    return render(request, 'core/contact.html')


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



# Required environment variables :
#   FLUTTERWAVE_SECRET_KEY
#   FLUTTERWAVE_PUBLIC_KEY  (only needed if you render their inline JS widget)
#   SITE_BASE_URL           (e.g. https://tambuaafrika.com — used for redirect_url)

FLUTTERWAVE_INITIATE_URL = "https://api.flutterwave.com/v3/payments"


def initiate_payment(pledge, request):
    """
    Creates a payment session with the gateway and returns the
    URL the user should be redirected to in order to pay.

    Swap point: to switch to Stripe, replace this function's body
    with a call to stripe.checkout.Session.create(...) and return
    session.url instead. campaign_pledge() below only cares that
    this function returns a URL string.
    """
    secret_key = os.environ.get("FLUTTERWAVE_SECRET_KEY")
    base_url = os.environ.get("SITE_BASE_URL", request.build_absolute_uri("/")[:-1])

    tx_ref = f"tambua-{pledge.pk}-{uuid.uuid4().hex[:8]}"
    pledge.transaction_id = tx_ref
    pledge.save(update_fields=["transaction_id"])

    payload = {
        "tx_ref": tx_ref,
        "amount": str(pledge.amount),
        "currency": "KES",
        "redirect_url": f"{base_url}{reverse('campaign_pledge_confirm')}",
        "customer": {
            "email": pledge.user.email,
            "name": getattr(pledge.user, "get_full_name", lambda: pledge.user.username)() or pledge.user.username,
        },
        "customizations": {
            "title": f"Tambua Afrika — {pledge.campaign.title}",
            "description": f"Pledge for {pledge.campaign.title}",
        },
        "meta": {
            "pledge_id": pledge.pk,
            "campaign_id": pledge.campaign_id,
        },
    }

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(FLUTTERWAVE_INITIATE_URL, json=payload, headers=headers, timeout=15)
    data = response.json()

    if data.get("status") == "success":
        return data["data"]["link"]

    # Payment provider rejected the request — surface a generic
    # failure so campaign_pledge() can show a message and let the
    # user retry, rather than crashing.
    pledge.status = Pledge.STATUS_FAILED
    pledge.save(update_fields=["status"])
    return None


def verify_payment(transaction_id, flutterwave_transaction_id):
    """
    Confirms a transaction actually succeeded, server-side, rather
    than trusting the redirect query params alone (those can be
    spoofed by a user). Called from campaign_pledge_confirm.
    """
    secret_key = os.environ.get("FLUTTERWAVE_SECRET_KEY")
    verify_url = f"https://api.flutterwave.com/v3/transactions/{flutterwave_transaction_id}/verify"
    headers = {"Authorization": f"Bearer {secret_key}"}

    response = requests.get(verify_url, headers=headers, timeout=15)
    data = response.json()

    if data.get("status") == "success" and data["data"]["status"] == "successful":
        return data["data"]["tx_ref"] == transaction_id
    return False


# ------------------------------------------------------------
# CAMPAIGN VIEWS
# ------------------------------------------------------------

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
    # Adjust this check to match however your project marks a
    # "creator" role (e.g. request.user.profile.role == "creator").
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
    """
    Handles both the browser redirect back from the gateway AND
    (if you configure Flutterwave's dashboard to call this same
    URL) server-to-server webhook notifications. Always re-verifies
    with the provider rather than trusting query params directly.
    """
    tx_ref = request.GET.get("tx_ref") or request.POST.get("tx_ref")
    gateway_tx_id = request.GET.get("transaction_id") or request.POST.get("transaction_id")
    status = request.GET.get("status", "")

    if not tx_ref or not gateway_tx_id:
        return HttpResponseBadRequest("Missing transaction reference.")

    try:
        pledge = Pledge.objects.select_related("campaign").get(transaction_id=tx_ref)
    except Pledge.DoesNotExist:
        return HttpResponseBadRequest("Unknown transaction.")

    if status == "successful" and verify_payment(tx_ref, gateway_tx_id):
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
