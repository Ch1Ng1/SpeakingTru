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
import re
import logging
import yfinance as yf

# Конфигурация на логване
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация на pygame за аудио
try:
    pygame.mixer.init()
except Exception as e:
    logger.error(f"Грешка при инициализация на pygame: {e}")

# API ключове (добавете вашите ако имате)
WEATHER_API_KEY = ""  # OpenWeatherMap API key (безплатен на openweathermap.org)
WOLFRAM_APP_ID = ""   # WolframAlpha App ID (безплатен на wolframalpha.com)

# Конфигурационни константи
ECHO_PREVENTION_DELAY = 3.5  # Секунди след говорене преди слушане
DUPLICATE_QUESTION_TIMEOUT = 10  # Секунди за игнориране на дублиран въпрос
POST_RESPONSE_DELAY = 4  # Секунди пауза след отговор
MICROPHONE_ENERGY_THRESHOLD = 500  # Чувствителност на микрофона
MAX_TEXT_LENGTH = 500  # Максимална дължина на текста за TTS
MAX_CONVERSATION_HISTORY = 100  # Максимален брой въпроси в историята

# История и памет
conversation_history = []
user_memory = {}  # Запазва важни неща за потребителя
MEMORY_FILE = "user_memory.json"
is_speaking = False  # Флаг дали KIKI говори в момента
last_speak_time = 0  # Последно време на говорене
last_question = ""  # Последен обработен въпрос
last_question_time = 0  # Време на последния въпрос

# Конфигурация на Wikipedia за български
wikipedia.set_lang("bg")

def load_memory():
    """Зарежда памет от файл"""
    global user_memory
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                user_memory = json.load(f)
                logger.info("Памет заредена успешно")
    except Exception as e:
        logger.error(f"Грешка при зареждане на памет: {e}")
        user_memory = {}

def save_memory():
    """Запазва памет във файл"""
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_memory, f, ensure_ascii=False, indent=2)
            logger.info("Памет запазена успешно")
    except Exception as e:
        logger.error(f"Грешка при запазване на памет: {e}")

def speak(text):
    """Изговаря текст на глас с Google TTS"""
    global is_speaking, last_speak_time
    
    if not text:
        return
    
    # Изчакваме ако все още говорим
    timeout = 0
    while is_speaking and timeout < 50:  # Максимум 5 секунди
        time.sleep(0.1)
        timeout += 1
    
    if is_speaking:
        logger.warning("Пропускане на speak() - все още говорим")
        return
    
    is_speaking = True
    
    # Почистваме текста от символи, които TTS не чете правилно
    text = re.sub(r'[<>«»*]', ', ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + "..."
    
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
        
        tts = gTTS(text=text, lang='bg', slow=False)
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # Допълнителна пауза след говорене
        time.sleep(0.5)
        
        pygame.mixer.music.unload()
        
        # Изчакваме малко преди да изтрием файла
        time.sleep(0.2)
        try:
            os.unlink(temp_file)
        except:
            pass
        
    except Exception as e:
        logger.error(f"Грешка при глас: {e}")
        print(f"❌ Грешка при глас: {e}")
    finally:
        is_speaking = False
        last_speak_time = time.time()  # Записваме кога сме спрели да говорим

def listen():
    """Слуша и разпознава реч"""
    global is_speaking, last_speak_time
    
    # Не слушаме докато KIKI говори
    if is_speaking:
        time.sleep(0.2)
        return ""
    
    # Изчакваме след като KIKI е спряла да говори
    # За да не улавяме ехото от високоговорителите
    time_since_speak = time.time() - last_speak_time
    if time_since_speak < ECHO_PREVENTION_DELAY:
        time.sleep(0.3)
        return ""
    
    recognizer = sr.Recognizer()
    # Увеличаваме energy_threshold за да не улавя ехо толкова лесно
    recognizer.energy_threshold = MICROPHONE_ENERGY_THRESHOLD
    recognizer.dynamic_energy_threshold = False
    
    with sr.Microphone() as source:
        # Не показваме съобщение ако говорим
        if not is_speaking:
            print("🎧 Слушам... (имате до 30 секунди)")
        
        try:
            # Проверка отново преди да започнем да слушаме
            if is_speaking:
                return ""
            
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            # Увеличаваме времената значително
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=60)
            
            # Проверка дали не сме започнали да говорим междувременно
            if is_speaking:
                logger.debug("Игнориране на аудио - KIKI говори")
                return ""
            
            print("✓ Разпознавам...")
            text = recognizer.recognize_google(audio, language="bg-BG")
            
            # Финална проверка
            if is_speaking:
                logger.debug("Игнориране на разпознат текст - KIKI говори")
                return ""
            
            print(f"👤 Вие: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            if not is_speaking:
                logger.warning("Микрофонът не улови нищо")
            return ""
        except sr.UnknownValueError:
            if not is_speaking:  # Не показваме грешка ако говорим
                print("⚠ Не разбрах какво казахте")
                logger.warning("Речта не е разпозната")
            return ""
        except Exception as e:
            if not is_speaking:
                logger.error(f"Грешка при слушане: {e}")
                print(f"❌ Грешка: {e}")
            return ""

def search_google(query):
    """Търси в Google"""
    if not query or len(query) < 2:
        return None
    
    try:
        search_url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Търсим featured snippet
        featured = soup.find('div', class_='BNeawe')
        if featured:
            text = featured.get_text().strip()
            if text and len(text) > 10:
                return text[:300]
        
        return "Намерих резултати, но не мога да ги обработя точно."
    except requests.Timeout:
        logger.warning("Google търсене изтекло време")
        return None
    except Exception as e:
        logger.error(f"Грешка при Google търсене: {e}")
        return None

def search_wikipedia(query):
    """Търси в Wikipedia"""
    if not query or len(query) < 2:
        return None
    
    try:
        result = wikipedia.summary(query, sentences=2)
        if result and len(result) > 10:
            return result[:400]
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:3] if e.options else []
        if options:
            return f"Има много резултати. Моля уточнете: {', '.join(options)}"
        return None
    except wikipedia.exceptions.PageError:
        logger.warning(f"Wikipedia страница не намерена: {query}")
        return None
    except Exception as e:
        logger.error(f"Wikipedia грешка: {e}")
        return None

