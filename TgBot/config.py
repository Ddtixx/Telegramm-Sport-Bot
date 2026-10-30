import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("API")
DATABASE_URL = os.getenv("DATABASE_URL")

ACTIVITY_MULTIPLIERS = {
    "сверх низкий": 1.2,
    "низкий": 1.375,
    "средний": 1.55,
    "высокий": 1.725,
    "спортивный": 1.9,
}

HARRIS_BENEDICT_COEFFS = {
    "male": {
        "base": 88.362,
        "weight": 13.397,
        "height": 4.799,
        "age": 5.677,
    },
    "female": {
        "base": 447.593,
        "weight": 9.247,
        "height": 3.098,
        "age": 4.330,
    },
}

MIFFLIN_JEOR_COEFFS = {
    "male": {"weight": 10, "height": 6.25, "age": 5, "base": 5},
    "female": {"weight": 10, "height": 6.25, "age": 5, "base": -161},
}

GOAL_ADJUSTMENTS = {
    "Сушка": {"calorie_delta": -0.20, "protein_ratio": 0.35, "fat_ratio": 0.30, "carb_ratio": 0.35},
    "Набор массы": {"calorie_delta": 0.20, "protein_ratio": 0.25, "fat_ratio": 0.30, "carb_ratio": 0.45},
    "Поддержание веса": {"calorie_delta": 0.0, "protein_ratio": 0.20, "fat_ratio": 0.30, "carb_ratio": 0.50},
    "Поддeржание веса": {"calorie_delta": 0.0, "protein_ratio": 0.20, "fat_ratio": 0.30, "carb_ratio": 0.50},
}

PROTEIN_KCAL = 4
FAT_KCAL = 9
CARB_KCAL = 4

CATEGORY_KEYWORDS = {
    "osnova": "индейка",
    "garnir": "хлеб",
    "napitok": "молоко",
}

CATEGORY_MAP = {
    "osnova": [145, 146, 151, 160, 175, 181],
    "garnir": [127, 128, 51751],
    "napitok": [50400],
    "molochnoe": [50390, 59082, 50396],
    "sladosti": [50434, 50428, 50429],
}
