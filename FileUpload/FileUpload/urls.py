from django.contrib import admin
from django.urls import path
from django.urls import include
import app.views as file_upload
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('file_upload/',include('app.urls')),
    path('admin/', admin.site.urls),
]

handler404 = 'app.views.custom_error_404'
handler500 = 'app.views.custom_error_500'