from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import TodoForm
from .models import TodoModel


# Create your views here.
def home(request):
    return render(request, 'todo/home.html')


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(),
                               'error': 'That name has already been taken. Please choose a new username'})

        else:
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Password did not match '})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Username an password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError as _ex:
            return render(request, 'todo/createtodos.html',
                          {'form': TodoForm(), 'error': 'Bad data passed. \n Try again'})

@login_required
def current_todo(request):
    todos = TodoModel.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos': todos})

@login_required
def completed_todos(request):
    todos = TodoModel.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo/completedtodos.html', {'todos': todos})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(TodoModel, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            form = TodoForm(instance=todo)
            return render(request, 'todo/viewtodo.html',
                          {'todo': todo, 'form': form, 'error': 'Bad data passed. \n Try again'})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(TodoModel, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('currenttodos')



@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(TodoModel, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')

