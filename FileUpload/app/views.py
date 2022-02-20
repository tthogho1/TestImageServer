from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.http import HttpResponse
from django.template import loader
import os
import sys
import json
from .cache.featureVector import featureVector
from .cache.AppConfig import AppConfig
from .ImageAnalysis import ImageAnalysis
from django.core.cache import cache
from django.http import FileResponse

# ------------------------------------------------------------------
model_kind="resnet50"
G_DICTIONARY= {}
config = AppConfig().get_config()
TEMP_FOLDER = config['image']['temp_image_folder']
IMAGE_FOLDER = config['image']['image_folder']

# ------------------------------------------------------------------
def file_upload(request):
    #
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        #
        model_kind= request.POST.get('analyze_model',None)
        if form.is_valid():
            imageAnalysis = ImageAnalysis(model_kind)
            imageAnalysis.set_folder(TEMP_FOLDER)
            #
            resultList = []
            for file_obj in request.FILES.getlist('file'):
                handle_uploaded_file(file_obj,TEMP_FOLDER)
                result = imageAnalysis.getOutput(file_obj.name)
                result_dict = {k: v.item() for k, v in result.items()}
                resultList.append(result_dict)
                delete_uploaded_file(file_obj,TEMP_FOLDER)
            json_str =json.dumps(resultList,ensure_ascii=False)
         
            return HttpResponse(json_str)
    else:
        form = UploadFileForm()
    #
    #
    return render(request, 'app/upload.html', {'form': form})
#
#
#
def file_download(request,F):
    file_path = IMAGE_FOLDER + F
    filename = F
    return FileResponse(open(file_path, "rb"), as_attachment=False, filename=filename)

#
#
#
def __get_vector(request,model_kind,folder,deleteFlg):
    imageAnalysis = ImageAnalysis(model_kind)
    imageAnalysis.set_folder(folder)
    imgVector = None
    for file_obj in request.FILES.getlist('file'): # one file only
        handle_uploaded_file(file_obj,folder)
        imgVector = imageAnalysis.getVector(file_obj.name)
        if (deleteFlg) :
            delete_uploaded_file(file_obj,folder)
        break   

    return imgVector,file_obj.name
#
#
def get_similar_image(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            model_kind= request.POST.get('analyze_model',None) # no param
            t_vector,fileName =__get_vector(request,model_kind,TEMP_FOLDER,True)

            vector = featureVector()  
            cosign = vector.get_similar_vector(t_vector)
            faiss = vector.get_similar_vectorByIndex(t_vector)
            
            l=[]

            l.append(cosign)
            l.append(faiss)
            json_string = json.dumps(l)
            print(json_string)
            return HttpResponse(json_string)
        else:
            t_vector=""
            # t.b.d
    else:
        form = UploadFileForm()
    #
    #
    return render(request, 'app/search.html', {'form': form})
#       
#
#
#
def cache_feature_vector(request):
    str="NG"
    if request.method == 'POST':
        model_kind= request.POST.get('analyze_model',None) # no param
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            imgVector , fileName = __get_vector(request,model_kind,IMAGE_FOLDER,False)
            vector=featureVector()
            vector.add_feature_vector(imgVector,fileName)
            str="OK"

    return HttpResponse(str)
#
#
def compare(request):
    if request.method == 'POST':
        model_kind= request.POST.get('analyze_model',None)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            imageAnalysis = ImageAnalysis(model_kind)
            imageAnalysis.set_folder(TEMP_FOLDER)
            vectorList = []
            for file_obj in request.FILES.getlist('file'):
                handle_uploaded_file(file_obj,TEMP_FOLDER)
                imgVector = __get_vector(file_obj,model_kind)
                vectorList.append(imgVector)
                delete_uploaded_file(file_obj,TEMP_FOLDER)

            result = imageAnalysis.cosineSimilarity(vectorList[0],vectorList[1])
            str = result.item()
            #result_dict = {k: v.item() for k, v in result.items()}
            #json_str =json.dumps(result_dict,ensure_ascii=False);
            return HttpResponse(str)
        
# ------------------------------------------------------------------
def handle_uploaded_file(file_obj,path):
    file_path = file_obj.name 
    sys.stderr.write(file_path + "\n")
    with open(path + file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

def delete_uploaded_file(file_obj,path):
    file_path = file_obj.name
    os.remove(path + file_path)

def custom_error_404(request,exception):
    return render(request,'404.html',{})

def custom_error_500(request,*args, **argv):
    return render(request,'500.html',status=500)

