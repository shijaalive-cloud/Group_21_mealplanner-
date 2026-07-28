"""
models.py
---------
Holds the Recipe class: a simple data container ("model") that stores
everything about one meal. No internet calls, no math, no UI code —
just data. This keeps it easy to test and easy to reuse anywhere.
"""


class Recipe:
    """Stores all information about a single meal/recipe."""

    def __init__(self, meal_id, name, category, cuisine, instructions, ingredients):
        self.meal_id = meal_id
        self.name = name
        self.category = category
        self.cuisine = cuisine
        self.instructions = instructions
        # ingredients is a list of (ingredient_name, measure_string) tuples
        # e.g. [("Chicken", "500g"), ("Salt", "1 tsp")]
        self.ingredients = ingredients

    @classmethod
    def from_api_data(cls, data):
        """
        TheMealDB does NOT return a clean ingredients list.
        It returns 20 separate fields: strIngredient1..20, strMeasure1..20.
        This method loops through those 20 fields and builds a normal list.
        """
        ingredients = []
        for i in range(1, 21):
            name = data.get(f"strIngredient{i}")
            measure = data.get(f"strMeasure{i}")
            if name and name.strip():  # skip empty slots
                ingredients.append((name.strip(), (measure or "").strip()))

        return cls(
            meal_id=data.get("idMeal", ""),
            name=data.get("strMeal", "Unknown Meal"),
            category=data.get("strCategory", "Unknown"),
            cuisine=data.get("strArea", "Unknown"),
            instructions=data.get("strInstructions", ""),
            ingredients=ingredients,
        )

    def to_dict(self):
        """Converts this object into a plain dictionary so json.dump() can save it."""
        return self.__dict__
