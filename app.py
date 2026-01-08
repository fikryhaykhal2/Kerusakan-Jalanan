import torch
import io
from fastapi import FastAPI, UploadFile, File
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# 1. INISIALISASI APP & MODEL
app = FastAPI()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "openai/clip-vit-base-patch32"
model_clip = CLIPModel.from_pretrained(model_name).to(device)
processor_clip = CLIPProcessor.from_pretrained(model_name)

# 2. DEFINISI KELAS & PROMPT (Sesuai riset Anda)
CLASSES = [
    "Jalan Berlubang", "Jalan Normal", "Pengausan Agregat", 
    "Retak Acak", "Retak Memanjang", "Retak kulit buaya", "Tambalan"
]

DETAILED_PROMPTS = {
    "Jalan Berlubang": "a deep localized circular pit or cavity in the asphalt road, dark sunken pothole with sharp edges",
    "Jalan Normal": "plain clean grey asphalt road surface, smooth pavement without any visible cracks or damage",
    "Pengausan Agregat": "rough road texture where stones and gravel are exposed, missing asphalt binder, stony surface",
    "Retak Acak": "multiple irregular horizontal or transverse cracks crossing the road width, scattered asphalt cracking",
    "Retak Memanjang": "a single thin vertical crack line running parallel to the road direction, longitudinal asphalt fracture",
    "Retak kulit buaya": "complex interconnected pattern of small cracks resembling scaly crocodile skin, alligator cracking distress",
    "Tambalan": "a distinct dark rectangular patch of new asphalt placed over an old road repair, repaved asphalt section"
}

PROMPT_LIST = [DETAILED_PROMPTS[cls] for cls in CLASSES]

@app.get("/")
def home():
    return {"status": "Model Kerusakan Jalan Aktif", "device": device}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 1. Baca gambar yang dikirim dari n8n/Telegram
    request_object_content = await file.read()
    image = Image.open(io.BytesIO(request_object_content)).convert("RGB")

    # 2. Preprocessing & Inference (Logika dari Notebook Anda)
    inputs = processor_clip(
        text=PROMPT_LIST, 
        images=image, 
        return_tensors="pt", 
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model_clip(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]

    # 3. Ambil Prediksi Terbaik
    best_idx = probs.argmax()
    confidence = float(probs[best_idx])
    label = CLASSES[best_idx]

    # 4. Response untuk n8n
    return {
        "jenis_kerusakan": label,
        "confidence": round(confidence, 4),
        "deskripsi_semantik": PROMPT_LIST[best_idx],
        "status": "success"
    }

# Cara menjalankan: uvicorn app:app --host 0.0.0.0 --port 8000