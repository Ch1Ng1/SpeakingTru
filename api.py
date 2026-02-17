import requests
from bs4 import BeautifulSoup
import wikipedia
import wolframalpha
import yfinance as yf
import json
import logging

logger = logging.getLogger(__name__)

class APIHandler:
    def __init__(self, config):
        self.config = config
        self.weather_api_key = config['api_keys']['weather']
        self.wolfram_app_id = config['api_keys']['wolfram']
        wikipedia.set_lang("bg")

    def search_google(self, query):
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

    def search_wikipedia(self, query):
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

    def get_weather(self, city="Sofia"):
        """Получава времето за град"""
        if not self.weather_api_key:
            return "Няма API ключ за време. Добавете го в config.json"

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric&lang=bg"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"Времето в {city}: {temp}°C, {description}"
        except Exception as e:
            logger.error(f"Грешка при получаване на време: {e}")
            return "Не можах да получа информация за времето"

    def get_stock_price(self, symbol):
        """Получава цена на акция"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            price = info.get('currentPrice', info.get('regularMarketPrice'))
            if price:
                return f"Цената на {symbol.upper()} е ${price:.2f}"
            return f"Не можах да намеря цена за {symbol}"
        except Exception as e:
            logger.error(f"Грешка при получаване на акция: {e}")
            return "Грешка при получаване на цената"

    def get_crypto_price(self, crypto):
        """Получава цена на криптовалута"""
        try:
            crypto = crypto.upper()
            if crypto == "BTC":
                symbol = "BTC-USD"
            elif crypto == "ETH":
                symbol = "ETH-USD"
            else:
                symbol = f"{crypto}-USD"

            stock = yf.Ticker(symbol)
            info = stock.info
            price = info.get('currentPrice', info.get('regularMarketPrice'))
            if price:
                return f"Цената на {crypto} е ${price:.2f}"
            return f"Не можах да намеря цена за {crypto}"
        except Exception as e:
            logger.error(f"Грешка при получаване на крипто: {e}")
            return "Грешка при получаване на цената"

    def get_gold_price(self):
        """Получава цена на злато"""
        try:
            gold = yf.Ticker("GC=F")
            info = gold.info
            price = info.get('currentPrice', info.get('regularMarketPrice'))
            if price:
                return f"Цената на златото е ${price:.2f} на унция"
            return "Не можах да намеря цена на злато"
        except Exception as e:
            logger.error(f"Грешка при получаване на злато: {e}")
            return "Грешка при получаване на цената"

    def calculate_wolfram(self, query):
        """Изчислява с WolframAlpha"""
        if not self.wolfram_app_id:
            return None

        try:
            client = wolframalpha.Client(self.wolfram_app_id)
            res = client.query(query)
            answer = next(res.results).text
            return answer
        except Exception as e:
            logger.error(f"WolframAlpha грешка: {e}")
            return None