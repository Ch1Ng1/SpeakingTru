import json
import os
import logging

logger = logging.getLogger(__name__)

class MemoryHandler:
    def __init__(self, config):
        self.config = config
        self.memory_file = config['files']['memory_file']
        self.user_memory = {}
        self.load_memory()

    def load_memory(self):
        """Зарежда памет от файл"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.user_memory = json.load(f)
                    logger.info("Памет заредена успешно")
        except Exception as e:
            logger.error(f"Грешка при зареждане на памет: {e}")
            self.user_memory = {}

    def save_memory(self):
        """Запазва памет във файл"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_memory, f, ensure_ascii=False, indent=2)
                logger.info("Памет запазена успешно")
        except Exception as e:
            logger.error(f"Грешка при запазване на памет: {e}")

    def remember(self, key, value):
        """Запомня нещо"""
        self.user_memory[key] = value
        self.save_memory()
        return f"Запомних {key}: {value}"

    def recall(self, key):
        """Припомня нещо"""
        if key in self.user_memory:
            return f"{key}: {self.user_memory[key]}"
        return f"Не си спомням {key}"

    def get_all_memory(self):
        """Връща цялата памет"""
        if self.user_memory:
            return "\n".join([f"{k}: {v}" for k, v in self.user_memory.items()])
        return "Няма запомнени неща"