import unittest
from unittest.mock import Mock, patch
from utils import calculate, get_current_time, get_joke, get_fact
from memory import MemoryHandler
from api import APIHandler
import json
import os
import tempfile

class TestUtils(unittest.TestCase):
    def test_calculate_simple(self):
        self.assertEqual(calculate("2 + 2"), "4")
        self.assertEqual(calculate("10 * 5"), "50")

    def test_calculate_float(self):
        self.assertEqual(calculate("5 / 2"), "2.50")

    def test_calculate_invalid(self):
        self.assertIsNone(calculate("invalid"))
        self.assertIsNone(calculate("2 + import os"))

    def test_get_current_time(self):
        time_str = get_current_time()
        self.assertIn("Днес е", time_str)
        self.assertIn("часа", time_str)

    def test_get_joke(self):
        joke = get_joke()
        self.assertIsInstance(joke, str)
        self.assertGreater(len(joke), 0)

    def test_get_fact(self):
        fact = get_fact()
        self.assertIsInstance(fact, str)
        self.assertGreater(len(fact), 0)

class TestMemoryHandler(unittest.TestCase):
    def setUp(self):
        self.config = {
            'files': {'memory_file': 'test_memory.json'}
        }
        self.memory = MemoryHandler(self.config)

    def tearDown(self):
        if os.path.exists('test_memory.json'):
            os.remove('test_memory.json')

    def test_remember_and_recall(self):
        result = self.memory.remember("name", "John")
        self.assertIn("Запомних", result)
        recall = self.memory.recall("name")
        self.assertEqual(recall, "name: John")

    def test_recall_nonexistent(self):
        recall = self.memory.recall("nonexistent")
        self.assertIn("Не си спомням", recall)

class TestAPIHandler(unittest.TestCase):
    def setUp(self):
        self.config = {
            'api_keys': {'weather': '', 'wolfram': ''}
        }
        self.api = APIHandler(self.config)

    @patch('requests.get')
    def test_search_google_timeout(self, mock_get):
        mock_get.side_effect = Exception("Timeout")
        result = self.api.search_google("test query")
        self.assertIsNone(result)

    def test_search_wikipedia_invalid(self):
        result = self.api.search_wikipedia("")
        self.assertIsNone(result)

    def test_get_weather_no_key(self):
        result = self.api.get_weather("Sofia")
        self.assertIn("Няма API ключ", result)

if __name__ == '__main__':
    unittest.main()