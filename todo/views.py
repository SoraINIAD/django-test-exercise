from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


def index(request):
    if request.method == 'POST':
        due_at_text = request.POST.get('due_at', '')
        due_at = None

        if due_at_text:
            parsed_due_at = parse_datetime(due_at_text)
            if parsed_due_at:
                due_at = make_aware(parsed_due_at)

        task = Task(
            title=request.POST['title'],
            due_at=due_at,
        )
        task.save()

    title_query = request.GET.get('q', '').strip()
    show_completed = request.GET.get('show_completed', 'all')
    order = request.GET.get('order', 'post')

    tasks = Task.objects.all()

    if title_query:
        tasks = tasks.filter(title__icontains=title_query)

    if show_completed == 'completed':
        tasks = tasks.filter(completed=True)
    elif show_completed == 'pending':
        tasks = tasks.filter(completed=False)

    if order == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')

    context = {
        'tasks': tasks,
        'title_query': title_query,
        'show_completed': show_completed,
        'order': order,
    }

    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }
    return render(request, "todo/edit.html", context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)
