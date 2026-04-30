import keras
from keras.layers import Input
from keras.models import Model
from keras.applications.resnet50 import preprocess_input, decode_predictions
from keras.applications import ResNet50
from PIL import Image
import numpy as np
import os

# загружаем предобученную ResNet50
model = ResNet50(weights='imagenet')

def read_image_files(files_max_count, dir_name, specific_file=None):
    """
    Загружает изображения из папки или конкретный файл
    """
    if specific_file:
        files = [specific_file]
    else:
        files = os.listdir(dir_name)
    
    files = files[:files_max_count]
    images = []
    for fname in files:
        path = os.path.join(dir_name, fname)
        img = Image.open(path)
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        images.append(img_array)
    
    return len(images), images

def getresult(images):
    """
    Классифицирует список изображений
    """
    results = []
    for img in images:
        preds = model.predict(img)
        decoded = decode_predictions(preds, top=3)[0]
        results.append(decoded)
    return results
