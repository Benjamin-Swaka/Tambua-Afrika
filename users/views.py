from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import UserUpdateForm, ProfileUpdateForm
from submissions.models import Submission   # Ensure this app exists
from core.models import UserProfile


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


@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')

    recent_submissions = Submission.objects.all().order_by('-created_at')[:10]
    total_users = User.objects.count()
    pending_reviews = Submission.objects.filter(status='review').count()

    context = {
        'submissions': recent_submissions,
        'total_users': total_users,
        'pending_reviews': pending_reviews,
        'segment': 'admin_overview',
    }
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