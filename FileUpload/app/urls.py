from django.urls import path

from . import views

urlpatterns = [
    path('', views.file_upload, name='file_upload'),
    path('rekognition', views.file_upload, name='file_upload'),
    path('getSimilarImage', views.get_similar_image, name='get_similar_image'),
    path('cacheFeatureVector', views.cache_feature_vector, name='cache_feature_vector'),
    path('compare', views.compare, name='compare'),
    path('download/<F>', views.file_download, name='file_download'),
]
