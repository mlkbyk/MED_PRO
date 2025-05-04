import easyocr
import cv2
import pygame
import time
import json
import re
from rapidfuzz import fuzz
import webbrowser

parol_path='D:/medicine-project/parol_expo.html'
aferin_path='D:/medicine-project/aferin_expo.html'
klamoks_path='D:/medicine-project/klamoksbıd.html'
contractubex_path='D:/medicine-project/contractubex.html'

# Load the JSON file with UTF-8 encoding
with open('medicine.json', 'r', encoding='utf-8') as file:
    medicines = json.load(file)


# Function to clean OCR text (lowercase, remove common units)
def clean_ocr_text(text):
    cleaned_text = text.strip().lower()
    cleaned_text = re.sub(r'\b(mg|tablet|capsule|cap|box|bottle|ml)\b', '', cleaned_text)
    return cleaned_text.strip()


# Use fuzzy string matching to calculate similarity percentage
def fuzzy_similarity(str1, str2):
    return fuzz.ratio(clean_ocr_text(str1), clean_ocr_text(str2))

def find_drugs(found_text, medicines, threshold=70):
    best_match = None
    best_score = 0

    for medicine in medicines.values():
        name = medicine.get('name', '')
        score = fuzzy_similarity(found_text, name)  # fuzzy instead of word match

        if score > best_score and score >= threshold:
            best_score = score
            best_match = medicine

    return best_match, best_score


# === Sound setup ===
pygame.mixer.init()
sound_path = r"C:\Users\MS\Downloads\effect.mp3"  # Path to your sound file

# === Start camera ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 940)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# === Initialize OCR reader ===
reader = easyocr.Reader(['en'], gpu=False)

found_drugs = set()  # Set to keep track of detected medicines
print("Camera is open...")

last_ocr_time = 0
ocr_interval = 2  # Time between OCR scans (in seconds)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    if current_time - last_ocr_time > ocr_interval:
        results = reader.readtext(frame)
        last_ocr_time = current_time

        for (bbox, text, prob) in results:
            if prob > 0.5:
                cleaned_text = text.strip().upper()
                if cleaned_text not in found_drugs:
                    found_drugs.add(cleaned_text)
                    print(f"🧾 Detected: {cleaned_text}")

                    # Try to find a matching medicine
                    matching_medicine, similarity = find_drugs(cleaned_text, medicines)
                    if matching_medicine:
                        print(
                            f"✅ Match found: {matching_medicine['name']} | Barcode: {matching_medicine['barkod1']} | Similarity: {similarity:.2f}%")

                        if matching_medicine['name'] == "Parol":
                            webbrowser.open(f'file:///{parol_path}')
                            print(f"📄 Web path: {parol_path}")
                        elif matching_medicine['name'].strip() == "A-ferin":
                            webbrowser.open(f'file:///{aferin_path}')
                            print(f"📄 Web path: {aferin_path}")
                        elif matching_medicine['name'] == "Contractubex":
                            webbrowser.open(f'file:///{contractubex_path}')
                            print(f"📄 Web path: {contractubex_path}")
                        elif matching_medicine['name'] == "Klamoks BID":
                            webbrowser.open(f'file:///{klamoks_path}')  # ← düzeltildi
                            print(f"📄 Web path: {klamoks_path}")

                        # Play sound only if match is found
                        pygame.mixer.music.load(sound_path)
                        pygame.mixer.music.play()

                        # Play sound only if match is found
                        pygame.mixer.music.load(sound_path)
                        pygame.mixer.music.play()

    # Optional display
    cv2.imshow("OCR Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
