from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.home, name='home'),
    path('chat-api/', views.chat_api, name='chat_api'),
    path('tts/', views.elevenlabs_tts, name='elevenlabs_tts'),
    path('api/conversations/', views.get_conversations, name='get_conversations'),
    path('api/conversations/<int:conversation_id>/', views.load_conversation, name='load_conversation'),
    path('api/conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    path('journal/', views.journal_view, name='journal'),
    path('api/journal/', views.save_journal_entry, name='save_journal_entry'),
]
