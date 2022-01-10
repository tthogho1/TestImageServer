from django.urls import path

from . import views

urlpatterns = [
    path('', views.file_upload, name='file_upload'),
    path('rekognition', views.file_upload, name='file_upload'),
    path('addFeatureVector', views.add_feature_vector, name='add_feature_vector'),
    path('compare', views.compare, name='compare'),
]