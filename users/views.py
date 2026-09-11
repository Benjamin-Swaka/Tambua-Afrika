from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db import transaction
from functools import wraps
import json

from .forms import UserUpdateForm, ProfileUpdateForm
from submissions.models import Submission   # Ensure this app exists
from core.models import (
    UserProfile, ConsentLog, FeaturedWork, OpenCall, ShopHighlight,
    Department, DepartmentMembership,
)
from core.permissions import (
    can_access_section,
    is_full_admin,
    is_department_admin,
    get_admin_department_slugs,
    allowed_submission_categories,
    admin_department_queryset,
)


def staff_required(view_func):
    """
    Gate for the custom admin dashboard. Only staff (or superuser)
    accounts get in -- everyone else is bounced back to their own
    dashboard rather than seeing a raw 403 or being sent through
    Django's built-in admin login.

    This only checks "is this a staff account at all" -- it does NOT
    know about department scoping. Views that belong to a specific
    department section use @admin_section_required(...) below instead,
    which layers department scoping on top of this same check. Views
    decorated with @staff_required alone (site-wide sections such as
    Users, Homepage Content, etc.) remain full-admin-only by virtue of
    not being reachable by department admins from the sidebar/URLs
    those roles are scoped to -- see admin_section_required.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "You don't have access to the admin dashboard.")
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def admin_section_required(section):
    """
    Gate for a specific custom-admin section (e.g. 'admin_products',
    'admin_tickets'). Stacks on top of the same authentication/staff
    check as @staff_required, then additionally checks whether this
    user's admin access is scoped to a department -- and if so, whether
    `section` belongs to one of their assigned departments.

    - Superusers and legacy/unscoped staff ("full admins"): always let
      through, unchanged from current behaviour.
    - Department admins: only let through for sections that belong to
      one of their assigned departments; otherwise redirected back to
      their own dashboard with an explanatory message.
    """
    def decorator(view_func):
        @wraps(view_func)
        @staff_required
        def _wrapped(request, *args, **kwargs):
            if not can_access_section(request.user, section):
                messages.error(
                    request,
                    "You don't have access to that department's admin area."
                )
                return redirect('staff_dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def full_admin_required(view_func):
    """
    Gate for site-wide sections that are never department-scoped
    (Users, Homepage Content, etc.). Superusers and legacy/unscoped
    staff pass; department admins are redirected to their dashboard.
    """
    @wraps(view_func)
    @staff_required
    def _wrapped(request, *args, **kwargs):
        if not is_full_admin(request.user):
            messages.error(
                request,
                "This area is only available to site-wide admins."
            )
            return redirect('staff_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
def dashboard_routing(request):
    """Redirect user to appropriate dashboard."""
    if request.user.is_superuser or request.user.is_staff:
        return redirect('staff_dashboard')

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.onboarding_completed:
        return redirect('select_department')

    return redirect('user_dashboard')


@login_required
def user_dashboard(request):
    my_submissions = Submission.objects.filter(user=request.user).order_by('-created_at')
    active_count = my_submissions.filter(status='review').count()
    accepted_count = my_submissions.filter(status='accepted').count()

    context = {
        'submissions': my_submissions[:5],
        'active_count': active_count,
        'accepted_count': accepted_count,
        'segment': 'overview',
    }
    return render(request, 'users/user_dashboard.html', context)


@staff_required
def staff_dashboard(request):
    """
    A superuser or legacy/unscoped staff account gets the full,
    site-wide overview exactly as before.

    A department admin gets a narrower version of the same page,
    built only from the department(s) they're assigned to -- they
    never see numbers or shortcuts for departments they don't manage.
    """
    full_admin = is_full_admin(request.user)
    dept_slugs = get_admin_department_slugs(request.user)

    context = {
        'segment': 'admin_overview',
        'is_full_admin': full_admin,
        'is_department_admin': not full_admin,
        'admin_department_slugs': dept_slugs,
    }

    show_stage = full_admin or 'stage' in dept_slugs
    show_shop = full_admin or 'shop' in dept_slugs
    show_submissions = full_admin or bool(allowed_submission_categories(request.user))

    if show_submissions:
        sub_qs = Submission.objects.all().order_by('-created_at')
        allowed_categories = allowed_submission_categories(request.user)
        if allowed_categories is not None:
            sub_qs = sub_qs.filter(category__in=allowed_categories)
        context['submissions'] = sub_qs[:8]
        context['pending_reviews'] = sub_qs.filter(status='review').count()

    if show_stage:
        from stage.models import Ticket, Show, ManualPayment

        paid_tickets = Ticket.objects.filter(status=Ticket.STATUS_PAID)
        context['ticket_revenue'] = paid_tickets.aggregate(total=Sum('total_amount'))['total'] or 0
        context['tickets_sold'] = paid_tickets.aggregate(qty=Sum('quantity'))['qty'] or 0
        context['pending_manual_payments'] = ManualPayment.objects.filter(
            status=ManualPayment.STATUS_PENDING,
            transaction_code__isnull=False,
        ).count()
        context['upcoming_shows'] = Show.objects.filter(
            is_active=True, date__gte=timezone.localdate()
        ).count()
        context['recent_tickets'] = paid_tickets.select_related('show', 'user').order_by('-paid_at')[:6]

    if show_shop:
        from shop.models import Product
        context['total_products'] = Product.objects.count()

    if full_admin:
        context['total_users'] = User.objects.count()

    return render(request, 'users/staff_dashboard.html', context)


@login_required
def profile_settings(request):
    # Ensure profile exists (it should, thanks to signals)
    profile = request.user.users_profile

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile_settings')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'segment': 'settings',
    }
    return render(request, 'users/profile.html', context)


# ==============================================
# GDPR: PRIVACY & DATA (self-service data subject rights)
# ==============================================

@login_required
def privacy_center(request):
    """
    Lets a user see their consent history and exercise their GDPR
    rights: download a copy of their data, or permanently delete
    their account.
    """
    consent_history = ConsentLog.objects.filter(user=request.user)[:10]
    context = {
        'consent_history': consent_history,
        'segment': 'privacy',
    }
    return render(request, 'users/privacy_center.html', context)


@login_required
def export_my_data(request):
    """
    Right to data portability (GDPR Art. 20): a downloadable JSON copy
    of everything we hold that's tied to this user.
    """
    user = request.user
    profile = getattr(user, 'users_profile', None)
    core_profile = getattr(user, 'core_profile', None)

    submissions = Submission.objects.filter(user=user).values(
        'title', 'category', 'status', 'created_at'
    )

    tickets = []
    try:
        from stage.models import Ticket
        tickets = list(
            Ticket.objects.filter(user=user).values(
                'ticket_code', 'show__title', 'quantity', 'total_amount',
                'status', 'created_at'
            )
        )
    except Exception:
        pass

    data = {
        'exported_at': timezone.now().isoformat(),
        'account': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'is_staff': user.is_staff,
        },
        'profile': {
            'bio': profile.bio if profile else None,
            'location': profile.location if profile else None,
            'role': profile.role if profile else None,
        } if profile else None,
        'department': {
            'primary_department': (
                core_profile.primary_department.name
                if core_profile and core_profile.primary_department else None
            ),
        } if core_profile else None,
        'submissions': list(submissions),
        'tickets': tickets,
        'consent_history': list(
            ConsentLog.objects.filter(user=user).values(
                'analytics', 'marketing', 'created_at'
            )
        ),
    }

    response = JsonResponse(data, json_dumps_params={'indent': 2, 'default': str})
    response['Content-Disposition'] = f'attachment; filename="tambua-afrika-data-{user.username}.json"'
    return response


@login_required
def delete_my_account(request):
    """
    Right to erasure (GDPR Art. 17). Requires re-entering the password
    as a confirmation step so an account can't be deleted by mistake or
    by someone who's grabbed a logged-in session.
    """
    if request.method == 'POST':
        password = request.POST.get('password', '')
        if not request.user.check_password(password):
            messages.error(request, "That password wasn't correct. Your account was not deleted.")
            return redirect('privacy_center')

        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account and associated data have been permanently deleted.")
        return redirect('home')

    return redirect('privacy_center')


# ==============================================
# CUSTOM ADMIN DASHBOARD (staff-only, separate from /admin/)
# ==============================================

@admin_section_required('admin_submissions')
def admin_submissions(request):
    """
    Submissions moderation: filter, review, accept/reject.

    Site-wide for full admins. A department admin only ever sees (and
    can only filter/act on) submissions in categories that belong to
    their assigned department(s) -- e.g. an Ink admin only sees
    manuscripts, never scripts, auditions, or comics.
    """
    qs = Submission.objects.select_related('user').order_by('-created_at')

    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    search = request.GET.get('q', '')

    allowed_categories = allowed_submission_categories(request.user)
    category_choices = Submission.CATEGORY_CHOICES
    if allowed_categories is not None:
        qs = qs.filter(category__in=allowed_categories)
        category_choices = [
            (value, label) for value, label in Submission.CATEGORY_CHOICES
            if value in allowed_categories
        ]
        # A department admin can't use ?category= to peek at a category
        # outside their department, even by hand-editing the URL.
        if category and category not in allowed_categories:
            category = ''

    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(user__email__icontains=search))

    context = {
        'submissions': qs[:200],
        'status_choices': Submission.STATUS_CHOICES,
        'category_choices': category_choices,
        'current_status': status,
        'current_category': category,
        'search': search,
        'segment': 'admin_submissions',
    }
    return render(request, 'users/admin_submissions.html', context)


@admin_section_required('admin_submissions')
def admin_submission_update_status(request, pk):
    """Approve / reject / re-review a single submission."""
    submission = get_object_or_404(Submission, pk=pk)

    allowed_categories = allowed_submission_categories(request.user)
    if allowed_categories is not None and submission.category not in allowed_categories:
        messages.error(request, "You don't have access to that submission's department.")
        return redirect('admin_submissions')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = dict(Submission.STATUS_CHOICES)
        if new_status in valid_statuses:
            submission.status = new_status
            submission.save()
            messages.success(request, f'"{submission.title}" marked as {valid_statuses[new_status]}.')
        else:
            messages.error(request, "Invalid status.")
    return redirect('admin_submissions')


@admin_section_required('admin_tickets')
def admin_tickets(request):
    """Site-wide ticket sales overview: filter by show/status, mark paid/cancelled."""
    from stage.models import Ticket, Show

    qs = Ticket.objects.select_related('show', 'user').order_by('-created_at')

    status = request.GET.get('status', '')
    show_id = request.GET.get('show', '')

    if status:
        qs = qs.filter(status=status)
    if show_id:
        qs = qs.filter(show_id=show_id)

    total_revenue = qs.filter(status=Ticket.STATUS_PAID).aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'tickets': qs[:200],
        'shows': Show.objects.all().order_by('-date'),
        'status_choices': Ticket.STATUS_CHOICES,
        'current_status': status,
        'current_show': show_id,
        'total_revenue': total_revenue,
        'segment': 'admin_tickets',
    }
    return render(request, 'users/admin_tickets.html', context)


@admin_section_required('admin_tickets')
def admin_ticket_update_status(request, ticket_code):
    from stage.models import Ticket

    ticket = get_object_or_404(Ticket, ticket_code=ticket_code)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel' and ticket.status != Ticket.STATUS_PAID:
            ticket.status = Ticket.STATUS_CANCELLED
            ticket.save(update_fields=['status'])
            messages.info(request, f"Ticket {ticket.ticket_code} cancelled.")
        elif action == 'cancel':
            messages.warning(request, "A paid ticket cannot be cancelled from this action.")
    return redirect('admin_tickets')


@admin_section_required('admin_products')
def admin_products(request):
    """Shop overview (full admins see it site-wide; Shop department admins too, since Shop is a single department)."""
    from shop.models import Product

    qs = Product.objects.all().order_by('-created_at')
    category = request.GET.get('category', '')
    if category:
        qs = qs.filter(category=category)

    context = {
        'products': qs,
        'category_choices': Product.CATEGORY_CHOICES,
        'current_category': category,
        'segment': 'admin_products',
    }
    return render(request, 'users/admin_products.html', context)


@admin_section_required('admin_products')
def admin_product_delete(request, pk):
    from shop.models import Product

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" was removed from the shop.')
    return redirect('admin_products')


@full_admin_required
def admin_users(request):
    """Site-wide user management: promote/demote staff, deactivate accounts,
    and assign/revoke department-admin access. Full admins only -- a
    department admin never gets to see or edit the full user list."""
    qs = User.objects.all().order_by('-date_joined')
    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(Q(email__icontains=search) | Q(username__icontains=search))

    users = list(qs[:300])

    # Attach each user's current department-admin assignments so the
    # template can pre-check the right boxes without extra queries per row.
    memberships = DepartmentMembership.objects.filter(
        user__in=users, role='admin'
    ).values_list('user_id', 'department_id')
    dept_admin_map = {}
    for user_id, department_id in memberships:
        dept_admin_map.setdefault(user_id, set()).add(department_id)
    for u in users:
        u.admin_department_ids = dept_admin_map.get(u.pk, set())

    context = {
        'users': users,
        'search': search,
        'departments': admin_department_queryset(),
        'segment': 'admin_users',
    }
    return render(request, 'users/admin_users.html', context)


@full_admin_required
def admin_user_toggle_staff(request, pk):
    """Grant/revoke access to this admin dashboard. Superuser-only, and
    a staff member can never demote themselves by accident here."""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can change staff access.")

    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, "You can't change your own staff access.")
        return redirect('admin_users')

    if request.method == 'POST':
        target.is_staff = not target.is_staff
        target.save()
        state = "granted" if target.is_staff else "revoked"
        messages.success(request, f"Admin dashboard access {state} for {target.email}.")
    return redirect('admin_users')


@full_admin_required
def admin_user_departments_update(request, pk):
    """
    Assign or revoke department-admin access for a user, directly from
    the custom admin dashboard -- no need to go into the Django admin.

    Superuser-only, same rule as the staff toggle above: department
    assignment grants dashboard-level power, so only the main admin
    hands it out. Submitting the form replaces the user's full set of
    department-admin assignments with whichever departments were
    checked (unchecking a department revokes admin rights to it).
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers can assign department admins.")

    target = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if target.is_superuser:
            messages.error(request, "Superusers already have full access and can't be department-scoped.")
            return redirect('admin_users')

        selected_ids = {
            int(v) for v in request.POST.getlist('departments') if v.isdigit()
        }
        valid_departments = {d.pk: d for d in admin_department_queryset()}
        selected_ids &= set(valid_departments.keys())

        current_admin_ids = set(
            DepartmentMembership.objects.filter(
                user=target, role='admin'
            ).values_list('department_id', flat=True)
        )

        to_add = selected_ids - current_admin_ids
        to_remove = current_admin_ids - selected_ids

        with transaction.atomic():
            for dept_id in to_add:
                membership, _ = DepartmentMembership.objects.get_or_create(
                    user=target, department_id=dept_id,
                    defaults={'role': 'admin'},
                )
                if membership.role != 'admin':
                    membership.role = 'admin'
                    membership.save(update_fields=['role'])

            if to_remove:
                # Demote back to 'viewer' rather than deleting the row,
                # so the user doesn't lose their general department
                # membership -- only the admin privilege for it.
                DepartmentMembership.objects.filter(
                    user=target, department_id__in=to_remove, role='admin'
                ).update(role='viewer')

            if selected_ids and not target.is_staff:
                # A department admin needs dashboard access to use it.
                target.is_staff = True
                target.save(update_fields=['is_staff'])

        dept_names = sorted(valid_departments[i].name for i in selected_ids)
        if dept_names:
            messages.success(
                request,
                f"{target.email} is now a department admin for: {', '.join(dept_names)}."
            )
        else:
            messages.success(request, f"Removed all department-admin assignments for {target.email}.")

    return redirect('admin_users')


