from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages

from .models import Poll, Choice
from .forms import VoteForm

def index(request):
    """
    Render a list of available polls.

    This view retrieves all available polls from the database and renders
    the 'index.html' template, displaying the list of polls.

    :param request: HTTP request object
    :return: Rendered HTML template with poll list
    """
    latest_polls = Poll.objects.order_by('-pub_date')[:5]
    context = {'latest_polls': latest_polls}
    return render(request, 'index.html', context)

def detail(request, poll_id):
    """
    Render the details of a specific poll.

    This view retrieves a specific poll from the database using its ID and
    renders the 'detail.html' template. It also handles voting using
    a form and displays real-time poll results using AJAX polling.

    :param request: HTTP request object
    :param poll_id: ID of the poll to display
    :return: Rendered HTML template with poll details and real-time results
    """
    poll = get_object_or_404(Poll, pk=poll_id)
    total_votes = poll.choice_set.aggregate(Sum('votes'))['votes__sum']
    
    if request.method == 'POST':
        form = VoteForm(poll_id, request.POST)
        if form.is_valid():
            choice_id = form.cleaned_data['choice']
            choice = get_object_or_404(Choice, pk=choice_id)
            choice.votes += 1
            choice.save()
            messages.success(request, "Thank you for voting!")
            return redirect('polling:detail', poll_id=poll_id)
    else:
        form = VoteForm(poll_id)

    return render(request, 'detail.html', {'poll': poll, 'total_votes': total_votes, 'form': form})


def vote(request, poll_id):
    # poll = get_object_or_404(Poll, pk=poll_id)
    # try:
    #     selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    # except (KeyError, Choice.DoesNotExist):
    #     return render(request, 'detail.html', {
    #         'poll': poll,
    #         'error_message': "You didn't select a choice.",
    #     })
    # else:
    #     selected_choice.votes += 1
    #     selected_choice.save()
    #     return JsonResponse({'votes': selected_choice.votes})
    """
    Handle user voting for a specific poll choice.

    This view handles user voting for a specific poll choice. It receives a POST
    request with the selected choice ID, updates the choice's vote count, and
    redirects back to the poll detail page.

    :param request: HTTP request object (POST)
    :param poll_id: ID of the poll for which user is voting
    :return: Redirect to poll detail page
    """
    poll = get_object_or_404(Poll, pk=poll_id)
    total_votes = poll.choice_set.aggregate(Sum('votes'))['votes__sum']

    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            choice_id = form.cleaned_data['choice']
            choice = get_object_or_404(Choice, pk=choice_id)
            choice.votes += 1
            choice.save()
            return redirect('polling:detail', poll_id=poll_id)

    # If the form is not valid or not a POST request, redirect back to poll detail
    return redirect('polling:detail', poll_id=poll_id)

def poll_results_api(request, poll_id):
    """
    Fetch real-time poll results as JSON.

    This view fetches the real-time poll results for a specific poll and
    returns the results in JSON format, which can be used for AJAX polling.

    :param request: HTTP request object
    :param poll_id: ID of the poll for which results are fetched
    :return: JSON response containing poll results
    """
    poll = get_object_or_404(Poll, pk=poll_id)
    total_votes = poll.choice_set.aggregate(Sum('votes'))['votes__sum']
    results = [{'choice_text': choice.choice_text, 'votes': choice.votes} for choice in poll.choice_set.all()]
    return JsonResponse({'results': results, 'total_votes': total_votes})