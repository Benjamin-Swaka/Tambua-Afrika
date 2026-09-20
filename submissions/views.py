from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Submission
from .forms import SubmissionForm
from core.models import OpenCall

def all_open_calls(request):
    open_calls = OpenCall.objects.filter(is_active=True)
    return render(request, 'submissions/open_calls.html', {'open_calls': open_calls})


def open_call_detail(request, slug):
    """
    One dedicated, reusable page per open call -- full guidelines, deadline,
    categories and status, plus the actual "Submit" call-to-action. This is
    what 'View Guidelines' now links to for any call that doesn't have its
    own external link_url configured, instead of dropping straight into the
    submissions dashboard with no context on what's actually being asked for.
    """
    call = get_object_or_404(OpenCall, slug=slug, is_active=True)
    return render(request, 'submissions/open_call_detail.html', {'call': call})


@login_required
def dashboard(request):
    user_submissions = Submission.objects.filter(user=request.user)
    return render(request, 'submissions/dashboard.html', {'submissions': user_submissions})

@login_required
def create_submission(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            return redirect('submission_dashboard')
    else:
        initial = {}
        category = request.GET.get('category')
        if category in dict(Submission.CATEGORY_CHOICES):
            initial['category'] = category
        form = SubmissionForm(initial=initial)
    
    return render(request, 'submissions/create.html', {'form': form})