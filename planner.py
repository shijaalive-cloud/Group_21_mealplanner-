"""
planner.py
----------
Keeps track of the weekly schedule (which recipes are planned for
which day, and how many servings) and handles saving/loading that
schedule to a local JSON file.
"""

import json
from models import Recipe
from shopping_list import ShoppingListGenerator


class MealPlanner:

    VALID_DAYS = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    ]

    def __init__(self):
        # e.g. {"Monday": [(Recipe, 4), (Recipe, 2)]}
        self.schedule = {}

    def add_meal(self, day, recipe, servings):
        day = day.strip().lower()

        if day not in self.VALID_DAYS:
            raise ValueError(f"'{day}' is not a valid day of the week.")
        if servings <= 0:
            raise ValueError("Servings must be a positive whole number.")

        day = day.capitalize()
        self.schedule.setdefault(day, [])
        self.schedule[day].append((recipe, servings))

    def get_all_meals(self):
        """Flattens the schedule into one list, used by the shopping list generator."""
        all_meals = []
        for meals in self.schedule.values():
            all_meals.extend(meals)
        return all_meals

    def save_to_file(self, file_path):
        shopping_list = ShoppingListGenerator.build_list(self.get_all_meals())

        data = {
            "schedule": {
                day: [{"recipe": r.to_dict(), "servings": s} for r, s in meals]
                for day, meals in self.schedule.items()
            },
            "shopping_list": shopping_list,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, file_path):
        """Rebuilds the schedule from a previously saved JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.schedule = {}
        for day, meals in data.get("schedule", {}).items():
            for item in meals:
                r = item["recipe"]
                recipe = Recipe(
                    r["meal_id"], r["name"], r["category"],
                    r["cuisine"], r["instructions"], r["ingredients"],
                )
                self.schedule.setdefault(day, []).append((recipe, item["servings"]))