def calculate(expression):
    """Изчислява математически изрази"""
    try:
        # Валидираме израза
        if not expression or not re.match(r'^[\d\s\+\-\*/\(\)\.]*$', expression):
            return None
        
        # Безопасно изчисление
        result = eval(expression, {"__builtins__": {}}, {})
        
        # Форматираме резултата
        if isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            else:
                return f"{result:.2f}"
        return str(result)
    except Exception as e:
        logger.warning(f"Грешка при изчисление: {e}")
        
        if WOLFRAM_APP_ID:
            try:
                client = wolframalpha.Client(WOLFRAM_APP_ID)
                res = client.query(expression)
                if res:
                    return next(res.results).text
            except Exception as e:
                logger.warning(f"WolframAlpha грешка: {e}")
        
        return None

def get_weather(city="Sofia"):
    """Получава информация за времето"""
    if not WEATHER_API_KEY:
        return "Нямам API ключ за времето. Посетете openweathermap.org за безплатен ключ."
    
    if not city or len(city) < 2:
        city = "Sofia"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=bg"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"В {city} е {temp}°C, {desc}."
        else:
            logger.warning(f"OpenWeatherMap грешка: {response.status_code}")
            return "Не мога да проверя времето в момента."
    except requests.Timeout:
        logger.warning("Времето изтекло време")
        return "Времето вземане е закъснело."
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP грешка при времето: {e}")
        return None
    except Exception as e:
        logger.error(f"Грешка при времето: {e}")
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

def get_stock_price(symbol):
    """Получава цена на акция в реално време"""
    try:
        # Добавяме .US за американски борси ако няма точка
        if '.' not in symbol:
            symbol = symbol.upper()
        
        stock = yf.Ticker(symbol)
        
        # Вземаме най-актуалната информация
        info = stock.info
        history = stock.history(period='1d')
        
        if history.empty:
            return f"Не намерих данни за {symbol}."
        
        current_price = history['Close'].iloc[-1]
        open_price = history['Open'].iloc[0]
        high = history['High'].max()
        low = history['Low'].min()
        
        # Изчисляваме промяна в проценти
        change = current_price - open_price
        change_percent = (change / open_price) * 100
        
        # Получаваме името на компанията
        company_name = info.get('shortName', symbol)
        
        result = f"{company_name}: {current_price:.2f} долара"
        
        if change >= 0:
            result += f", нагоре с {change_percent:.2f}%"
        else:
            result += f", надолу с {abs(change_percent):.2f}%"
        
        result += f". Най-висока: {high:.2f}, най-ниска: {low:.2f}."
        
        return result
    except Exception as e:
        logger.error(f"Грешка при борсови данни: {e}")
        return f"Не мога да получа информация за {symbol}. Проверете дали символът е правилен."

