from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Submission
from .forms import SubmissionForm
from core.models import OpenCall

def all_open_calls(request):
    open_calls = OpenCall.objects.filter(is_active=True)
    return render(request, 'submissions/open_calls.html', {'open_calls': open_calls})

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
        form = SubmissionForm()
    
    return render(request, 'submissions/create.html', {'form': form})