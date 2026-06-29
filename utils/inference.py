"""Model loading and single-image inference."""
import io
import torch
import torchvision.transforms as T
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from PIL import Image

CLASSES = ["Acne", "Eczema", "Melanoma", "Psoriasis"]
NUM_CLASSES = len(CLASSES)
MODEL_PATH = "models/dermassist_best.pt"

_model = None

_transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _load_model():
    global _model
    if _model is not None:
        return _model
    weights = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, NUM_CLASSES)
    try:
        state = torch.load(MODEL_PATH, map_location="cpu")
        model.load_state_dict(state)
    except FileNotFoundError:
        pass  # weights not yet trained; returns untrained model for dev
    model.eval()
    _model = model
    return model


def predict_image(file_like):
    """Return (label, confidence, probabilities_tensor)."""
    img = Image.open(file_like).convert("RGB")
    tensor = _transform(img).unsqueeze(0)
    model = _load_model()
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze()
    idx = int(probs.argmax())
    return CLASSES[idx], float(probs[idx]), probs.tolist()
