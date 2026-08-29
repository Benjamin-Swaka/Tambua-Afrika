from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Submission
from .forms import SubmissionForm

@login_required(login_url='/admin/')
def dashboard(request):
    user_submissions = Submission.objects.filter(user=request.user)
    return render(request, 'submissions/dashboard.html', {'submissions': user_submissions})

@login_required(login_url='/admin/')
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