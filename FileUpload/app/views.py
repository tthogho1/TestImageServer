from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.http import HttpResponse
from django.template import loader
import os
import sys
import json
from .ImageAnalysis import ImageAnalysis
from django.core.cache import cache
from django.http import FileResponse

# ------------------------------------------------------------------
model_kind="resnet50"
G_DICTIONARY= {}
# ------------------------------------------------------------------
def file_upload(request):
    #
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        #
        model_kind= request.POST.get('analyze_model',None)
        if form.is_valid():
            imageAnalysis = ImageAnalysis(model_kind)
            #
            resultList = []
            for file_obj in request.FILES.getlist('file'):
                handle_uploaded_file(file_obj)
                result = imageAnalysis.getOutput(file_obj.name)
                result_dict = {k: v.item() for k, v in result.items()}
                resultList.append(result_dict)
                delete_uploaded_file(file_obj)
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
    file_path = 'media/' + F
    filename = F
    return FileResponse(open(file_path, "rb"), as_attachment=False, filename=filename)

#
#
#
def get_similar_image(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        model_kind= request.POST.get('analyze_model',None) # no param
        imageAnalysis = ImageAnalysis(model_kind)
        #
        t_vector=""
        for file_obj in request.FILES.getlist('file'): # only one file
            handle_uploaded_file(file_obj)
            t_vector = imageAnalysis.getVector(file_obj.name)
            delete_uploaded_file(file_obj) 

        imgVectorDictionary = cache.get('imgVector')
        maxSimilarity = 0
        for k, v in imgVectorDictionary.items():
            result = imageAnalysis.cosineSimilarity(t_vector,v)
            t_Similarity = result.item()
            if (t_Similarity > maxSimilarity  ):
                maxSimilarity = t_Simirarity
                key = k

    return HttpResponse(maxSimilarity)
#
#
#
def get_vector(file_obj,model_kind):
    imageAnalysis = ImageAnalysis(model_kind)
    result = imageAnalysis.getVector(file_obj.name)
    print(result)
    return result
#
#
#
def cache_feature_vector(request):
    str="NG"
    imgVectorDictionary = cache.get('imgVector')
    if imgVectorDictionary == None:
        imgVectorDictionary = {}
        cache.set('imgVector',imgVectorDictionary)

    if request.method == 'POST':
        model_kind= request.POST.get('analyze_model',None) # no param
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            imageAnalysis = ImageAnalysis(model_kind)
            for file_obj in request.FILES.getlist('file'): # one file only
                handle_uploaded_file(file_obj)
                imgVector = imageAnalysis.getVector(file_obj.name)
                imgVectorDictionary[file_obj.name]=imgVector
                cache.set('imgVector',imgVectorDictionary)
             #   delete_uploaded_file(file_obj)
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
            vectorList = []
            for file_obj in request.FILES.getlist('file'):
                handle_uploaded_file(file_obj)
                imgVector = get_vector(file_obj,model_kind)
                vectorList.append(imgVector)
                delete_uploaded_file(file_obj)

            result = imageAnalysis.cosineSimilarity(vectorList[0],vectorList[1])
            str = result.item()
            #result_dict = {k: v.item() for k, v in result.items()}
            #json_str =json.dumps(result_dict,ensure_ascii=False);
            return HttpResponse(str)
        
# ------------------------------------------------------------------
def handle_uploaded_file(file_obj):
    file_path = file_obj.name 
    sys.stderr.write(file_path + "\n")
    with open('media/' + file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

def delete_uploaded_file(file_obj):
    file_path = file_obj.name
    os.remove('media/' + file_path)
