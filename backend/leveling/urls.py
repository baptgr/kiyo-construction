from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
    path('chat/stream/', views.chat_stream, name='chat_stream'),
] 