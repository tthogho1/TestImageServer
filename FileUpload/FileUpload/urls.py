from django.contrib import admin
from django.urls import path
from django.urls import include
import app.views as file_upload


urlpatterns = [
    path('success/url/',file_upload.success),
    path('file_upload/',include('app.urls')),
    path('admin/', admin.site.urls),
]