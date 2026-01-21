import speech_recognition as sr
from gtts import gTTS
import pygame
import requests
import json
import os
import tempfile
import time
from datetime import datetime
import wikipedia
import wolframalpha
from bs4 import BeautifulSoup
import random

# Инициализация на pygame за аудио
pygame.mixer.init()

# API ключове (добавете вашите ако имате)
WEATHER_API_KEY = ""  # OpenWeatherMap API key (безплатен на openweathermap.org)
WOLFRAM_APP_ID = ""   # WolframAlpha App ID (безплатен на wolframalpha.com)

# История и памет
conversation_history = []
user_memory = {}  # Запазва важни неща за потребителя

# Конфигурация на Wikipedia за български
wikipedia.set_lang("bg")

def speak(text):
    """Изговаря текст на глас с Google TTS"""
    # Почистваме текста от символи, които TTS не чете правилно
    text = text.replace('>', ', ').replace('<', ', ')
    text = text.replace('  ', ' ').strip()
    
    print(f"🤖 KIKI: {text}")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name
        
        tts = gTTS(text=text, lang='bg', slow=False)
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.music.unload()
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Грешка при глас: {e}")

def listen():
    """Слуша и разпознава реч"""
    recognizer = sr.Recognizer()
    # Намаляваме energy_threshold за по-добра чувствителност
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = False
    
    with sr.Microphone() as source:
        print("🎧 Слушам... (имате до 30 секунди)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Увеличаваме времената значително
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=60)
            print("✓ Разпознавам...")
            text = recognizer.recognize_google(audio, language="bg-BG")
            print(f"👤 Вие: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("⚠ Не разбрах какво казахте")
            return ""
        except Exception as e:
            print(f"❌ Грешка: {e}")
            return ""

def search_google(query):
    """Търси в Google"""
    try:
        search_url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Търсим featured snippet
        featured = soup.find('div', class_='BNeawe')
        if featured:
            return featured.get_text()
        
        return "Намерих резултати, но не мога да ги обработя."
    except Exception as e:
        print(f"❌ Грешка при търсене: {e}")
        return None

def search_wikipedia(query):
    """Търси в Wikipedia"""
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Има много резултати. Моля уточнете: {', '.join(e.options[:3])}"
    except wikipedia.exceptions.PageError:
        return None
    except Exception as e:
        print(f"❌ Wikipedia грешка: {e}")
        return None

def calculate(expression):
    """Изчислява математически изрази"""
    try:
        # Безопасно изчисление
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except:
        if WOLFRAM_APP_ID:
            try:
                client = wolframalpha.Client(WOLFRAM_APP_ID)
                res = client.query(expression)
                return next(res.results).text
            except:
                pass
        return None

def get_weather(city="Sofia"):
    """Получава информация за времето"""
    if not WEATHER_API_KEY:
        return "Нямам API ключ за времето. Посетете openweathermap.org за безплатен ключ."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=bg"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"В {city} е {temp}°C, {desc}."
        else:
            return "Не мога да проверя времето в момента."
    except Exception as e:
        print(f"❌ Грешка при времето: {e}")
        return None

def tell_joke():
    """Разказва вицове на български"""
    jokes = [
        "Защо компютърът отиде при доктора? Защото имаше вирус!",
        "Как AI пие кафе? С много байтове!",
        "Защо роботът беше тъжен? Защото му липсваше хард драйв!",
        "Какво каза нулата на осмицата? Хубав колан имаш!",
        "Защо програмистите бъркат Коледа с Хелоуин? Защото 25 dec е равно на 31 oct!",
    ]
    return random.choice(jokes)

def get_fun_fact():
    """Споделя интересен факт"""
    facts = [
        "Мравките никога не спят!",
        "Банановото дърво всъщност е трева, не дърво.",
        "Медузите съществуват преди динозаврите.",
        "В Исландия няма комари.",
        "Светлината от слънцето пътува до Земята около 8 минути.",
        "Златните рибки могат да различават цветове.",
    ]
    return random.choice(facts)

def process_command(text):
    """Обработва специални команди"""
    text = text.lower()
    
    # Калкулатор
    if any(word in text for word in ['колко е', 'изчисли', 'пресметни', '+', '-', '*', '/']):
        # Извличаме математическия израз
        for word in ['колко е', 'изчисли', 'пресметни']:
            if word in text:
                expr = text.split(word)[-1].strip()
                # Заменяме български думи с операции
                expr = expr.replace('плюс', '+').replace('минус', '-')
                expr = expr.replace('по', '*').replace('делено на', '/')
                expr = expr.replace('умножено по', '*')
                result = calculate(expr)
                if result:
                    return f"Резултатът е {result}"
    
    # Времето
    if 'какво е времето' in text or 'колко градуса' in text:
        city = "Sofia"
        if 'в' in text:
            words = text.split('в')
            if len(words) > 1:
                city = words[1].strip().split()[0].capitalize()
        return get_weather(city)
    
    # Вицове
    if 'виц' in text or 'разсмей' in text or 'смешно' in text:
        return tell_joke()
    
    # Факти
    if 'факт' in text or 'кажи ми нещо интересно' in text:
        return get_fun_fact()
    
    # Wikipedia търсене
    if 'какво е' in text or 'кой е' in text or 'коя е' in text:
        query = text.replace('какво е', '').replace('кой е', '').replace('коя е', '').strip()
        if query:
            result = search_wikipedia(query)
            if result:
                return result
    
    # Търсене в интернет
    if 'потърси' in text or 'търси в интернет' in text:
        query = text.replace('потърси', '').replace('търси в интернет', '').strip()
        if query:
            result = search_google(query)
            if result:
                return result
    
    # Запомняне
    if 'запомни че' in text or 'моят' in text and ('име' in text or 'град' in text):
        if 'име' in text:
            name = text.split('име')[-1].strip().split()[0]
            user_memory['name'] = name
            return f"Запомних, че се казваш {name}!"
        if 'град' in text:
            city = text.split('град')[-1].strip().split()[0]
            user_memory['city'] = city
            return f"Запомних, че си от {city}!"
    
    return None

def get_ai_response(user_message):
    """Генерира отговор базиран на вградени функции и прости диалози"""
    
    # Първо проверяваме за специални команди
    command_response = process_command(user_message)
    if command_response:
        return command_response
    
    # Добавяме в историята
    conversation_history.append(user_message)
    
    # Прости диалогови отговори
    text = user_message.lower()
    
    # Поздрави
    if any(word in text for word in ['здравей', 'здрасти', 'хей', 'добър ден', 'добро утро', 'добър вечер']):
        responses = [
            "Здравей! Как мога да ти помогна?",
            "Здрасти! Какво искаш да научиш?",
            "Здравей! Радвам се да те чуя!",
        ]
        return random.choice(responses)
    
    # Как си
    if any(word in text for word in ['как си', 'как е', 'как се чувстваш']):
        responses = [
            "Страхотно съм! Готова да ти помогна!",
            "Отлично! Благодаря, че питаш! Как мога да помогна?",
            "Чувствам се супер! А ти как си?",
        ]
        return random.choice(responses)
    
    # Името
    if 'как се казваш' in text or 'кое е твоето име' in text or 'как ти е името' in text:
        return "Казвам се KIKI! Твоя AI асистент!"
    
    # Кой си
    if 'кой си' in text or 'коя си' in text or 'какво си' in text:
        return "Аз съм KIKI - твоят интелигентен асистент! Мога да изчислявам, проверявам времето, търся в Wikipedia и разказвам вицове!"
    
    # Колко е часът
    if 'колко е часът' in text or 'колко часа' in text or 'час' in text:
        now = datetime.now()
        return f"Часът е {now.strftime('%H:%M')}"
    
    # Каква е датата
    if 'каква е датата' in text or 'какъв ден' in text or 'кой ден' in text:
        now = datetime.now()
        day_name = ["понеделник", "вторник", "сряда", "четвъртък", "петък", "събота", "неделя"][now.weekday()]
        month_names = ["януари", "февруари", "март", "април", "май", "юни", "юли", "август", "септември", "октомври", "ноември", "декември"]
        month_name = month_names[now.month - 1]
        return f"Днес е {day_name}, {now.day} {month_name} {now.year} година"
    
    # Благодаря
    if 'благодаря' in text or 'мерси' in text or 'thanks' in text:
        responses = [
            "Няма защо! Винаги съм тук да помогна!",
            "С удоволствие! Ако имаш още въпроси, питай!",
            "Радвам се да помогна!",
        ]
        return random.choice(responses)
    
    # Помощ
    if 'помощ' in text or 'какво можеш' in text or 'способности' in text:
        return "Мога да: изчислявам математически изрази, проверявам времето, търся в Wikipedia, разказвам вицове, споделям интересни факти и запомням неща за теб!"
    
    # Име на потребителя
    if user_memory.get('name') and ('аз' in text or 'ме' in text):
        name = user_memory['name']
        return f"Знам че се казваш {name}!"
    
    # Ако не е намерено съвпадение, даваме общ отговор
    generic_responses = [
        "Интересен въпрос! За съжаление не мога да отговоря точно. Опитай да попиташ за времето, факти или изчисления!",
        "Не съм сигурна как да отговоря на това. Мога да ти помогна с математика, времето или Wikipedia търсения!",
        "Хм, това е извън моите способности. Попитай ме за време, факти, изчисления или вицове!",
        "Не разбрах точно. Опитай: 'Какво е времето?', 'Колко е 5+3?' или 'Кажи ми факт'",
    ]
    
    return random.choice(generic_responses)

def main():
    """Главна функция"""
    print("=" * 60)
    print("🚀 KIKI - AI асистент с много способности!")
    print("=" * 60)
    print("\n📋 Какво мога да правя:")
    print("   ✓ Изчисления (Колко е 15 * 7?)")
    print("   ✓ Времето (Какво е времето?)")
    print("   ✓ Wikipedia (Какво е изкуствен интелект?)")
    print("   ✓ Вицове (Разкажи вицове!)")
    print("   ✓ Интересни факти (Кажи ми факт)")
    print("   ✓ Запомняне (Запомни че се казвам...)")
    print("   ✓ Разговор на български")
    print("\n🎤 Казвайте 'kiki' НАВСЯКЪДЕ във въпроса!")
    print("   Пример: 'Kiki, колко е часът?' или 'Колко е часът, kiki?'\n")
    print("💡 БЕЗ Ollama - работи с вградени функции!\n")
    
    wake_word = "kiki"
    is_processing = False
    
    speak("Здравей! Аз съм Kiki! Слушам постоянно. Кажи ми името си навсякъде във въпроса!")
    
    # Калибриране
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🔧 Калибриране на микрофона...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    try:
        while True:
            text = listen()
            
            if not text:
                continue
            
            # Команди за изход
            if any(word in text for word in ['стоп kiki', 'край kiki', 'довиждане kiki', 'изключи се kiki', 'стоп кики', 'край кики']):
                speak("Довиждане! Беше ми приятно!")
                break
            
            # Проверяваме дали "kiki" е НАВСЯКЪДЕ в изречението
            wake_words = ["kiki", "кики"]
            
            # Проверяваме дали текстът съдържа някоя от вариациите
            contains_wake = False
            question = text
            
            for wake in wake_words:
                if wake in text.lower():
                    contains_wake = True
                    print(f"✓ Намерих '{wake}' във въпроса")
                    # Премахваме wake word и обработваме въпроса
                    question = text.replace(wake, '').replace(wake.capitalize(), '').strip()
                    question = question.rstrip(',').rstrip('.').strip()
                    break
            
            if not contains_wake:
                print(f"⚠ Не намерих 'kiki' в: {text[:50]}...")
            
            if contains_wake:
                # Проверка дали вече обработва въпрос
                if is_processing:
                    print("⏳ Вече обработвам въпрос, моля изчакайте...")
                    speak("Моля изчакайте, обработвам предишния въпрос.")
                    continue
                
                if question:
                    is_processing = True  # Маркираме че започваме обработка
                    print(f"📝 Обработвам: {question}")
                    try:
                        response = get_ai_response(question)
                        speak(response)
                    finally:
                        is_processing = False  # Освобождаваме след завършване
                else:
                    if not is_processing:
                        speak("Да, слушам те!")
                continue
            
            # Ако не съдържа "миранда", игнорираме
    
    except KeyboardInterrupt:
        print("\n👋 Програмата е спряна.")
        speak("Довиждане!")
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    main()
