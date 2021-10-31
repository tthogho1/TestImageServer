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
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # sys.stderr.write("*** file_upload \n")
            file_obj = request.FILES['file']
            handle_uploaded_file(file_obj)
            imageAnalysis = ImageAnalysis()
            result = imageAnalysis.getOutput(file_obj.name)
            result_dict = {k: v.item() for k, v in result.items()}
            json_str =json.dumps(result_dict,ensure_ascii=False);
            print(json_str)
            return HttpResponse(json_str)
    else:
        form = UploadFileForm()
    return render(request, 'app/upload.html', {'form': form})
#
#
# ------------------------------------------------------------------
def handle_uploaded_file(file_obj):
    file_path = file_obj.name 
    sys.stderr.write(file_path + "\n")
    with open('media/' + file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
 
# ------------------------------------------------------------------
def success(request):
    str_out = "Success!<p />"
    str_out += "成功<p />"
    return HttpResponse(str_out)
# ------------------------------------------------------------------