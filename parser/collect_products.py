import logging
import os
import re
import time
import psycopg2
from dotenv import load_dotenv
from mcp_client import VkusvillMCP
from pathlib import Path

load_dotenv(os.getenv("ENV_FILE", str(Path(__file__).resolve().parent.parent / ".env")))

DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_nutrition(text: str) -> dict:
    """Парсит КБЖУ из строки свойств товара."""
    result = {"protein": None, "fat": None, "carbs": None, "calories": None}

    if not text:
        return result

    text = text.split("<br>")[0]

    patterns = {
        "protein": r'белки\s+([\d.,]+)',
        "fat": r'жиры\s+([\d.,]+)',
        "carbs": r'углеводы\s+([\d.,]+)',
        "calories": r'([\d.,]+)\s*ккал',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result[key] = float(match.group(1).replace(",", "."))
            except ValueError:
                logger.warning("Не удалось преобразовать %s: %s", key, match.group(1))

    return result


def get_retailer_id(cursor) -> int:
    cursor.execute("SELECT id FROM retailers WHERE code = 'vkusvill'")
    row = cursor.fetchone()
    if not row:
        raise RuntimeError("Ритейлер 'vkusvill' не найден в базе. Выполните schema.sql.")
    return row[0]


def save_category(cursor, retailer_id: int, cat: dict) -> int:
    """Сохранить категорию и вернуть её ID."""
    external_id = str(cat.get("id", ""))
    name = cat.get("name", "")

    if not external_id:
        return None

    cursor.execute("""
        INSERT INTO categories (retailer_id, external_id, name)
        VALUES (%s, %s, %s)
        ON CONFLICT (retailer_id, external_id)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id
    """, (retailer_id, external_id, name))

    return cursor.fetchone()[0]


def normalize_weight(weight_data: dict) -> float | None:
    """Извлекает вес в граммах из данных товара."""
    if not weight_data:
        return None

    value = weight_data.get("value")
    if value is None:
        return None

    unit = (weight_data.get("unit") or "").lower()
    if unit in ("kg", "кг"):
        return float(value) * 1000
    if unit in ("g", "г", "гр"):
        return float(value)
    if unit in ("ml", "мл", "l", "л"):
        return float(value) if unit in ("ml", "мл") else float(value) * 1000

    return float(value) * 1000 if value < 100 else float(value)


def collect_products(query: str, max_pages: int = 5):
    """Собрать товары по запросу."""
    client = VkusvillMCP()
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    retailer_id = get_retailer_id(cursor)

    total_saved = 0
    total_skipped = 0

    for page in range(1, max_pages + 1):
        logger.info("Запрос '%s', страница %d/%d", query, page, max_pages)

        try:
            result = client.search_products(query, page=page, mode="full")
        except Exception as e:
            logger.error("Ошибка поиска на странице %d: %s", page, e)
            break

        if not result or not result.get("ok"):
            logger.warning("Поиск вернул ошибку: %s", result)
            break

        items = result.get("data", {}).get("items", [])
        if not items:
            logger.info("Товары закончились на странице %d", page)
            break

        for item in items:
            item_id = item.get("id")
            if not item_id:
                total_skipped += 1
                continue

            name = item.get("name", "").replace("&nbsp;", " ").strip()
            if not name:
                total_skipped += 1
                continue

            weight_data = item.get("weight") or {}
            weight = normalize_weight(weight_data)

            unit = item.get("unit") or "шт"
            category = item.get("category") or []
            properties = item.get("properties") or []

            nutrition = {"protein": None, "fat": None, "carbs": None, "calories": None}
            for prop in properties:
                if "Пищевая" in prop.get("name", ""):
                    nutrition = parse_nutrition(prop.get("value", ""))
                    break

            category_id = None
            if category:
                try:
                    category_id = save_category(cursor, retailer_id, category[0])
                except Exception as e:
                    logger.warning("Не удалось сохранить категорию: %s", e)

            try:
                cursor.execute("""
                    INSERT INTO products (
                        retailer_id, external_id, name, brand, category_id,
                        weight_g, unit,
                        calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (retailer_id, external_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        category_id = EXCLUDED.category_id,
                        weight_g = EXCLUDED.weight_g,
                        calories_per_100g = EXCLUDED.calories_per_100g,
                        protein_per_100g = EXCLUDED.protein_per_100g,
                        fat_per_100g = EXCLUDED.fat_per_100g,
                        carbs_per_100g = EXCLUDED.carbs_per_100g,
                        updated_at = now()
                """, (
                    retailer_id,
                    str(item_id),
                    name,
                    None,
                    category_id,
                    weight,
                    unit,
                    nutrition["calories"],
                    nutrition["protein"],
                    nutrition["fat"],
                    nutrition["carbs"],
                ))
                total_saved += 1
                logger.info("  + %s — %s ккал", name[:50], nutrition.get("calories"))
            except Exception as e:
                total_skipped += 1
                logger.error("  x %s — %s", name[:50], e)

        conn.commit()
        time.sleep(2)

    cursor.close()
    conn.close()

    logger.info("Запрос '%s' завершён: сохранено %d, пропущено %d", query, total_saved, total_skipped)


if __name__ == "__main__":
    queries = [
        "молоко", "хлеб", "мясо", "рыба", "овощи",
        "фрукты", "сыр", "яйца", "крупы", "масло",
        "творог", "йогурт", "кефир", "сметана", "колбаса",
        "курица", "говядина", "свинина", "индейка", "фарш",
        "картофель", "морковь", "лук", "помидоры", "огурцы",
    ]

    for query in queries:
        logger.info("=== %s ===", query)
        try:
            collect_products(query, max_pages=3)
        except Exception as e:
            logger.error("Критическая ошибка для '%s': %s", query, e)
        time.sleep(3)
