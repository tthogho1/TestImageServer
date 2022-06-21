#from django.http import HttpResponseRedirect
import json
import logging
import urllib.request

from django.shortcuts import render
from .forms import UploadFileForm
from django.http import HttpResponse
from django.template import loader
from .cache.FeatureVector import FeatureVector
from .cache.AppConfig import AppConfig
from .ImageAnalysis import ImageAnalysis
from django.http import FileResponse
from .util.FileUtil import FileUtil

# ------------------------------------------------------------------
logger = logging.getLogger(__name__)
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
            logger.info("file upload start");
            resultList = []
            for file_obj in request.FILES.getlist('file'):
                FileUtil.handleUploadedFile(file_obj,TEMP_FOLDER)
                result = imageAnalysis.getOutput(file_obj.name)
                result_dict = {k: v.item() for k, v in result.items()}
                resultList.append(result_dict)
                FileUtil.deleteUploadedFile(file_obj,TEMP_FOLDER)
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
        FileUtil.handleUploadedFile(file_obj,folder)
        imgVector = imageAnalysis.getVector(file_obj.name)
        if (deleteFlg) :
            FileUtil.deleteUploadedFile(file_obj,folder)
        break   

    return imgVector,file_obj.name
#
#
#
def __get_vector_from_data(data,fileName,model_kind,folder,deleteFlg):
    imageAnalysis = ImageAnalysis(model_kind)
    imageAnalysis.set_folder(folder)
    imgVector = None
    FileUtil.handleUploadedFileByName(data,folder,fileName)
    imgVector = imageAnalysis.getVector(fileName)
    if (deleteFlg) :
        FileUtil.deleteUploadedFileByName(fileName,folder)
    
    return imgVector
#
#
def get_similar_image(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            model_kind= request.POST.get('analyze_model',None) # no param
            t_vector,fileName =__get_vector(request,model_kind,TEMP_FOLDER,True)

            vector = FeatureVector.getInstance()  
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
def get_similar_imageUrl(request):

    if request.method == 'POST':
        model_kind= request.POST.get('analyze_model',None) # no param

        imgUrl = request.POST.get('imgUrl')
        fileName = imgUrl.split("/")[-1]
        req = urllib.request.Request(imgUrl)
        body=None
        with urllib.request.urlopen(req) as res:
            body = res.read()

        t_vector = __get_vector_from_data(body,fileName,model_kind,TEMP_FOLDER,True)

        vector = FeatureVector.getInstance()  
        cosign = vector.get_similar_vector(t_vector)
        faiss = vector.get_similar_vectorByIndex(t_vector)
            
        l=[]

        l.append(cosign)
        l.append(faiss)
        json_string = json.dumps(l)
        print(json_string)
        return HttpResponse(json_string)
    #
    #
    return render(request, 'app/searchByUrl.html')
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
            vector=FeatureVector.getInstance()
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
                FileUtil.handleUploadedFile(file_obj,TEMP_FOLDER)
                imgVector = imageAnalysis.getVector(file_obj.name)
                vectorList.append(imgVector)
                FileUtil.deleteUploadedFile(file_obj,TEMP_FOLDER)

            result = imageAnalysis.cosineSimilarity(vectorList[0],vectorList[1])
            str = result.item()
            return HttpResponse(str)
        


def custom_error_404(request,exception):
    return render(request,'404.html',{})

def custom_error_500(request,*args, **argv):
    return render(request,'500.html',status=500)

