from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .serializers import TodoSerializer
from .models import Todo

class TodoListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        qs = Todo.objects.all().order_by('-created_at')
        serializer = TodoSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodoDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, *args, **kwargs):
        todo = get_object_or_404(Todo, pk=pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        todo = get_object_or_404(Todo, pk=pk)
        serializer = TodoSerializer(todo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        todo = get_object_or_404(Todo, pk=pk)
        serializer = TodoSerializer(todo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        todo = get_object_or_404(Todo, pk=pk)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            if title:
                Todo.objects.create(
                    user=request.user,
                    title=title,
                    description=description,
                )
                messages.success(request, 'Todo added!')

        elif action == 'toggle':
            todo_id = request.POST.get('todo_id')
            todo = Todo.objects.filter(id=todo_id, user=request.user).first()
            if todo:
                todo.completed = not todo.completed
                todo.save()

        elif action == 'delete':
            todo_id = request.POST.get('todo_id')
            Todo.objects.filter(id=todo_id, user=request.user).delete()
            messages.success(request, 'Todo deleted.')

        return redirect('dashboard')

    todos = Todo.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'todos': todos})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserCreationForm()

    return render(request, 'todos/register.html', {'form': form})