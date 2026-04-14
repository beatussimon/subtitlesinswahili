from django.contrib import admin
from django.urls import path

from subtitles import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/upload/', views.upload_subtitle, name='upload-subtitle'),
    path('api/status/<int:job_id>/', views.translation_status, name='translation-status'),
    path('api/download/<int:job_id>/', views.download_translation, name='download-translation'),
]
