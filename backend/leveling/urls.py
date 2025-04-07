from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
    path('chat/', views.chat, name='chat'),
    path('chat/stream/', views.chat_stream, name='chat_stream'),
    path('conversation/delete', views.delete_conversation, name='delete_conversation'),
] 