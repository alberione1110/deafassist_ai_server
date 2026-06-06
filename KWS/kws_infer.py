import torch
import torchaudio
import numpy as np
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import soundfile as sf
# ===== 설정 =====
MODEL_NAME = "dbif/kws_tuning_model"

labels = [
    "background",
    "call",
    "shout",
    "crying",
    "car_horn",
    "dog_bark",
    "knock",
    "alarm"
]

thresholds = {
    0: 0.0,
    1: 0.90,
    2: 0.70,
    3: 0.85,
    4: 0.98,
    5: 0.65,
    6: 0.93,
    7: 0.90
}

# ===== 모델 & 전처리 로드 =====
model = AutoModelForAudioClassification.from_pretrained(MODEL_NAME)
feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)

model.eval()

device = torch.device("cpu")
model.to(device)

# ===== 방향 (임시) =====
def get_direction():
    return "b"

# ===== 오디오 로드 =====
def load_audio(path):
    waveform, sr = sf.read(path)

    # numpy → torch
    waveform = torch.tensor(waveform).float()

    # mono 변환
    if len(waveform.shape) > 1:
        waveform = waveform.mean(dim=1)

    # shape 맞추기 (1, T)
    waveform = waveform.unsqueeze(0)

    if sr != 16000:
        waveform = torchaudio.transforms.Resample(sr, 16000)(waveform)

    return waveform

# ===== 전처리 =====
def preprocess(waveform):
    waveform = waveform.squeeze()

    # 최소 길이 보장 (1초 기준)
    if waveform.shape[0] < 16000:
        pad = 16000 - waveform.shape[0]
        waveform = torch.nn.functional.pad(waveform, (0, pad))

    waveform = waveform.detach().cpu().numpy()

    return feature_extractor(
        waveform,
        sampling_rate=16000,
        return_tensors="pt"
    )

# ===== 샘플 기반 =====
SAMPLE_PATH = "sample_dog_bark.wav"

def predict_sample():
    waveform = load_audio(SAMPLE_PATH)
    inputs = preprocess(waveform)

    with torch.no_grad():
        inputs = {k: v.to(device) for k, v in inputs.items()}
        inputs = {k: v.float() for k, v in inputs.items()}  # optional but safe
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0]

    return process_output(probs)

# ===== wav 파일 기반 =====
def predict_from_wav(audio_path):
    waveform = load_audio(audio_path)
    inputs = preprocess(waveform)

    with torch.no_grad():
        inputs = {k: v.to(device) for k, v in inputs.items()}
        inputs = {k: v.float() for k, v in inputs.items()}  # optional but safe
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0]

    return process_output(probs)

def predict_from_waveform(waveform):
    """
    waveform: numpy or torch (16000 samples or chunk)
    """

    if isinstance(waveform, np.ndarray):
        waveform = torch.tensor(waveform).float()

    # mono 처리
    if waveform.dim() > 1:
        waveform = waveform.mean(dim=0)

    # shape 맞추기 (1, T)
    waveform = waveform.unsqueeze(0)

    return _infer(waveform)

def _infer(waveform):
    inputs = preprocess(waveform)

    with torch.no_grad():
        inputs = {k: v.to(device) for k, v in inputs.items()}
        inputs = {k: v.float() for k, v in inputs.items()}
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0]

    return process_output(probs)

# ===== 공통 처리 =====
def process_output(probs):
    detections = []

    for i, prob in enumerate(probs):
        if prob.item() >= thresholds[i]:
            detections.append((i, prob.item()))

    if len(detections) > 0:
        best = max(detections, key=lambda x: x[1])
        label_idx, score = best
        detected = True
    else:
        label_idx = int(torch.argmax(probs))
        score = float(probs[label_idx])
        detected = False

    return {
        "label": labels[label_idx],
        "score": score,
        "detected": detected,
        "direction": get_direction()
    }