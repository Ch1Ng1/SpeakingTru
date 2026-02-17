import ast
import operator
import re
import random
from datetime import datetime

def calculate(expression):
    """Изчислява математически изрази по безопасен начин"""
    # Валидираме израза
    if not expression or not re.match(r'^[\d\s\+\-\*/\(\)\.\^]*$', expression):
        return None

    # Заменяме ^ с ** за степенуване
    expression = expression.replace('^', '**')

    try:
        # Безопасно изчисление с ограничени операции
        allowed_names = {
            k: v for k, v in operator.__dict__.items() if not k.startswith('_')
        }
        allowed_names.update({
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
        })

        # Парсваме и оценяваме израза
        node = ast.parse(expression, mode='eval')

        # Проверяваме дали всички имена са позволени
        for node_item in ast.walk(node):
            if isinstance(node_item, ast.Name) and node_item.id not in allowed_names:
                return None
            elif isinstance(node_item, ast.Call) and node_item.func.id not in allowed_names:
                return None

        result = eval(compile(node, '<string>', 'eval'), {"__builtins__": {}}, allowed_names)

        # Форматираме резултата
        if isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            return f"{result:.2f}"
        return str(result)
    except Exception as e:
        return None

def get_current_time():
    """Връща текущата дата и час"""
    now = datetime.now()
    return now.strftime("Днес е %d.%m.%Y, %H:%M часа")

def get_joke():
    """Връща случаен виц"""
    jokes = [
        "Защо компютърът отиде на лекар? Защото имаше вирус!",
        "Какво прави програмистът когато е тъжен? Пише код!",
        "Защо Python е като змия? Защото е обектно-ориентиран!",
        "Какво е общото между програмиста и рибата? И двамата плуват в код!",
        "Защо програмистите работят нощем? Защото денем има твърде много светлина!"
    ]
    return random.choice(jokes)

def get_fact():
    """Връща случаен интересен факт"""
    facts = [
        "Океанът произвежда около 70% от кислорода на Земята.",
        "Сърцето на синия кит е толкова голямо, че човек може да плува в него.",
        "Медузите нямат мозък, сърце или кръв.",
        "Светкавицата е по-гореща от повърхността на Слънцето.",
        "Човешкият мозък използва около 20% от енергията на тялото."
    ]
    return random.choice(facts)