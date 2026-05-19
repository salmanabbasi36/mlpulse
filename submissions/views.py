from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Submission
from .forms import SubmissionForm


def submit_article(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            if request.user.is_authenticated:
                sub.author = request.user
                if not sub.author_name:
                    sub.author_name = request.user.get_full_name() or request.user.username
                if not sub.author_email:
                    sub.author_email = request.user.email
            sub.save()
            messages.success(request, 'Your article has been submitted! We will review it and get back to you.')
            return redirect('blog:home')
    else:
        form = SubmissionForm()
        if request.user.is_authenticated:
            form.initial = {
                'author_name': request.user.get_full_name() or request.user.username,
                'author_email': request.user.email,
                'author_bio': request.user.bio,
            }
    return render(request, 'submissions/submit.html', {'form': form})
