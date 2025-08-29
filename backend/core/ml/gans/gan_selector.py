import torch
from PIL import Image
import torchvision.transforms as transforms
from .base_gan import AttentionResUNetGenerator

# Globals
_gans = {}
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Pre/post transforms 
_transforms = transforms.Compose([
    transforms.Resize((128, 256)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])
_to_pil = transforms.ToPILImage()

_gan_paths = {
    'h_blur': 'core/ml/gans/weights/gan_h_blur.pt',
    'v_blur': 'core/ml/gans/weights/gan_v_blur.pt',
    'low_light': 'core/ml/gans/weights/gan_low_light.pt',
    'low_qual': 'core/ml/gans/weights/gan_low_qual.pt'
}

def load_gans():
    global _gans
    for distortion, ckpt in _gan_paths.items():
        model = AttentionResUNetGenerator()
        model.load_state_dict(torch.load(ckpt, map_location=_device))
        model.to(_device)
        model.eval()
        _gans[distortion] = model
    print(f'[GAN] Loaded {len(_gans)} GAN models')

def run_gan(image_file, distortion_class):
    if distortion_class not in _gans:
        # EDIT FOR NORMAL
        raise ValueError(f'No GAN available for class {distortion_class}')
    
    # Load image
    if isinstance(image_file, str):
        img = Image.open(image_file).convert("RGB")
    else:
        img = Image.open(image_file).convert("RGB")

    # Preprocess
    input_tensor = _transforms(img).unsqueeze(0).to(_device)

    # Inference
    with torch.no_grad():
        enhanced_tensor = _gans[distortion_class](input_tensor)

    # Convert back to PIL
    enhanced_tensor = enhanced_tensor.squeeze(0).cpu().clamp(-1, 1)
    enhanced_img = _to_pil((enhanced_tensor * 0.5 + 0.5)) # denormalize
    return enhanced_img