@full_admin_required
def admin_user_toggle_active(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, "You can't deactivate your own account.")
        return redirect('admin_users')

    if request.method == 'POST':
        target.is_active = not target.is_active
        target.save()
        state = "reactivated" if target.is_active else "deactivated"
        messages.success(request, f"{target.email} was {state}.")
    return redirect('admin_users')


# ==============================================
# CUSTOM ADMIN: SHOWS (create/edit tickets' Shows without Django admin)
# ==============================================

@admin_section_required('admin_shows')
def admin_shows(request):
    from stage.models import Show

    shows = Show.objects.all().order_by('-date')
    context = {
        'shows': shows,
        'segment': 'admin_shows',
    }
    return render(request, 'users/admin_shows.html', context)


@admin_section_required('admin_shows')
def admin_show_create(request):
    from stage.forms import ShowForm

    if request.method == 'POST':
        form = ShowForm(request.POST, request.FILES)
        if form.is_valid():
            show = form.save()
            messages.success(request, f'"{show.title}" was created.')
            return redirect('admin_shows')
    else:
        form = ShowForm()

    return render(request, 'users/admin_show_form.html', {
        'form': form,
        'segment': 'admin_shows',
        'is_edit': False,
    })


@admin_section_required('admin_shows')
def admin_show_edit(request, pk):
    from stage.models import Show
    from stage.forms import ShowForm

    show = get_object_or_404(Show, pk=pk)
    if request.method == 'POST':
        form = ShowForm(request.POST, request.FILES, instance=show)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{show.title}" was updated.')
            return redirect('admin_shows')
    else:
        form = ShowForm(instance=show)

    return render(request, 'users/admin_show_form.html', {
        'form': form,
        'segment': 'admin_shows',
        'is_edit': True,
        'show': show,
    })


