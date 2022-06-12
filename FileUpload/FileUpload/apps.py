from django.apps import AppConfig


class FileUploadConfig(AppConfig):
    name = 'FileUpload'

    def ready(self):
        from app.cache.FeatureVector import FeatureVector 
        #
        print('go to initialzie FeatureVector')
        FeatureVector()