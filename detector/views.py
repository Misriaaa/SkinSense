from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from django.conf import settings

# ---------- LOAD MODEL ----------
MODEL_PATH = os.path.join(settings.BASE_DIR, "skin_disease_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# ---------- CLASS LABELS ----------
CLASS_NAMES = {
    'akiec': 'Actinic Keratoses',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis-like Lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevi',
    'vasc': 'Vascular Lesions'
}


# ---------- HOME PAGE ----------
def home(request):
    """Render home page with disease categories."""
    return render(request, 'detector/index.html', {'class_names': CLASS_NAMES})

# ---------- UPLOAD & PREDICTION ----------
def upload(request):
    result = None
    warning = None

    if request.method == "POST" and request.FILES.get('image'):
        f = request.FILES['image']
        fs = FileSystemStorage()
        file_path = fs.save(f.name, f)
        full_path = fs.path(file_path)

        try:
            img = image.load_img(full_path, target_size=(128, 128))
            img_array = np.expand_dims(image.img_to_array(img) / 255.0, axis=0)

            predictions = model.predict(img_array)
            confidence = round(100 * np.max(predictions), 2)
            entropy = -np.sum(predictions * np.log(predictions + 1e-8))

            # Sort prediction probabilities
            sorted_preds = np.sort(predictions[0])[::-1]
            top1, top2 = sorted_preds[0], sorted_preds[1]
            confidence_gap = top1 - top2  # difference between top 2 predicted probabilities

            class_order = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']
            pred_index = np.argmax(predictions)
            pred_key = class_order[pred_index]
            pred_class = CLASS_NAMES[pred_key]

            # 🧠 Advanced Non-Skin Detection Logic
            if entropy > 1.6 or confidence < 30 or confidence_gap < 0.1:
                 warning = "⚠️ Unable to Detect Disease. The uploaded image doesn’t appear to be a valid skin lesion."
            else:
                 result = {
                    "class": pred_class,
                    "confidence": confidence,
                    "image_url": fs.url(file_path)
         }


        except Exception as e:
            warning = f"⚠️ Error processing image: {str(e)}"

    return render(request, "detector/upload.html", {"result": result, "warning": warning})

# ---------- ABOUT PAGE ----------
def about(request):
    return render(request, 'detector/about.html')


# ---------- RESULT PAGE ----------
def result(request):
    return render(request, "detector/result.html")
