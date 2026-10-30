import json
import requests
from typing import Any


MCP_URL = "https://mcp.vkusvill.ru/mcp"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

class VkusvillMCP:
    """Клиент для MCP-сервера ВкусВилл."""

    def __init__(self, url: str = MCP_URL):
        self.url = url
        self._id = 0

    def _call(self, method: str, params: dict) -> dict:
        """Отправить JSON-RPC запрос."""
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self._id,
        }
        response = requests.post(self.url, json=payload, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_tools(self) -> list[dict]:
        """Получить список инструментов."""
        result = self._call("tools/list", {})
        return result.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> Any:
        """Вызвать инструмент."""
        result = self._call("tools/call", {
            "name": name,
            "arguments": arguments,
        })

        # MCP возвращает content как список
        content = result.get("result", {}).get("content", [])
        if not content:
            return None

        # Первый элемент — text с JSON
        text = content[0].get("text", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


    def search_products(
        self,
        query: str,
        page: int = 1,
        mode: str = "full",
        sort: str = "popularity",
    ) -> dict:
        """Поиск товаров."""
        return self.call_tool("vkusvill_products_search", {
            "q": query,
            "page": page,
            "mode": mode,
            "sort": sort,
        })

    def product_details(self, product_id: int) -> dict:
        """Детали товара."""
        return self.call_tool("vkusvill_product_details", {
            "id": product_id,
        })

    def product_by_barcode(self, barcode: str) -> dict:
        """Товар по штрихкоду."""
        return self.call_tool("vkusvill_product_barcode", {
            "barcode": barcode,
        })

    def product_analogs(self, product_id: int) -> dict:
        """Аналоги товара."""
        return self.call_tool("vkusvill_product_analogs", {
            "id": product_id,
        })

    def discount_products(self, page: int = 1) -> dict:
        """Акционные товары."""
        return self.call_tool("vkusvill_products_discount", {
            "page": page,
            "type": "card",
        })

    def shops(self, page: int = 1) -> dict:
        """Магазины."""
        return self.call_tool("vkusvill_shops", {
            "page": page,
        })

    def recipes(self, query: str = "", page: int = 1) -> dict:
        """Рецепты."""
        return self.call_tool("vkusvill_recipes", {
            "q": query,
            "page": page,
            "sort": "popularity",
            "id_feature_filter": 0,
            "id_cooking_time_filter": 0,
            "id_cooking_method_filter": 0,
            "id_complexity_filter": 0,
            "id_category_filter": 0,
            "id_exclude_allergens_filter": [],
        })


if __name__ == "__main__":
    # Тест
    client = VkusvillMCP()

    print("=== Инструменты ===")
    tools = client.list_tools()
    for tool in tools:
        print(f"- {tool['name']}")

    print("\n=== Поиск 'молоко' ===")
    result = client.search_products("молоко", mode="full")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