def get_crypto_price(crypto):
    """Получава цена на криптовалута"""
    try:
        # Криптовалутите в yfinance имат -USD суфикс
        crypto_upper = crypto.upper()
        if not crypto_upper.endswith('-USD'):
            crypto_upper = f"{crypto_upper}-USD"
        
        ticker = yf.Ticker(crypto_upper)
        history = ticker.history(period='1d')
        
        if history.empty:
            return f"Не намерих данни за {crypto}."
        
        current_price = history['Close'].iloc[-1]
        open_price = history['Open'].iloc[0]
        
        change = current_price - open_price
        change_percent = (change / open_price) * 100
        
        result = f"{crypto.upper()}: {current_price:.2f} долара"
        
        if change >= 0:
            result += f", нагоре с {change_percent:.2f}%"
        else:
            result += f", надолу с {abs(change_percent):.2f}%"
        
        return result
    except Exception as e:
        logger.error(f"Грешка при криптовалутни данни: {e}")
        return f"Не мога да получа информация за {crypto}."

def process_command(text):
    """Обработва специални команди"""
    if not text or len(text) < 2:
        return None
    
    text = text.lower().strip()
    
    # Калкулатор
    if any(word in text for word in ['колко е', 'изчисли', 'пресметни', '+', '-', '*', '/']):
        for word in ['колко е', 'изчисли', 'пресметни']:
            if word in text:
                expr = text.split(word)[-1].strip()
                # Заменяме български думи с операции
                expr = expr.replace('плюс', '+').replace('минус', '-')
                expr = expr.replace('по', '*').replace('делено на', '/')
                expr = expr.replace('умножено по', '*')
                expr = re.sub(r'[а-я]', '', expr)  # Премахваме случайни букви
                expr = expr.strip()
                
                if expr:
                    result = calculate(expr)
                    if result:
                        return f"Резултатът е {result}"
                break
    
    # Времето
    if 'какво е времето' in text or 'колко градуса' in text:
        city = "Sofia"
        # Проверяваме за конкретен град
        city_match = re.search(r'в\s+([а-я]+)', text)
        if city_match:
            city = city_match.group(1).capitalize()
        return get_weather(city)
    
    # Вицове
    if any(word in text for word in ['виц', 'разсмей', 'смешно']):
        return tell_joke()
    
    # Факти
    if any(word in text for word in ['факт', 'нещо интересно', 'интересен факт']):
        return get_fun_fact()
    
    # Злато и сребро
    if any(word in text for word in ['злато', 'gold', 'сребро', 'silver', 'метал']):
        precious_metals = {
            'злато': 'GC=F', 'gold': 'GC=F', 'голд': 'GC=F',
            'сребро': 'SI=F', 'silver': 'SI=F', 'силвър': 'SI=F',
        }
        
        found_metal = None
        for name, symbol in precious_metals.items():
            if name in text:
                found_metal = symbol
                break
        
        if found_metal:
            return get_stock_price(found_metal)
        else:
            return "Кажете ми кой благороден метал. Например: злато, сребро."
    
    # Борсови данни - акции
    if any(word in text for word in ['акция', 'акции', 'stock', 'борса', 'цена на']):
        # Популярни американски акции
        stock_symbols = {
            'apple': 'AAPL', 'епъл': 'AAPL', 'ейпъл': 'AAPL',
            'google': 'GOOGL', 'гугъл': 'GOOGL',
            'microsoft': 'MSFT', 'майкрософт': 'MSFT',
            'tesla': 'TSLA', 'тесла': 'TSLA',
            'amazon': 'AMZN', 'амазон': 'AMZN',
            'meta': 'META', 'facebook': 'META', 'фейсбук': 'META',
            'nvidia': 'NVDA', 'нвидия': 'NVDA',
            'netflix': 'NFLX', 'нетфликс': 'NFLX',
        }
        
        # Търсим за символ в текста
        found_symbol = None
        for name, symbol in stock_symbols.items():
            if name in text:
                found_symbol = symbol
                break
        
        # Или проверяваме за директен символ (напр. "AAPL")
        if not found_symbol:
            symbol_match = re.search(r'\b([A-Z]{1,5})\b', text.upper())
            if symbol_match:
                found_symbol = symbol_match.group(1)
        
        if found_symbol:
            return get_stock_price(found_symbol)
        else:
            return "Кажете ми символа или името на компанията. Например: Apple, Tesla, Microsoft."
    
    # Криптовалути
    if any(word in text for word in ['биткойн', 'bitcoin', 'криптовалута', 'крипто', 'ethereum', 'етериум']):
        crypto_names = {
            'bitcoin': 'BTC', 'биткойн': 'BTC', 'биткоин': 'BTC',
            'ethereum': 'ETH', 'етериум': 'ETH', 'етереум': 'ETH',
            'dogecoin': 'DOGE', 'dogе': 'DOGE', 'доге': 'DOGE',
            'cardano': 'ADA', 'кардано': 'ADA',
            'ripple': 'XRP', 'рипъл': 'XRP',
        }
        
        found_crypto = None
        for name, symbol in crypto_names.items():
            if name in text:
                found_crypto = symbol
                break
        
        if found_crypto:
            return get_crypto_price(found_crypto)
        else:
            return "Кажете ми коя криптовалута. Например: Bitcoin, Ethereum, Dogecoin."
    
    # Wikipedia търсене
    if any(word in text for word in ['какво е', 'кой е', 'коя е', 'какви']):
        for word in ['какво е', 'кой е', 'коя е', 'какви']:
            if word in text:
                query = text.split(word)[-1].strip()
                if query and len(query) > 2:
                    result = search_wikipedia(query)
                    if result:
                        return result
                break
    
    # Търсене в интернет
    if any(word in text for word in ['потърси', 'търси в интернет', 'google']):
        for word in ['потърси', 'търси в интернет', 'google']:
            if word in text:
                query = text.split(word)[-1].strip()
                if query and len(query) > 2:
                    result = search_google(query)
                    if result:
                        return result
                break
    
    # Запомняне на име
    if 'запомни' in text and 'име' in text:
        name_match = re.search(r'се\s+казвам\s+([а-яА-Я]+)', text)
        if not name_match:
            name_match = re.search(r'име\s+([а-яА-Я]+)', text)
        
        if name_match:
            name = name_match.group(1).capitalize()
            user_memory['name'] = name
            save_memory()
            return f"Запомних, че се казваш {name}!"
    
    # Запомняне на град
    if 'град' in text and any(word in text for word in ['живея', 'от', 'съм']):
        city_match = re.search(r'град\s+([а-яА-Я]+)|от\s+([а-яА-Я]+)', text)
        if city_match:
            city = city_match.group(1) or city_match.group(2)
            city = city.capitalize()
            user_memory['city'] = city
            save_memory()
            return f"Запомних, че си от {city}!"
    
    return None

