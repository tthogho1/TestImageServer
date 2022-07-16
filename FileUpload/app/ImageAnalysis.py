# 
# # pip install torch torchvision
# # pip install scikit-learn

import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from torch.autograd import Variable
from PIL import Image

import torchvision
from PIL import Image
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets.utils import download_url
from .cache.AppConfig import AppConfig


class ImageAnalysis:
    config = AppConfig().get_config()
    TEMP_FOLDER = config['image']['temp_image_folder']
    IMAGE_FOLDER = config['image']['image_folder']

    def __init__(self,model_kind):
        self.device = self.get_device(True)
        if model_kind == "resnet50" :
            self.model = torchvision.models.resnet50(pretrained=True).to(self.device)
            self.OUTPUTSIZE = 2048
        else:
            self.model = torchvision.models.resnet18(pretrained=True).to(self.device)
            self.OUTPUTSIZE = 512
        self.name=""
        self.transform = transforms.Compose(
            [
                transforms.Resize(256),  # 
                transforms.CenterCrop(224),  # 
                transforms.ToTensor(),  # 
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  
            ]
        )
        self.class_names = self.get_classes()
        self.layer = self.model._modules.get('avgpool')
        self.folder=IMAGE_FOLDER
        print("media folder :" + IMAGE_FOLDER)

    def set_folder(self,path):
        self.folder=path

    def get_device(self,use_gpu):
        if use_gpu and torch.cuda.is_available():
            torch.backends.cudnn.deterministic = True
            return torch.device("cuda")
        else:
            return torch.device("cpu")


    def get_classes(self):
        if not Path("data/imagenet_class_index.json").exists():
            download_url("https://git.io/JebAs", "data", "imagenet_class_index.json")
        with open("data/imagenet_class_index.json",'r', encoding="utf-8") as f:
            data = json.load(f)
            class_names = [x["en"] for x in data]
        return class_names

    def getOutput(self,filename):
        img = Image.open(self.folder + filename)
        inputs = self.transform(img)
        inputs = inputs.unsqueeze(0).to(self.device)
        self.model.eval()
        outputs = self.model(inputs)
        result = self.printResult(outputs)
        return result

    def printResult(self,outputs):
        batch_probs = F.softmax(outputs, dim=1)
        batch_probs, batch_indices = batch_probs.sort(dim=1, descending=True)
        result  = dict()
        for probs, indices in zip(batch_probs, batch_indices):
            for k in range(3):
                result[self.class_names[indices[k]]]=probs[k]
                print(f"Top-{k + 1} {self.class_names[indices[k]]} {probs[k]:.2%}")
        return result

    def getVector(self,filename):
        img = Image.open(self.folder + filename)
        scaler = transforms.Scale((224, 224))
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
        to_tensor = transforms.ToTensor()
        self.model.eval()

        t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
        my_embedding = torch.zeros(self.OUTPUTSIZE)
        def copy_data(m, i, o):
            my_embedding.copy_(o.data.reshape(o.data.size(1)))
        h = self.layer.register_forward_hook(copy_data)
        self.model(t_img)
        h.remove()
        return my_embedding

    def cosineSimilarity(self,vector1,vector2):
        cos = nn.CosineSimilarity(dim=1, eps=1e-6)
        cos_sim = cos(vector1.unsqueeze(0),
                      vector2.unsqueeze(0))
        # print('\nCosine similarity: {0}\n'.format(cos_sim))
        return cos_sim
