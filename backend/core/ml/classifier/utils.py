import torch
from PIL import Image
import torchvision.transforms as transforms
from .model import DistortionClassifier18

# Globals
_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_class_labels = ["h_blur", "low_light", "low_qual", "normal", "v_blur"]

_transform = transforms.Compose([
    transforms.Resize((128, 256)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

def load_cnn_model(model_path="core/ml/classifier/weights/distortion_classifier.pt"):
    global _model
    _model = DistortionClassifier18(num_classes=len(_class_labels))
    _model.to(_device)
    _model.load_state_dict(torch.load(model_path, map_location=_device))
    _model.eval()

def predict_image(image_file):
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_cnn_model() first.")
    
    img = Image.open(image_file).convert("RGB")
    input_tensor = _transform(img).unsqueeze(0).to(_device)

    with torch.no_grad():
        outputs = _model(input_tensor)
        _, predicted = torch.max(outputs, 1)
        class_id = int(predicted.item())

        return {"class_id": class_id, "class_name": _class_labels[class_id]}