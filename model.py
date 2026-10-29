import torch
import numpy as np
import torch.nn.functional as F
from transformers import VideoMAEImageProcessor, VideoMAEModel

WORDS = ["HELLO","YES","NO","PLEASE","THANK YOU"]

processor = VideoMAEImageProcessor.from_pretrained("MCG-NJU/videomae-base")
model = VideoMAEModel.from_pretrained("MCG-NJU/videomae-base")

# Predefined reference embeddings (demo)
reference_vectors = torch.randn(len(WORDS),768)

def preprocess_frames(frames,max_frames=16):

    if len(frames) > max_frames:
        step=len(frames)//max_frames
        frames=frames[::step][:max_frames]

    frames=[frame.astype(np.uint8) for frame in frames]

    return frames


def predict(frames):

    frames=preprocess_frames(frames)

    inputs=processor(frames,return_tensors="pt")

    with torch.no_grad():
        outputs=model(**inputs)

    features=outputs.last_hidden_state.mean(dim=1)

    similarities = F.cosine_similarity(features, reference_vectors)

    pred = torch.argmax(similarities).item()

    confidence = torch.max(similarities).item()

    confidence = round((confidence+1)/2*100,2)

    return WORDS[pred], confidence