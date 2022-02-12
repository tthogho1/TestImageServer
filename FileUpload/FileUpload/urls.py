from django.contrib import admin
from django.urls import path
from django.urls import include
import app.views as file_upload


urlpatterns = [
    path('file_upload/',include('app.urls')),
    path('admin/', admin.site.urls),
]

handler404 = 'app.views.custom_error_404'