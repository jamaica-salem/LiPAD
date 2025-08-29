import torch
import torch.nn as nn
import torch.nn.functional as F

class ResConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, dropout=0.0, batch_norm=False):
        super().__init__()
        padding = kernel_size // 2

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding)
        self.bn1 = nn.BatchNorm2d(out_channels) if batch_norm else nn.Identity()

        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size, padding=padding)
        self.bn2 = nn.BatchNorm2d(out_channels) if batch_norm else nn.Identity()
        
        self.drop = nn.Dropout(p=dropout) if dropout > 0 else nn.Identity()

        self.shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=1, padding=0)
        self.bn_sc = nn.BatchNorm2d(out_channels) if batch_norm else nn.Identity()

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = F.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.drop(out)

        shortcut = self.shortcut(residual)
        shortcut = self.bn_sc(shortcut)

        out += shortcut
        out = F.relu(out)
        return out


class GatingSignal(nn.Module):
    def __init__(self, in_channels, out_channels, batch_norm=False):
        super().__init__()
        layers = [nn.Conv2d(in_channels, out_channels, kernel_size=1, padding=0)]
        if batch_norm:
            layers.append(nn.BatchNorm2d(out_channels))
        layers.append(nn.ReLU(inplace=True))
        self.gate = nn.Sequential(*layers)

    def forward(self, x):
        return self.gate(x)

class AttentionBlock(nn.Module):
    def __init__(self, in_channels, gating_channels, inter_channels):
        super().__init__()

        self.theta_x = nn.Conv2d(in_channels, inter_channels, kernel_size=2, stride=2, padding=0) # Theta_x: downsample input x
        self.phi_g = nn.Conv2d(gating_channels, inter_channels, kernel_size=1, padding=0) # Phi_g: transform gating signal

        self.upsample_g = nn.ConvTranspose2d(inter_channels, inter_channels, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.combine = nn.Sequential(
            nn.ReLU(inplace=True),
            nn.Conv2d(inter_channels, 1, kernel_size=1),
            nn.Sigmoid())

        self.final_conv = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, kernel_size=1),
            nn.BatchNorm2d(in_channels))

    def forward(self, x, g):
        # x: skip connection feature map
        # g: gating signal (decoder feature map)
        theta_x = self.theta_x(x)
        phi_g = self.phi_g(g)

        # Upsample gating to match theta_x
        upsample_g = self.upsample_g(phi_g)

        if upsample_g.shape != theta_x.shape:
            upsample_g = F.interpolate(upsample_g, size=theta_x.shape[2:], mode='bilinear', align_corners=True)

        psi = self.combine(theta_x + upsample_g)
        psi = F.interpolate(psi, size=x.shape[2:], mode='bilinear', align_corners=True)
        psi = psi.expand(-1, x.shape[1], -1, -1)

        y = x * psi
        return self.final_conv(y)


class AttentionResUNetGenerator(nn.Module):
    def __init__(self, in_channels=3, out_channels=3, base_filters=64, dropout=0.0, batch_norm=True):
        super().__init__()

        # Encoder
        self.down1 = ResConvBlock(in_channels, base_filters, dropout=dropout, batch_norm=batch_norm) # 3 x 64
        self.pool1 = nn.MaxPool2d(2)
        self.down2 = ResConvBlock(base_filters, base_filters * 2, dropout=dropout, batch_norm=batch_norm) # 64 x 128
        self.pool2 = nn.MaxPool2d(2)
        self.down3 = ResConvBlock(base_filters * 2, base_filters * 4, dropout=dropout, batch_norm=batch_norm) # 128 x 256
        self.pool3 = nn.MaxPool2d(2)
        self.down4 = ResConvBlock(base_filters * 4, base_filters * 8, dropout=dropout, batch_norm=batch_norm) # 256 x 512
        self.pool4 = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = ResConvBlock(base_filters * 8, base_filters * 16, dropout=dropout, batch_norm=batch_norm) # 512 x 1024

        # Gating and Attention
        self.gate4 = GatingSignal(base_filters * 16, base_filters * 8, batch_norm) # 1024 x 512
        self.attn4 = AttentionBlock(base_filters * 8, base_filters * 8, base_filters * 8) # 512 x 512

        self.gate3 = GatingSignal(base_filters * 8, base_filters * 4, batch_norm) # 512 x 256
        self.attn3 = AttentionBlock(base_filters * 4, base_filters * 4, base_filters * 4) # 256 x 256

        self.gate2 = GatingSignal(base_filters * 4, base_filters * 2, batch_norm) # 256 x 128
        self.attn2 = AttentionBlock(base_filters * 2, base_filters * 2, base_filters * 2) # 128 x 128

        self.gate1 = GatingSignal(base_filters * 2, base_filters, batch_norm) # 128 x 64
        self.attn1 = AttentionBlock(base_filters, base_filters, base_filters) # 64 x 64

        # Decoder
        self.up4 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True) # 2048
        self.dec4 = ResConvBlock(base_filters * 16 + base_filters * 8, base_filters * 8, dropout=dropout, batch_norm=batch_norm)

        self.up3 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.dec3 = ResConvBlock(base_filters * 8 + base_filters * 4, base_filters * 4, dropout=dropout, batch_norm=batch_norm)

        self.up2 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.dec2 = ResConvBlock(base_filters * 4 + base_filters * 2, base_filters * 2, dropout=dropout, batch_norm=batch_norm)

        self.up1 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.dec1 = ResConvBlock(base_filters * 2 + base_filters, base_filters, dropout=dropout, batch_norm=batch_norm)

        # Output Layer
        self.final_conv = nn.Sequential(
            nn.Conv2d(base_filters, out_channels, kernel_size=1),
            nn.Tanh())

    def forward(self, x):
        d1 = self.down1(x)
        p1 = self.pool1(d1)
        d2 = self.down2(p1)
        p2 = self.pool2(d2)
        d3 = self.down3(p2)
        p3 = self.pool3(d3)
        d4 = self.down4(p3)
        p4 = self.pool4(d4)

        bn = self.bottleneck(p4)

        g4 = self.gate4(bn)
        a4 = self.attn4(d4, g4)
        u4 = self.up4(bn)
        u4 = torch.cat([u4, a4], dim=1)
        d5 = self.dec4(u4)

        g3 = self.gate3(d5)
        a3 = self.attn3(d3, g3)
        u3 = self.up3(d5)
        u3 = torch.cat([u3, a3], dim=1)
        d6 = self.dec3(u3)

        g2 = self.gate2(d6)
        a2 = self.attn2(d2, g2)
        u2 = self.up2(d6)
        u2 = torch.cat([u2, a2], dim=1)
        d7 = self.dec2(u2)

        g1 = self.gate1(d7)
        a1 = self.attn1(d1, g1)
        u1 = self.up1(d7)
        u1 = torch.cat([u1, a1], dim=1)
        d8 = self.dec1(u1)

        return self.final_conv(d8)