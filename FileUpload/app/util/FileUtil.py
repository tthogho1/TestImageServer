import sys
import os

# Create your models here.
class FileUtil :

    @staticmethod
    def handleUploadedFile(file_obj,path):
        file_path = file_obj.name 
        sys.stderr.write(file_path + "\n")
        with open(path + file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

    @staticmethod
    def deleteUploadedFile(file_obj,path):
        file_path = file_obj.name
        os.remove(path + file_path)


    @staticmethod
    def handleUploadedFileByName(data,path,fileName):
        sys.stderr.write(fileName + "\n")
        with open(path + fileName, 'wb+') as destination:
            destination.write(data)
    
    @staticmethod
    def deleteUploadedFileByName(fileName,path):
        os.remove(path + fileName)