@admin_section_required('admin_shows')
def admin_show_delete(request, pk):
    from stage.models import Show

    show = get_object_or_404(Show, pk=pk)
    if request.method == 'POST':
        title = show.title
        show.delete()
        messages.success(request, f'"{title}" was deleted.')
    return redirect('admin_shows')


@admin_section_required('admin_shows')
def admin_show_toggle_active(request, pk):
    from stage.models import Show

    show = get_object_or_404(Show, pk=pk)
    if request.method == 'POST':
        show.is_active = not show.is_active
        show.save()
    return redirect('admin_shows')


# ==============================================
# CUSTOM ADMIN: HOMEPAGE CONTENT
# (Featured Works / Open Calls / Shop Highlights — add, remove, replace)
# ==============================================

@full_admin_required
def admin_homepage_content(request):
    context = {
        'featured_works': FeaturedWork.objects.all(),
        'open_calls': OpenCall.objects.all(),
        'shop_highlights': ShopHighlight.objects.all(),
        'segment': 'admin_homepage',
    }
    return render(request, 'users/admin_homepage_content.html', context)


@full_admin_required
def admin_featured_work_form(request, pk=None):
    from core.forms import FeaturedWorkForm
    instance = get_object_or_404(FeaturedWork, pk=pk) if pk else None
    if request.method == 'POST':
        form = FeaturedWorkForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Featured work saved.")
            return redirect('admin_homepage_content')
    else:
        form = FeaturedWorkForm(instance=instance)
    return render(request, 'users/admin_content_form.html', {
        'form': form, 'segment': 'admin_homepage', 'is_edit': bool(pk),
        'title': 'Featured Work', 'cancel_url': 'admin_homepage_content',
    })


