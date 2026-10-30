import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():

    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def get_random_product_by_category(category_keyword: str, max_calories: float = None):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT p.id, p.name, p.calories_per_100g, p.protein_per_100g,
               p.fat_per_100g, p.carbs_per_100g, p.weight_g, p.unit,
               c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE LOWER(p.name) LIKE LOWER(%s)
    """
    params = [f'%{category_keyword}%']

    if max_calories:
        query += " AND p.calories_per_100g <= %s"
        params.append(max_calories)

    query += " ORDER BY RANDOM() LIMIT 1"

    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def get_random_product(category_ids: list = None):

    conn = get_connection()
    cursor = conn.cursor()

    if category_ids:
        cursor.execute("""
            SELECT id, name, calories_per_100g, protein_per_100g,
                   fat_per_100g, carbs_per_100g, weight_g, unit
            FROM products
            WHERE category_id = ANY(%s)
              AND calories_per_100g IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 1
        """, (category_ids,))
    else:
        cursor.execute("""
            SELECT id, name, calories_per_100g, protein_per_100g,
                   fat_per_100g, carbs_per_100g, weight_g, unit
            FROM products
            WHERE calories_per_100g IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 1
        """)

    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def get_products_by_category(category_ids: list, limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, calories_per_100g, protein_per_100g,
               fat_per_100g, carbs_per_100g, weight_g, unit
        FROM products
        WHERE category_id = ANY(%s)
          AND calories_per_100g IS NOT NULL
        ORDER BY RANDOM()
        LIMIT %s
    """, (category_ids, limit))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
