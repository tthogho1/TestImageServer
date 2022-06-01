from threading import Lock
from django.core.cache import cache
from app.ImageAnalysis import ImageAnalysis
import json
import faiss
import numpy as np
import time

class FeatureVector:
    _instance = None
    _vectorDictionary = None
    _imageList = None
    _lock = Lock()
    _Index = None
    d=512 # faiss dimenstion 
    __instance = None

    @staticmethod
    def getInstance():
      if FeatureVector.__instance == None:
         FeatureVector()
      return FeatureVector.__instance


    def __init__(self):
        if FeatureVector.__instance != None:
            raise Exception("Singleton class")
        else:
            FeatureVector.__instance = self

        print('do init')
        self._vectorDictionary = cache.get('imgVector')
        if self._vectorDictionary == None:
            self._vectorDictionary = {}
            cache.set('imgVector',self._vectorDictionary)    

        self._imageList = cache.get('imgName')
        if self._imageList == None:
            self._imageList = []
            cache.set('imgName',self._imageList)

        self._Index = cache.get('faissIndex')
        if self._Index is None:
            print('initialize faiss index')
            self._Index = faiss.IndexFlatL2(self.d)
            print(self._Index.is_trained)
            cache.set('faissIndex',self._Index)

#
#    def __new__(cls):
#        if cls._instance is None:
#            cls._instance = super().__new__(cls)
#
#        return cls._instance

    #
    def add_feature_vector(self,imgVector,_name):
        if self._lock.acquire():
            try:
                self._vectorDictionary[_name]=imgVector
                cache.set('imgVector',self._vectorDictionary)
                # faiss 
                self._imageList.append(_name)
                print(str(len(self._imageList)) + ":" + _name )
                cache.set('imgName',self._imageList)

                xb = np.array(imgVector).reshape((1,512))
                self._Index.add(xb)
                print('Index Size : ' + str(self._Index.ntotal))
                cache.set('faissIndex',self._Index)
            finally:
                self._lock.release()
#
    
    def get_similar_vector(self,t_vector):
           
        imgVectorDictionary = self._vectorDictionary
        model_kind=None # need to set
        imageAnalysis = ImageAnalysis(model_kind) # model_kind = null

        t_start = time.time() 

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

        #json_string = json.dumps(l)
        t_end = time.time() 
        diff = t_end - t_start

        print("similarity check " + str(diff))

        return l

    def get_similar_vectorByIndex(self,t_vector):
        
        t_start = time.time()

        xb = np.array(t_vector).reshape((1,512))   
        print(self._Index.ntotal)

        model_kind=None # need to set
        imageAnalysis = ImageAnalysis(model_kind) # model_kind = null


        D, I = self._Index.search(xb, 3) # sanity check
        IList = I[0]
        DList = D[0]
        l=[] # initialize list
        for i in range(3):
            t_obj ={}
            t_obj['file']=self._imageList[IList[i]]
            t_obj['similarity']=str(DList[i])
            l.insert(i,t_obj)

        #json_string = json.dumps(l)
        t_end = time.time() 
        diff = t_end - t_start

        print("distance check " + str(diff))

        return l
