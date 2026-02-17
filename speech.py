import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
import os
import time
import re
import logging

logger = logging.getLogger(__name__)

class SpeechHandler:
    def __init__(self, config):
        self.config = config
        self.is_speaking = False
        self.last_speak_time = 0
        try:
            pygame.mixer.init()
        except Exception as e:
            logger.error(f"Грешка при инициализация на pygame: {e}")

    def speak(self, text):
        """Изговаря текст на глас с Google TTS"""
        if not text:
            return

        # Изчакваме ако все още говорим
        timeout = 0
        while self.is_speaking and timeout < 50:  # Максимум 5 секунди
            time.sleep(0.1)
            timeout += 1

        if self.is_speaking:
            logger.warning("Пропускане на speak() - все още говорим")
            return

        self.is_speaking = True

        # Почистваме текста от символи, които TTS не чете правилно
        text = re.sub(r'[<>«»*]', ', ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) > self.config['settings']['max_text_length']:
            text = text[:self.config['settings']['max_text_length'] + "..."

        print(f"🤖 KIKI: {text}")
        try:
            # Спираме и изчакваме всяко текущо възпроизвеждане
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                time.sleep(0.3)

            # Освобождаваме ресурсите
            try:
                pygame.mixer.music.unload()
            except:
                pass

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name

            try:
                tts = gTTS(text=text, lang=self.config['settings']['language'], slow=False)
                tts.save(temp_file)

                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                # Допълнителна пауза след говорене
                time.sleep(0.5)

            finally:
                # Спираме музиката и освобождаваме ресурсите
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                except:
                    pass

                # Изтриваме временния файл
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass  # Файлът може вече да е изтрит

        except Exception as e:
            logger.error(f"Грешка при глас: {e}")
            print(f"❌ Грешка при глас: {e}")
        finally:
            self.is_speaking = False
            self.last_speak_time = time.time()  # Записваме кога сме спрели да говорим

    def listen(self):
        """Слуша и разпознава реч"""
        # Не слушаме докато KIKI говори
        if self.is_speaking:
            time.sleep(0.2)
            return ""

        # Изчакваме след като KIKI е спряла да говори
        # За да не улавяме ехото от високоговорителите
        time_since_speak = time.time() - self.last_speak_time
        if time_since_speak < self.config['settings']['echo_prevention_delay']:
            time.sleep(0.3)
            return ""

        recognizer = sr.Recognizer()
        # Увеличаваме energy_threshold за да не улавя ехо толкова лесно
        recognizer.energy_threshold = self.config['settings']['microphone_energy_threshold']
        recognizer.dynamic_energy_threshold = False

        with sr.Microphone() as source:
            # Не показваме съобщение ако говорим
            if not self.is_speaking:
                print("🎧 Слушам... (имате до 30 секунди)")

            try:
                # Проверка отново преди да започнем да слушаме
                if self.is_speaking:
                    return ""

                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                # Увеличаваме времената значително
                audio = recognizer.listen(source, timeout=30, phrase_time_limit=60)

                # Проверка дали не сме започнали да говорим междувременно
                if self.is_speaking:
                    logger.debug("Игнориране на аудио - KIKI говори")
                    return ""

                print("✓ Разпознавам...")
                text = recognizer.recognize_google(audio, language=self.config['settings']['speech_recognition_language'])

                # Финална проверка
                if self.is_speaking:
                    logger.debug("Игнориране на разпознат текст - KIKI говори")
                    return ""

                print(f"👤 Вие: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                if not self.is_speaking:
                    logger.warning("Микрофонът не улови нищо")
                return ""
            except sr.UnknownValueError:
                if not self.is_speaking:  # Не показваме грешка ако говорим
                    print("⚠ Не разбрах какво казахте")
                    logger.warning("Речта не е разпозната")
                return ""
            except Exception as e:
                if not self.is_speaking:
                    logger.error(f"Грешка при слушане: {e}")
                    print(f"❌ Грешка: {e}")
                return ""