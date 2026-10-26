from django.urls import path
from .views import TodoDetailView, TodoListCreateView

urlpatterns = [
    path('todo/', TodoListCreateView.as_view(), name='todo_list'),
    path('todo/<int:pk>/', TodoDetailView.as_view(), name='todo-detail'),
]