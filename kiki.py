import json
import time
import logging
from speech import SpeechHandler
from api import APIHandler
from memory import MemoryHandler
from utils import calculate, get_current_time, get_joke, get_fact

# Конфигурация на логване
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KIKI:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.speech = SpeechHandler(self.config)
        self.api = APIHandler(self.config)
        self.memory = MemoryHandler(self.config)

        self.conversation_history = []
        self.last_question = ""
        self.last_question_time = 0

    def process_command(self, text):
        """Обработва команда и връща отговор"""
        if not text:
            return ""

        # Проверка за дублирани въпроси
        current_time = time.time()
        if text == self.last_question and current_time - self.last_question_time < self.config['settings']['duplicate_question_timeout']:
            return "Вече отговорих на този въпрос наскоро."

        self.last_question = text
        self.last_question_time = current_time

        # Добавяме към историята
        self.conversation_history.append(text)
        if len(self.conversation_history) > self.config['settings']['max_conversation_history']:
            self.conversation_history.pop(0)

        # Обработка на команди
        text_lower = text.lower()

        # Калкулатор
        if any(word in text_lower for word in ['изчисли', 'пресметни', 'колко е', 'колко са']):
            expr = re.search(r'(\d+(?:\.\d+)?(?:\s*[\+\-\*/\^]\s*\d+(?:\.\d+)?)+)', text)
            if expr:
                result = calculate(expr.group(1))
                if result:
                    return f"Резултатът е {result}"

        # Време
        if 'време' in text_lower or 'температура' in text_lower:
            city = "София"  # По подразбиране
            # Опитваме да извлечем град
            words = text.split()
            for word in words:
                if word[0].isupper():  # Вероятно име на град
                    city = word
                    break
            return self.api.get_weather(city)

        # Дата и час
        if any(word in text_lower for word in ['ден', 'дата', 'час', 'време е']):
            return get_current_time()

        # Wikipedia
        if any(word in text_lower for word in ['какво е', 'кой е', 'какво знаеш за']):
            query = text.replace('kiki', '').replace('гурко', '').strip()
            result = self.api.search_wikipedia(query)
            if result:
                return result

        # Google търсене
        if 'потърси' in text_lower or 'намери' in text_lower:
            query = text.replace('kiki', '').replace('гурко', '').strip()
            result = self.api.search_google(query)
            if result:
                return result

        # Акции
        if 'акция' in text_lower or 'цена' in text_lower:
            # Опитваме да извлечем символ
            words = text.split()
            for word in words:
                if word.isupper() and len(word) <= 5:  # Вероятно тикер
                    return self.api.get_stock_price(word)
            # Ако няма символ, питаме
            return "Коя акция искате да проверя?"

        # Крипто
        if any(crypto in text_lower for crypto in ['bitcoin', 'btc', 'ethereum', 'eth', 'dogecoin']):
            if 'bitcoin' in text_lower or 'btc' in text_lower:
                return self.api.get_crypto_price('BTC')
            elif 'ethereum' in text_lower or 'eth' in text_lower:
                return self.api.get_crypto_price('ETH')
            elif 'dogecoin' in text_lower:
                return self.api.get_crypto_price('DOGE')

        # Злато
        if 'злато' in text_lower:
            return self.api.get_gold_price()

        # Памет
        if 'запомни' in text_lower:
            # Опитваме да извлечем ключ и стойност
            parts = text.split('че')
            if len(parts) > 1:
                key_value = parts[1].strip()
                if ':' in key_value:
                    key, value = key_value.split(':', 1)
                    return self.memory.remember(key.strip(), value.strip())
            return "Какво да запомня?"

        if 'припомни' in text_lower or 'спомняш ли си' in text_lower:
            # Опитваме да извлечем ключ
            words = text.split()
            for word in words:
                if word in self.memory.user_memory:
                    return self.memory.recall(word)
            return self.memory.get_all_memory()

        # Вицове
        if 'виц' in text_lower or 'шега' in text_lower:
            return get_joke()

        # Факти
        if 'факт' in text_lower:
            return get_fact()

        # Помощ
        if any(word in text_lower for word in ['помощ', 'какво можеш', 'способности']):
            return ("Мога да: изчислявам, проверявам времето, търся в Wikipedia и Google, "
                   "давам цени на акции и криптовалути, разказвам вицове и факти, "
                   "запомням неща и говоря на български.")

        # WolframAlpha за сложни изчисления
        if self.api.wolfram_app_id:
            result = self.api.calculate_wolfram(text)
            if result:
                return result

        # Общ разговор
        return "Не разбрах командата. Кажете 'помощ' за списък с възможности."

    def run(self):
        """Основен цикъл на асистента"""
        print("🤖 KIKI е готов! Кажете 'kiki' или 'гурко' за да започнете.")
        print("За спиране кажете 'стоп kiki' или натиснете Ctrl+C")

        try:
            while True:
                text = self.speech.listen()
                if text:
                    if 'kiki' in text or 'гурко' in text:
                        if 'стоп' in text:
                            self.speech.speak("Довиждане!")
                            break

                        # Премахваме ключовата дума
                        command = text.replace('kiki', '').replace('гурко', '').strip()
                        if command:
                            response = self.process_command(command)
                            if response:
                                self.speech.speak(response)
                                time.sleep(self.config['settings']['post_response_delay'])
                        else:
                            self.speech.speak("Да, слушам ви!")

        except KeyboardInterrupt:
            print("\n👋 Спиране на KIKI...")
        except Exception as e:
            logger.error(f"Грешка в основния цикъл: {e}")
            print(f"❌ Грешка: {e}")

if __name__ == "__main__":
    kiki = KIKI()
    kiki.run()