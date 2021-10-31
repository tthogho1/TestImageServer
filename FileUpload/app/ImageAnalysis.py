# 
# # pip install torch torchvision
# # pip install scikit-learn

import json
from pathlib import Path

import numpy as np
import torch
import torchvision
from PIL import Image
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets.utils import download_url


class ImageAnalysis:
    def __init__(self):
        self.name=""
        self.device = self.get_device(True)
        self.model = torchvision.models.resnet50(pretrained=True).to(self.device)
        self.transform = transforms.Compose(
        [
            transforms.Resize(256),  # 
            transforms.CenterCrop(224),  # 
            transforms.ToTensor(),  # 
            transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            ),  
        ]
        )
        self.class_names = self.get_classes()

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
            class_names = [x["ja"] for x in data]
        return class_names

    def getOutput(self,filename):
        img = Image.open("media/" + filename)
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
