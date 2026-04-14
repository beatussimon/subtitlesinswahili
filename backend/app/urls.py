from django.contrib import admin
from django.urls import path

from subtitles import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', views.register_user, name='register-user'),
    path('api/auth/login/', views.login_user, name='login-user'),
    path('api/auth/logout/', views.logout_user, name='logout-user'),
    path('api/auth/me/', views.current_user, name='current-user'),
    path('api/categories/', views.list_categories, name='list-categories'),
    path('api/subtitles/', views.list_subtitles, name='list-subtitles'),
    path('api/subtitles/<int:subtitle_id>/download/', views.download_subtitle, name='download-subtitle'),
    path('api/subtitles/<int:subtitle_id>/bookmark/', views.toggle_bookmark, name='toggle-bookmark'),
    path('api/subtitles/<int:subtitle_id>/comments/', views.list_comments, name='list-comments'),
    path('api/subtitles/<int:subtitle_id>/comments/create/', views.create_comment, name='create-comment'),
    path('api/requests/', views.list_subtitle_requests, name='list-subtitle-requests'),
    path('api/requests/create/', views.create_subtitle_request, name='create-subtitle-request'),
    path('api/upload/', views.upload_subtitle, name='upload-subtitle'),
    path('api/status/<int:job_id>/', views.translation_status, name='translation-status'),
    path('api/download/<int:job_id>/', views.download_translation, name='download-translation'),
]
