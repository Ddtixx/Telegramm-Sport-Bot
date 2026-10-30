import random
from db import get_products_by_category


CATEGORY_MAP = {
    "osnova": [145, 146, 151, 160, 175, 181],   # Курица, говядина, индейка, свинина, рыба
    "garnir": [127, 128, 51751],                 # Хлеб, крупы
    "napitok": [50400],                          # Растительное молоко
    "molochnoe": [50390, 59082, 50396],         # Молоко
    "sladosti": [50434, 50428, 50429],          # Конфеты, торты, пирожные
}


def pick_products_for_basket(budget: float, items: dict) -> dict:
    """
    Подбирает продукты под бюджет.
    
    :param budget: дневной бюджет (руб)
    :param items: dict с выбранными позициями
    :return: dict с продуктами
    """
    result = {
        "products": [],
        "total_calories": 0,
        "total_protein": 0,
        "total_fat": 0,
        "total_carbs": 0,
        "total_price": 0,
    }

    PRICE_PER_100G = 20

    for key, product in items.items():
        if not product:
            continue

        weight = product.get("weight_g") or 100
        price = (weight / 100) * PRICE_PER_100G

        result["products"].append({
            "name": product["name"],
            "weight": weight,
            "calories": product.get("calories_per_100g") or 0,
            "protein": product.get("protein_per_100g") or 0,
            "fat": product.get("fat_per_100g") or 0,
            "carbs": product.get("carbs_per_100g") or 0,
            "price": price,
        })

        result["total_calories"] += product.get("calories_per_100g") or 0
        result["total_protein"] += product.get("protein_per_100g") or 0
        result["total_fat"] += product.get("fat_per_100g") or 0
        result["total_carbs"] += product.get("carbs_per_100g") or 0
        result["total_price"] += price

    return result


def format_basket(basket_data: dict) -> str:

    products = basket_data["products"]

    if not products:
        return "Корзина пуста."

    text = "🛒 <b>Ваша корзина:</b>\n\n"

    for i, item in enumerate(products, 1):
        text += f"{i}. <b>{item['name']}</b>\n"
        text += f"   {item['weight']:.0f}г · {item['calories']:.0f} ккал/100г · {item['price']:.0f}₽\n\n"

    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += f"🔥 Калории: <b>{basket_data['total_calories']:.0f}</b> ккал\n"
    text += f"🥩 Белки: <b>{basket_data['total_protein']:.1f}</b> г\n"
    text += f"🧈 Жиры: <b>{basket_data['total_fat']:.1f}</b> г\n"
    text += f"🍞 Углеводы: <b>{basket_data['total_carbs']:.1f}</b> г\n"
    text += f"💰 Цена: <b>{basket_data['total_price']:.0f}</b> ₽\n"

    return text
