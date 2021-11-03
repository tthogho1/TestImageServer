from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.http import HttpResponse
from django.template import loader

import sys
import json
from .ImageAnalysis import ImageAnalysis

# ------------------------------------------------------------------
def file_upload(request):
    #
    #
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        #
        if form.is_valid():
            imageAnalysis = ImageAnalysis()
            #
            resultList = []
            for file_obj in request.FILES.getlist('file'):
                handle_uploaded_file(file_obj)
                #
                result = imageAnalysis.getOutput(file_obj.name)
                result_dict = {k: v.item() for k, v in result.items()}
                resultList.append(result_dict)
                #json_str =json.dumps(result_dict,ensure_ascii=False);
                json_str =json.dumps(resultList,ensure_ascii=False);
                print(json_str)
         
            return HttpResponse(json_str)
    else:
        form = UploadFileForm()
    #
    #
    return render(request, 'app/upload.html', {'form': form})
#
#
def get_vector(file_obj):
    imageAnalysis = ImageAnalysis()
    result = imageAnalysis.getVector(file_obj.name)
    print(result)
    return result
#
#
def compare(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            imageAnalysis = ImageAnalysis()
            vectorList = []
            for file_obj in request.FILES.getlist('file'):
                handle_uploaded_file(file_obj)
                imgVector = get_vector(file_obj)
                vectorList.append(imgVector)

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
 
