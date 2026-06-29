"""Grad-CAM heatmap generation using pytorch-grad-cam."""
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as T

try:
    from pytorch_grad_cam import GradCAM
    from pytorch_grad_cam.utils.image import show_cam_on_image
    GRADCAM_AVAILABLE = True
except ImportError:
    GRADCAM_AVAILABLE = False

from utils.inference import _load_model, _transform

_transform_np = T.Compose([T.Resize((224, 224)), T.ToTensor()])


def generate_gradcam(file_like):
    """Return an RGB numpy array overlay, or None if unavailable."""
    if not GRADCAM_AVAILABLE:
        return None
    img = Image.open(file_like).convert("RGB")
    tensor = _transform(img).unsqueeze(0)
    rgb = np.array(img.resize((224, 224))) / 255.0

    model = _load_model()
    target_layer = model.features[-1]

    with GradCAM(model=model, target_layers=[target_layer]) as cam:
        grayscale = cam(input_tensor=tensor)[0]

    overlay = show_cam_on_image(rgb.astype(np.float32), grayscale, use_rgb=True)
    return overlay
