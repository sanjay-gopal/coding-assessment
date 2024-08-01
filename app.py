#
# The image description web service
#
from fastapi import FastAPI, File, UploadFile
import uvicorn
import clip
from io import BytesIO
from PIL import Image
import torch
from torchvision.datasets import CIFAR100
import os
from fastapi.responses import JSONResponse
import json


# Load the model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load('ViT-B/32', device)

# Download the dataset
cifar100 = CIFAR100(root=os.path.expanduser("~/.cache"), download=True, train=False)

app = FastAPI()

#
# The description API
#
@app.post("/description")
async def generate_description(image: UploadFile = File(...)):
    image = await image.read()

    image_obj = Image.open(BytesIO(image))
    image_input = preprocess(image_obj).unsqueeze(0).to(device)
    text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in cifar100.classes]).to(device)

    # Calculate features
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_inputs)

    # Pick the top 5 most similar labels for the image
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    values, indices = similarity[0].topk(5)

    # Print the result
    result = {}
    for value, index in zip(values, indices):
        # Print to console for debugging purposes
        # print(f"{cifar100.classes[index]:>16s}: {100 * value.item():.2f}%")
        result[cifar100.classes[index]] = 100 * value.item()

    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

