Index: app.py
===================================================================
--- app.py	Before
+++ app.py	After
@@ -1,24 +1,49 @@
-# app.py
-from fastapi import FastAPI, File, UploadFile
-from PIL import Image
-from transformers import BlipProcessor, BlipForConditionalGeneration
-import torch
-
-# ✅ Create the FastAPI instance
-app = FastAPI()
-
-# ✅ Load AI model
-processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
-model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
-
-@app.get("/")
-def root():
-    return {"message": "Backend is working!"}
-
-@app.post("/describe-image/")
-async def describe_image(file: UploadFile = File(...)):
-    image = Image.open(file.file)
-    inputs = processor(images=image, return_tensors="pt")
-    out = model.generate(**inputs)
-    caption = processor.decode(out[0], skip_special_tokens=True)
-    return {"description": caption}
+from typing import Optional
+from pathlib import Path
+import os
+import tempfile
+
+from fastapi import FastAPI, File, UploadFile
+from PIL import Image
+from transformers import BlipProcessor, BlipForConditionalGeneration
+import torch
+
+from gesturereco import VoiceSignSpeechService
+
+app = FastAPI()
+
+processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
+model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
+voice_service = VoiceSignSpeechService()
+
+
+@app.get("/")
+def root():
+    return {"message": "Backend is working!"}
+
+
+@app.post("/describe-image/")
+async def describe_image(file: UploadFile = File(...)):
+    image = Image.open(file.file)
+    inputs = processor(images=image, return_tensors="pt")
+    out = model.generate(**inputs)
+    caption = processor.decode(out[0], skip_special_tokens=True)
+    return {"description": caption}
+
+
+@app.post("/voice-to-sign/")
+async def voice_to_sign(
+    file: UploadFile = File(...),
+    language: Optional[str] = None,
+    speak: bool = False,
+):
+    data = await file.read()
+    suffix = Path(file.filename).suffix if file.filename else ".wav"
+    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
+        tmp.write(data)
+        tmp_path = tmp.name
+    try:
+        result = voice_service.process_audio_file(tmp_path, language=language, speak=speak)
+    finally:
+        os.unlink(tmp_path)
+    return result
from typing import Optional
from pathlib import Path
import os
import tempfile

from fastapi import FastAPI, File, UploadFile
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

from gesturereco import VoiceSignSpeechService

app = FastAPI()

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
voice_service = VoiceSignSpeechService()


@app.get("/")
def root():
    return {"message": "Backend is working!"}


@app.post("/describe-image/")
async def describe_image(file: UploadFile = File(...)):
    image = Image.open(file.file)
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return {"description": caption}


@app.post("/voice-to-sign/")
async def voice_to_sign(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    speak: bool = False,
):
    data = await file.read()
    suffix = Path(file.filename).suffix if file.filename else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        result = voice_service.process_audio_file(tmp_path, language=language, speak=speak)
    finally:
        os.unlink(tmp_path)
    return result
