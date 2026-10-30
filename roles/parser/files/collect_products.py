import os
import re
import time
import psycopg2
from dotenv import load_dotenv
from mcp_client import VkusvillMCP
from pathlib import Path

load_dotenv(os.getenv("ENV_FILE", str(Path(__file__).resolve().parent.parent / ".env")))

DATABASE_URL = os.getenv("DATABASE_URL")


def parse_nutrition(text: str) -> dict:
    """Парсит КБЖУ из строки."""
    result = {"protein": None, "fat": None, "carbs": None, "calories": None}

    if not text:
        return result

    text = text.split("<br>")[0]

    match = re.search(r'белки\s+([\d.,]+)', text, re.IGNORECASE)
    if match:
        result["protein"] = float(match.group(1).replace(",", "."))

    match = re.search(r'жиры\s+([\d.,]+)', text, re.IGNORECASE)
    if match:
        result["fat"] = float(match.group(1).replace(",", "."))

    match = re.search(r'углеводы\s+([\d.,]+)', text, re.IGNORECASE)
    if match:
        result["carbs"] = float(match.group(1).replace(",", "."))

    match = re.search(r'([\d.,]+)\s*ккал', text, re.IGNORECASE)
    if match:
        result["calories"] = float(match.group(1).replace(",", "."))

    return result


def get_retailer_id(cursor) -> int:
    cursor.execute("SELECT id FROM retailers WHERE code = 'vkusvill'")
    return cursor.fetchone()[0]


def save_category(cursor, retailer_id: int, cat: dict) -> int:
    """Сохранить категорию и вернуть её ID."""
    external_id = str(cat.get("id"))
    name = cat.get("name", "")

    cursor.execute("""
        INSERT INTO categories (retailer_id, external_id, name)
        VALUES (%s, %s, %s)
        ON CONFLICT (retailer_id, external_id) 
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id
    """, (retailer_id, external_id, name))

    return cursor.fetchone()[0]


def collect_products(query: str, max_pages: int = 5):
    """Собрать товары по запросу."""
    client = VkusvillMCP()
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    retailer_id = get_retailer_id(cursor)

    total_saved = 0

    for page in range(1, max_pages + 1):
        print(f"Страница {page}...")

        result = client.search_products(query, page=page, mode="full")
        if not result.get("ok"):
            print(f"Ошибка поиска: {result}")
            break

        items = result.get("data", {}).get("items", [])
        if not items:
            break

        for item in items:
            item_id = item["id"]
            name = item["name"].replace("&nbsp;", " ")

            weight_data = item.get("weight") or {}
            weight = weight_data.get("value")

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
                category_id = save_category(cursor, retailer_id, category[0])

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
                weight * 1000 if weight else None,
                unit,
                nutrition["calories"],
                nutrition["protein"],
                nutrition["fat"],
                nutrition["carbs"],
            ))

            total_saved += 1
            print(f"  ✓ {name[:50]} — {nutrition['calories']} ккал")

        conn.commit()
        time.sleep(2)

    cursor.close()
    conn.close()

    print(f"\nВсего сохранено: {total_saved}")


if __name__ == "__main__":
    queries = [
        "молоко", "хлеб", "мясо", "рыба", "овощи",
        "фрукты", "сыр", "яйца", "крупы", "масло",
        "творог", "йогурт", "кефир", "сметана", "колбаса",
        "курица", "говядина", "свинина", "индейка", "фарш",
        "картофель", "морковь", "лук", "помидоры", "огурцы",
    ]
    
    for query in queries:
        print(f"\n=== {query} ===")
        try:
            collect_products(query, max_pages=3)
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(3)
