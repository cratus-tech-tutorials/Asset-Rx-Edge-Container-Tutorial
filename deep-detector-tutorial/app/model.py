import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

MODEL = "weights.ptm"
IM_SCALE = (64, 64)
STATE_SHAPE = (1, *IM_SCALE)
NUM_CLASSES = 2

class ConvNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.num_channels = STATE_SHAPE[0]
        self.conv_out_shape = 1568
        self.fc1Dims = 64
        self.fc2Dims = 64

        self.conv = nn.Sequential(
            nn.Conv2d(self.num_channels, 8, 3, stride=2), nn.ReLU(),
            nn.Conv2d(8, 16, 3, stride=2), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2), nn.ReLU(),
        )
        self.classify = nn.Sequential(
            nn.Linear( self.conv_out_shape,  self.fc1Dims), nn.ReLU(),
            nn.Linear( self.fc1Dims, self.fc2Dims), nn.ReLU(),
            nn.Linear( self.fc2Dims, NUM_CLASSES ))

    def forward(self, x):
        x = self.conv(x)
        x = x.flatten().unsqueeze(0)
        x = self.classify(x)
        s = F.softmax(x, dim=1)
        m = torch.argmax(s, dim=1)
        return m
