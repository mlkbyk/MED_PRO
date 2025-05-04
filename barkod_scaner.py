import cv2 as cv
from pyzbar import pyzbar
import os
import pygame
import json

# Load medicine database (barkod1, barkod2)
with open('medicine.json', 'r', encoding='utf-8') as file:
    medicines = json.load(file)

# Initialize pygame for sound
pygame.mixer.init()

# Sound file path
sound_path = r"C:\Users\MS\Downloads\effect.mp3"

# Start webcam
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

# To store already detected barcodes
found_barcodes = set()

print("[INFO] Camera is running, waiting for QR/Barcode...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Frame capture failed.")
        break

    # Convert to grayscale
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Reduce noise and improve barcode clarity
    gray = cv.GaussianBlur(gray, (5, 5), 0)
    thresh = cv.adaptiveThreshold(gray, 255,
                                  cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv.THRESH_BINARY, 11, 2)

    # Decode barcodes
    barcodes = pyzbar.decode(thresh)

    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8").strip()
        barcode_type = barcode.type

        if barcode_data in found_barcodes:
            continue

        found_barcodes.add(barcode_data)

        # Search for matching medicine
        matched_medicine = None
        for medicine in medicines.values():
            if barcode_data == medicine.get('barkod1') or barcode_data == medicine.get('barkod2'):
                matched_medicine = medicine
                break

        if matched_medicine:
            print(f"[✅] Medicine found: {matched_medicine['name']} (Barcode: {barcode_data})")
        else:
            print(f"[ℹ️] Unknown barcode: {barcode_data}")

        # Play sound only if a medicine is matched
        if matched_medicine and os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()

    # Display camera feed
    cv.imshow("Camera View", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv.destroyAllWindows()
