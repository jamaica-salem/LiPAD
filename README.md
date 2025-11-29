# 🚗 LiPAD – License Plate Advanced Deblurrer

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.12-orange)](https://www.tensorflow.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1-red)](https://pytorch.org/)

**LiPAD** is an **AI-powered web application** for real-time **deblurring and analysis of vehicle license plate images**. It leverages a **CNN, GAN, and CRNN** pipeline to deliver **high-fidelity restoration** and **fast OCR recognition**, reducing manual correction time by up to 80%.  

---

## 🧠 Project Overview

This project tackles the challenge of reading blurred license plate images caused by **low light, motion, or poor quality**. LiPAD integrates **deep learning models** into a single pipeline:

- **CNN (Convolutional Neural Network)** – Automatically classifies the type of distortion.  
- **GAN (Generative Adversarial Network)** – Restores blurred images based on distortion type.  
- **CRNN (Convolutional Recurrent Neural Network)** – Extracts license plate characters after restoration.  

**Performance Highlights:**

- ✅ **94%+ recognition accuracy** on blurred license plate images.  
- ⏱️ Processes images **in less than 3 seconds on average**.  
- 🔧 Reduces manual image correction by **80%**.

---

## 🖥️ User Flow

1. **Upload Image**: Provide a blurred license plate image.  
2. **Choose Classification Method**:
   - **Automatic**: CNN predicts the distortion type.  
   - **Manual**: Users select the distortion type:
     - Low Light  
     - Low Quality  
     - Horizontally Blurred  
     - Vertically Blurred  
3. **Image Restoration**: GAN restores the license plate based on distortion type.  
4. **OCR Extraction**: CRNN extracts characters from the deblurred image.  
5. **Results Displayed**: View the restored image and extracted license plate characters.

---

## ⚡ Features

- 🚀 **Real-time processing** for fast license plate restoration.  
- ⏱️ **Average processing time < 3 seconds** per image.  
- 🤖 **Automatic and manual classification** for flexibility.  
- ✨ **High-fidelity GAN restoration** for blurred images.  
- 📝 **OCR-based character extraction** using CRNN.  
- 📊 **End-to-end pipeline integration** for seamless processing.  
- 📈 **Accuracy & Efficiency**:
  - 94%+ OCR recognition accuracy.  
  - Up to 80% reduction in manual image correction time.

---

## 🛠️ Technologies Used

- **Frontend:** Vue, TailwindCSS, TypeScript  
- **Backend:** Python, Django REST Framework 
- **Machine Learning:** TensorFlow, PyTorch  
- **Neural Networks:** CNN (Distortion Classifier), GAN (Deblurring), CRNN (OCR)  

---

## 🌟 Project Highlights

- **Exploratory Data Analysis (EDA)**: Prepared and cleaned license plate datasets.  
- **End-to-End Pipeline**: Integrated three deep learning models for seamless processing.  
- **Flexible Classification**: Manual override of automatic distortion detection.  
- **Speed & Accuracy**: Processes images **in < 3 seconds** with high OCR accuracy.  

---

## 🚀 How to Use

1. Open the web app.  
2. Upload a blurred license plate image.  
3. Select **Automatic** or **Manual** classification.  
4. Wait for GAN to restore the image.  
5. View the deblurred license plate and OCR results.  

---

## 📝 Future Improvements

- Batch image processing support.  
- OCR for **multi-country license plates**.  
- Enhance GAN models for **more extreme blur types**.  

---


**LiPAD Team** | AI-Powered License Plate Restoration 🚗🤖
