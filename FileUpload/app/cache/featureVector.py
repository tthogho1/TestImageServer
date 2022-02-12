from threading import Lock
from django.core.cache import cache
from app.ImageAnalysis import ImageAnalysis
import json

class featureVector:
    _instance = None
    _vectorDictionary = None
    _lock = Lock()

    def __init__(self):
        print('init')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    #
    def add_feature_vector(self,imgVector,_name):
        if self._lock.acquire():
            try:
                self._vectorDictionary = cache.get('imgVector')
                if self._vectorDictionary == None:
                    self._vectorDictionary = {}
                self._vectorDictionary[_name]=imgVector
                cache.set('imgVector',self._vectorDictionary)
            finally:
                self._lock.release()
#
    def get_similar_vector(self,t_vector):
        if self._vectorDictionary == None :
           self._vectorDictionary = cache.get('imgVector')
           
        imgVectorDictionary = self._vectorDictionary
        model_kind=None # need to set
        imageAnalysis = ImageAnalysis(model_kind) # model_kind = null

        l=[] # initialize list
        for i in range(3):
            t_obj={}
            t_obj['file']="dummy"
            t_obj['similarity']=0
            l.insert(i,t_obj)

        for k, v in imgVectorDictionary.items():
            result = imageAnalysis.cosineSimilarity(t_vector,v)
            t_Similarity = result.item()
            t_obj ={}
            t_obj['file']=k
            t_obj['similarity']=t_Similarity
            l_obj=None
            length=len(l)
            for i in range(length):
                l_obj = l[i]
                if (t_Similarity > l_obj['similarity'] ):
                    l.insert(i,t_obj)
                    del l[length]
                    break

        json_string = json.dumps(l)
        return json_string

