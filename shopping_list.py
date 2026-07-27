"""
shopping_list.py
----------------
Turns messy ingredient "measure" strings like "1 1/2 cups" into a
(quantity, unit) pair using regular expressions, then adds them all
up (scaled by servings) across every recipe in the weekly plan.
"""

import re


class ShoppingListGenerator:

    # Matches: whole numbers, decimals, fractions, and mixed fractions
    # Examples matched: "500", "1.5", "3/4", "1 1/2"
    QUANTITY_PATTERN = r"^(\d+\s+\d+/\d+|\d+/\d+|\d*\.\d+|\d+)"

    @classmethod
    def parse_measure(cls, measure_str):
        """Splits a measure string into a (quantity, unit) pair.

        Examples:
            "500g"       -> (500.0, "g")
            "1 1/2 cups" -> (1.5,   "cups")
            "a pinch"    -> (1.0,   "a pinch")   # no number found -> default 1
        """
        if not measure_str or not measure_str.strip():
            return 1.0, "unit"

        measure_str = measure_str.strip().lower()
        match = re.match(cls.QUANTITY_PATTERN, measure_str)

        if not match:
            # No number at the start (e.g. "to taste") -> treat as 1 of that unit
            return 1.0, measure_str

        number_text = match.group(1)
        unit = measure_str[match.end():].strip() or "unit"

        try:
            if " " in number_text:            # mixed fraction "1 1/2"
                whole, frac = number_text.split()
                num, den = frac.split("/")
                quantity = float(whole) + float(num) / float(den)
            elif "/" in number_text:          # plain fraction "3/4"
                num, den = number_text.split("/")
                quantity = float(num) / float(den)
            else:                             # normal number "500"
                quantity = float(number_text)
        except (ValueError, ZeroDivisionError):
            quantity = 1.0

        return quantity, unit

    @classmethod
    def build_list(cls, planned_meals):
        """planned_meals is a list of (Recipe, servings) tuples.
        Returns: {"Chicken": {"g": 1000.0}, "Salt": {"tsp": 3.0}, ...}
        """
        shopping_list = {}

        for recipe, servings in planned_meals:
            for ing_name, measure_str in recipe.ingredients:
                clean_name = ing_name.strip().title()
                quantity, unit = cls.parse_measure(measure_str)
                scaled_quantity = quantity * servings

                shopping_list.setdefault(clean_name, {})
                shopping_list[clean_name][unit] = (
                    shopping_list[clean_name].get(unit, 0) + scaled_quantity
                )

        return shopping_list
