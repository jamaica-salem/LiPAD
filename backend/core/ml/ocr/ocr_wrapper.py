from paddleocr import PaddleOCR
import numpy as np
import os

_ocr = None

def load_ocr():
    global _ocr

    #custom_rec_model_dir = os.path.abspath("C:\\Thesis\\LiPAD Webapp\\LiPAD\\backend\\core\\ml\\ocr\\weights")
    _ocr = PaddleOCR(use_angle_cls=True, lang='en')

def run_ocr(pil_img):
    if _ocr is None:
        raise ValueError('OCR model is not loaded. Call load_ocr() first.')
    img_array = np.array(pil_img)
    return _ocr.ocr(img_array, cls=True)