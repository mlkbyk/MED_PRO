import speech_recognition as sr
import json
from rapidfuzz import fuzz
import webbrowser
import time
import pygame  # Pygame kütüphanesini import et6

# Ses dosyalarının yolları
giris_sesi_yolu = "C:\\Users\\MS\\Downloads\\hangi_ilac.mp3"
anlasilmadi_sesi_yolu = "C:\\Users\\MS\\Downloads\\üzgünüm.mp3"
tekrar_soyleyin_sesi_yolu = "C:\\Users\\MS\\Downloads\\tekrar.mp3"  # Yeni ses dosyası

# İlaç sayfalarınızın yolları
parol_path = 'D:/medicine-project/parol_expo.html'
aferin_path = 'D:/medicine-project/aferin_expo.html'
klamoks_path = 'D:/medicine-project/klamoksbıd.html'
contractubex_path = 'D:/medicine-project/contractubex.html'

# İlaçları ve yollarını bir sözlükte toplayalım
medicine_paths = {
    "Parol": parol_path,
    "A-ferin": aferin_path,
    "Klamoks BID": klamoks_path,
    "Contractubex": contractubex_path
}

# JSON dosyasından ilaç verilerini yükle
try:
    with open('medicine.json', 'r', encoding='utf-8') as file:
        medicines = json.load(file)
except FileNotFoundError:
    print("❌ 'medicine.json' dosyası bulunamadı.")
    exit()
except json.JSONDecodeError:
    print("❌ 'medicine.json' dosyası geçerli bir JSON formatında değil.")
    exit()


# Pygame başlatma ve ses yükleme fonksiyonu
def play_sound(sound_path):
    try:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(sound_path)
        sound.play()
        while pygame.mixer.get_busy():  # Ses çalarken bekle
            pygame.time.delay(100)
        pygame.mixer.quit()
    except pygame.error as e:
        print(f"❌ Ses dosyası çalınırken bir hata oluştu: {e}")
    except FileNotFoundError:
        print(f"❌ Ses dosyası bulunamadı: {sound_path}")


# Fuzzy string matching (benzerlik hesaplama)
def clean_ocr_text(text):
    return text.strip().lower()


def fuzzy_similarity(str1, str2):
    return fuzz.ratio(clean_ocr_text(str1), clean_ocr_text(str2))


# İlaçları JSON ile eşleştiren fonksiyon (cümle içinden ilaç adı bulmaya yönelik)
def find_best_matching_medicine_in_sentence(spoken_text, medicines, threshold=70):
    best_match = None
    best_score = 0
    spoken_words = clean_ocr_text(spoken_text).split()

    for medicine in medicines.values():
        medicine_name = clean_ocr_text(medicine.get('name', ''))
        for word in spoken_words:
            score = fuzzy_similarity(word, medicine_name)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = medicine
                break  # Bir kelime eşleşirse diğer kelimelere bakmaya gerek yok (şimdilik)
        if best_match:
            break

    return best_match


# Sesli komutla ilaç adını tanıma
recognizer = sr.Recognizer()


def listen_for_medicine():
    with sr.Microphone() as source:
        print("🎤 Dinliyorum...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, phrase_time_limit=5)  # 5 saniye dinleme süresi
            print("🎤 Tanımlanıyor...")
            command = recognizer.recognize_google(audio, language="tr-TR")  # Türkçe için "tr-TR"
            print(f"🎤 Duyulan: {command}")
            return command.lower()
        except sr.UnknownValueError:
            play_sound(anlasilmadi_sesi_yolu)  # Anlaşılamadı sesini çal (üzgünüm.mp3)
            print("❌ Üzgünüm, ne dediğinizi anlayamadım.")
            return None
        except sr.RequestError as e:
            print(f"❌ İstek hatası oluştu; internet bağlantınızı kontrol edin: {e}")
            return None
        except sr.WaitTimeoutError:
            play_sound(tekrar_soyleyin_sesi_yolu)  # Zaman aşımı olduysa tekrar söyleyin sesini çal
            print("❌ Ses algılanamadı. Lütfen ilacın adını tekrar söyleyin.")
            return None
        except Exception as e:
            print(f"❌ Beklenmeyen bir hata oluştu: {e}")
            return None


# Sürekli dinleme ve ilaç arama fonksiyonu (cümle içinden arama yapacak şekilde güncellendi)
def continuously_search_medicine_by_voice():
    play_sound(giris_sesi_yolu)  # Giriş sesini çal
    print("🔊 Sürekli dinleme başlatıldı. Çıkmak için 'çık' deyin.")
    while True:
        command = listen_for_medicine()

        if command:
            if "çık" in command:
                print("🛑 Dinleme sonlandırıldı.")
                break

            best_match = find_best_matching_medicine_in_sentence(command, medicines)

            if best_match:
                medicine_name = best_match['name'].strip()
                print(f"✅ Eşleşen ilaç bulundu: {medicine_name} | Barkod: {best_match['barkod1']}")

                if medicine_name in medicine_paths:
                    webbrowser.open(f'file:///{medicine_paths[medicine_name]}')
                    print(f"🌐 {medicine_name} için web sayfası açılıyor...")
                else:
                    print(f"⚠️ {medicine_name} için web sayfası yolu tanımlanmamış.")
            else:
                print(f"❌ '{command}' içinde eşleşen bir ilaç bulunamadı.")
        # Kısa bir bekleme süresi ekleyelim, böylece sürekli işlem yapmaz
        time.sleep(0.5)

# Sürekli dinleme ve ilaç arama başlatma
if __name__ == "__main__":
    pygame.init()  # Pygame'i başlat
    continuously_search_medicine_by_voice()
    pygame.quit()  # Pygame'i kapat
