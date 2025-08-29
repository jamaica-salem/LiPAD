import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models

class DistortionClassifier18(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.network = models.resnet18()
        self.network.fc = nn.Linear(self.network.fc.in_features, num_classes)

    def forward(self, xb):
        return self.network(xb)