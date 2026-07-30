import requests
from models import Recipe
class MealDBClient:

    BASE_URL = "https://www.themealdb.com/api/json/v1/1"

    def search_by_name(self, name):
        url = f"{self.BASE_URL}/search.php?s={name}"
        return self._get_recipes(url)

    def search_by_ingredient(self, ingredient):
        url = f"{self.BASE_URL}/filter.php?i={ingredient}"
        return self._get_recipes(url)

    def search_by_category(self, category):
        url = f"{self.BASE_URL}/filter.php?c={category}"
        return self._get_recipes(url)

    def get_full_recipe(self, meal_id):
       
        url = f"{self.BASE_URL}/lookup.php?i={meal_id}"
        recipes = self._get_recipes(url)
        return recipes[0] if recipes else None

    def _get_recipes(self, url):
      
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # raises an error for bad status codes
            data = response.json()
            meals = data.get("meals")

            if not meals:  # TheMealDB returns {"meals": null} when nothing is found
                return []

            return [Recipe.from_api_data(m) for m in meals]

        except requests.exceptions.RequestException as e:
            print(f"[Network/API error] Could not reach TheMealDB: {e}")
            return []