def get_ai_response(user_message):
    """Генерира отговор базиран на вградени функции и прости диалози"""
    
    if not user_message:
        return None
    
    # Първо проверяваме за специални команди
    command_response = process_command(user_message)
    if command_response:
        return command_response
    
    # Добавяме в историята
    if len(conversation_history) < MAX_CONVERSATION_HISTORY:
        conversation_history.append(user_message)
    else:
        # Премахваме най-старата запис ако сме достигнали лимита
        conversation_history.pop(0)
        conversation_history.append(user_message)
    
    # Прости диалогови отговори
    text = user_message.lower().strip()
    
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
    if any(word in text for word in ['как се казваш', 'кое е твоето име', 'как ти е името']):
        return "Казвам се KIKI! Твоя AI асистент!"
    
    # Кой си
    if any(word in text for word in ['кой си', 'коя си', 'какво си', 'кой си ти']):
        return "Аз съм KIKI - твоят интелигентен асистент! Мога да изчислявам, проверявам времето, търся в Wikipedia и разказвам вицове!"
    
    # Колко е часът
    if any(word in text for word in ['колко е часът', 'колко часа', 'час']):
        now = datetime.now()
        return f"Часът е {now.strftime('%H:%M')}"
    
    # Каква е датата
    if any(word in text for word in ['каква е датата', 'какъв ден', 'кой ден', 'дата']):
        now = datetime.now()
        day_names = ["понеделник", "вторник", "сряда", "четвъртък", "петък", "събота", "неделя"]
        month_names = ["януари", "февруари", "март", "април", "май", "юни", "юли", "август", "септември", "октомври", "ноември", "декември"]
        
        day_name = day_names[now.weekday()]
        month_name = month_names[now.month - 1]
        return f"Днес е {day_name}, {now.day} {month_name} {now.year} година"
    
    # Благодаря
    if any(word in text for word in ['благодаря', 'мерси', 'thanks', 'спасибо']):
        responses = [
            "Няма защо! Винаги съм тук да помогна!",
            "С удоволствие! Ако имаш още въпроси, питай!",
            "Радвам се да помогна!",
        ]
        return random.choice(responses)
    
    # Помощ
    if any(word in text for word in ['помощ', 'какво можеш', 'способности', 'умееш']):
        return "Мога да: изчислявам математически izraзи, проверявам времето, проверявам борсови цени (акции, злато, сребро) и криптовалути, търся в Wikipedia и Google, разказвам вицове, споделям интересни факти и запомням неща за теб!"
    
    # Име на потребителя
    if user_memory.get('name'):
        name = user_memory['name']
        if any(word in text for word in ['какво е мое име', 'как се казвам', 'помниш ли го']):
            return f"Ты си {name}!"
        if any(word in text for word in ['аз', 'мое']):
            if random.random() > 0.7:  # 30% шанс да спомена няколко пъти
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
    print("   ✓ Борсови данни (Каква е цената на Apple акция?)")
    print("   ✓ Благородни метали (Колко струва златото?)")
    print("   ✓ Криптовалути (Колко струва Bitcoin?)")
    print("   ✓ Wikipedia (Какво е изкуствен интелект?)")
    print("   ✓ Вицове (Разкажи вицове!)")
    print("   ✓ Интересни факти (Кажи ми факт)")
    print("   ✓ Запомняне (Запомни че се казвам...)")
    print("   ✓ Разговор на български")
    print("\n🎤 Казвайте 'kiki' НАВСЯКЪДЕ във въпроса!")
    print("   Пример: 'Kiki, колко е часът?' или 'Колко е часът, kiki?'\n")
    print("💡 БЕЗ Ollama - работи с вградени функции!\n")
    
    # Зареждаме памет
    load_memory()
    if user_memory.get('name'):
        print(f"👤 Добре дошъл(а) обратно, {user_memory['name']}!\n")
    
    wake_word = "kiki"
    is_processing = False
    
    speak("Здравей! Аз съм Kiki! Слушам постоянно. Кажи ми името си навсякъде във въпроса!")
    
    # Калибриране
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🔧 Калибриране на микрофона...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
    except Exception as e:
        logger.error(f"Грешка при калибриране: {e}")
        print("❌ Проблем с микрофона")
        return
    
    try:
        global last_question, last_question_time
        
        while True:
            # Изчакваме ако KIKI говори
            if is_speaking:
                time.sleep(0.5)
                continue
            
            text = listen()
            
            if not text:
                continue
            
            # Команди за изход
            if any(word in text for word in ['стоп kiki', 'край kiki', 'довиждане kiki', 
                                             'изключи се kiki', 'стоп кики', 'край кики', 
                                             'довиждане', 'exit', 'quit']):
                speak("Довиждане! Беше ми приятно!")
                break
            
            # Вариации на wake word
            wake_words = ["kiki", "кики", "gourko", "гурко"]
            
            contains_wake = any(wake in text.lower() for wake in wake_words)
            
            if not contains_wake:
                logger.debug(f"Wake word не намерен в: {text[:50]}")
                continue
            
            # Премахваме wake word и обработваме въпроса
            question = text
            for wake in wake_words:
                question = question.replace(wake, ' ').replace(wake.capitalize(), ' ')
            
            question = re.sub(r'\s+', ' ', question).strip()
            question = question.rstrip(',').rstrip('.').strip()
            
            if not question or len(question) < 3:
                # Само казал "kiki" без въпрос или твърде кратък въпрос
                if not is_processing:
                    speak("Да, слушам те!")
                    # Кратка пауза след отговора
                    time.sleep(1)
                continue
            
            # Проверка за дублиран въпрос
            current_time = time.time()
            if question == last_question and (current_time - last_question_time) < DUPLICATE_QUESTION_TIMEOUT:
                logger.info(f"Игнориране на дублиран въпрос: {question}")
                print("⚠ Този въпрос вече е обработен.")
                time.sleep(1)
                continue
            
            # Проверка дали вече обработва въпрос
            if is_processing:
                print("⏳ Вече обработвам въпрос, моля изчакайте...")
                continue
            
            is_processing = True
            last_question = question
            last_question_time = current_time
            print(f"📝 Обработвам: {question}")
            try:
                response = get_ai_response(question)
                if response:
                    # Допълнителна проверка преди да говорим
                    if not is_speaking:
                        speak(response)
                        # Добавяме още пауза след отговора за пълно заглушаване на ехото
                        print("⏸ Пауза за избягване на ехо...")
                        time.sleep(POST_RESPONSE_DELAY)
                    else:
                        logger.warning("Пропускане на отговор - все още говорим")
            except Exception as e:
                logger.error(f"Грешка при обработка: {e}")
                if not is_speaking:
                    speak("Извинете, възникна грешка.")
                    time.sleep(2.5)
            finally:
                is_processing = False
    
    except KeyboardInterrupt:
        print("\n👋 Програмата е спряна.")
        speak("Довиждане!")
    except Exception as e:
        logger.error(f"Критична грешка: {e}")
        print(f"❌ Критична грешка: {e}")
    finally:
        pygame.mixer.quit()
        save_memory()

if __name__ == "__main__":
    main()