@full_admin_required
def admin_featured_work_delete(request, pk):
    obj = get_object_or_404(FeaturedWork, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Featured work removed.")
    return redirect('admin_homepage_content')


@full_admin_required
def admin_open_call_form(request, pk=None):
    from core.forms import OpenCallForm
    instance = get_object_or_404(OpenCall, pk=pk) if pk else None
    if request.method == 'POST':
        form = OpenCallForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Open call saved.")
            return redirect('admin_homepage_content')
    else:
        form = OpenCallForm(instance=instance)
    return render(request, 'users/admin_content_form.html', {
        'form': form, 'segment': 'admin_homepage', 'is_edit': bool(pk),
        'title': 'Open Call', 'cancel_url': 'admin_homepage_content',
    })


@full_admin_required
def admin_open_call_delete(request, pk):
    obj = get_object_or_404(OpenCall, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Open call removed.")
    return redirect('admin_homepage_content')


@full_admin_required
def admin_shop_highlight_form(request, pk=None):
    from core.forms import ShopHighlightForm
    instance = get_object_or_404(ShopHighlight, pk=pk) if pk else None
    if request.method == 'POST':
        form = ShopHighlightForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop highlight saved.")
            return redirect('admin_homepage_content')
    else:
        form = ShopHighlightForm(instance=instance)
    return render(request, 'users/admin_content_form.html', {
        'form': form, 'segment': 'admin_homepage', 'is_edit': bool(pk),
        'title': 'Shop Highlight', 'cancel_url': 'admin_homepage_content',
    })


@full_admin_required
def admin_shop_highlight_delete(request, pk):
    obj = get_object_or_404(ShopHighlight, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Shop highlight removed.")
    return redirect('admin_homepage_content')


# ==============================================
# CUSTOM ADMIN: MANUAL M-PESA PAYMENT VERIFICATION
# ==============================================

@admin_section_required('admin_manual_payments')
def admin_manual_payments(request):
    """List manual payments submitted by customers."""
    from stage.models import ManualPayment

    status = request.GET.get('status', ManualPayment.STATUS_PENDING)
    search = request.GET.get('q', '').strip()

    qs = ManualPayment.objects.select_related(
        'ticket__show',
        'ticket__user',
        'verified_by',
    )

    if status in dict(ManualPayment.STATUS_CHOICES):
        qs = qs.filter(status=status)
    else:
        status = ''

    if search:
        qs = qs.filter(
            Q(payment_reference__icontains=search) |
            Q(transaction_code__icontains=search) |
            Q(ticket__ticket_code__icontains=search) |
            Q(ticket__user__email__icontains=search) |
            Q(ticket__user__username__icontains=search)
        )

    context = {
        'payments': qs.order_by('-created_at')[:300],
        'status_choices': ManualPayment.STATUS_CHOICES,
        'current_status': status,
        'search': search,
        'pending_count': ManualPayment.objects.filter(
            status=ManualPayment.STATUS_PENDING
        ).count(),
        'segment': 'admin_manual_payments',
    }
    return render(request, 'users/admin_manual_payments.html', context)


@admin_section_required('admin_manual_payments')
def admin_manual_payment_review(request, payment_reference):
    """Review and verify/reject one manual payment."""
    from stage.models import ManualPayment, Ticket

    payment = get_object_or_404(
        ManualPayment.objects.select_related(
            'ticket__show',
            'ticket__user',
            'verified_by',
        ),
        payment_reference=payment_reference,
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if payment.status != ManualPayment.STATUS_PENDING:
            messages.warning(
                request,
                f"This payment is already {payment.get_status_display().lower()}."
            )
            return redirect(
                'admin_manual_payment_review',
                payment_reference=payment.payment_reference,
            )

        if action == 'verify':
            with transaction.atomic():
                payment = ManualPayment.objects.select_for_update().select_related(
                    'ticket'
                ).get(pk=payment.pk)
                ticket = Ticket.objects.select_for_update().get(pk=payment.ticket_id)

                if payment.status != ManualPayment.STATUS_PENDING:
                    messages.warning(request, "This payment has already been processed.")
                elif not payment.transaction_code:
                    messages.error(request, "Cannot verify a payment without an M-Pesa transaction code.")
                elif payment.amount != ticket.total_amount:
                    messages.error(
                        request,
                        "Payment amount does not match the ticket amount. Do not verify it until resolved."
                    )
                elif ticket.status == Ticket.STATUS_CANCELLED:
                    messages.error(request, "This reservation is cancelled. Do not verify the payment.")
                elif ticket.status == Ticket.STATUS_PAID:
                    payment.status = ManualPayment.STATUS_VERIFIED
                    payment.verified_at = timezone.now()
                    payment.verified_by = request.user
                    payment.save(update_fields=[
                        'status', 'verified_at', 'verified_by', 'updated_at'
                    ])
                    messages.warning(
                        request,
                        "The ticket was already paid. The manual payment has been recorded as verified."
                    )
                else:
                    # This is the only path that converts the reservation
                    # into a paid/valid ticket.
                    ticket.mark_as_paid(reference=payment.transaction_code)

                    payment.status = ManualPayment.STATUS_VERIFIED
                    payment.verified_at = timezone.now()
                    payment.verified_by = request.user
                    payment.rejection_reason = ''
                    payment.save(update_fields=[
                        'status',
                        'verified_at',
                        'verified_by',
                        'rejection_reason',
                        'updated_at',
                    ])

                    messages.success(
                        request,
                        f"Payment {payment.payment_reference} verified. "
                        f"Ticket {ticket.ticket_code} is now confirmed."
                    )

            return redirect(
                'admin_manual_payment_review',
                payment_reference=payment.payment_reference,
            )

        if action == 'reject':
            reason = request.POST.get('rejection_reason', '').strip()
            if not reason:
                messages.error(request, "Provide a reason before rejecting the payment.")
            else:
                payment.status = ManualPayment.STATUS_REJECTED
                payment.rejection_reason = reason
                payment.verified_at = timezone.now()
                payment.verified_by = request.user
                payment.save(update_fields=[
                    'status',
                    'rejection_reason',
                    'verified_at',
                    'verified_by',
                    'updated_at',
                ])
                messages.success(
                    request,
                    f"Payment {payment.payment_reference} rejected."
                )
                return redirect('admin_manual_payments')

    return render(
        request,
        'users/admin_manual_payment_review.html',
        {
            'payment': payment,
            'segment': 'admin_manual_payments',
        },
    )


# ==============================================
# CUSTOM ADMIN: TICKET DOOR VERIFICATION / CHECK-IN
# ==============================================

@admin_section_required('admin_tickets')
def admin_ticket_verify(request, ticket_code=None):
    """
    Two ways in:
      - Scanning a ticket's QR code opens this page directly at
        /admin-panel/tickets/verify/<ticket_code>/ (staff_required
        still gates it -- the QR alone isn't enough to check someone
        in, whoever opens it has to already be logged in as staff).
      - Typing a code by hand into the search box on this same page
        (in case a phone camera isn't handy).
    """
    from stage.models import Ticket

    ticket = None
    code = (ticket_code or request.POST.get('ticket_code', '') or request.GET.get('ticket_code', '')).strip().upper()

    if code:
        try:
            ticket = Ticket.objects.select_related('show', 'user', 'checked_in_by').get(ticket_code=code)
        except Ticket.DoesNotExist:
            messages.error(request, f"No ticket found with code {code}.")

    if request.method == 'POST' and request.POST.get('action') == 'checkin' and ticket:
        if ticket.status != Ticket.STATUS_PAID:
            messages.error(request, "This ticket hasn't been paid for — cannot check in.")
        elif ticket.checked_in:
            messages.warning(
                request,
                f"Already checked in at {ticket.checked_in_at:%H:%M on %d %b} "
                f"by {ticket.checked_in_by or 'a staff member'}."
            )
        else:
            ticket.checked_in = True
            ticket.checked_in_at = timezone.now()
            ticket.checked_in_by = request.user
            ticket.save(update_fields=['checked_in', 'checked_in_at', 'checked_in_by'])
            buyer_name = ticket.user.get_full_name() or ticket.user.username
            messages.success(request, f"{buyer_name} checked in for {ticket.show.title}.")
        return redirect('admin_ticket_verify_code', ticket_code=ticket.ticket_code)

    return render(request, 'users/admin_ticket_verify.html', {
        'ticket': ticket,
        'searched_code': code,
        'segment': 'admin_tickets',
    })